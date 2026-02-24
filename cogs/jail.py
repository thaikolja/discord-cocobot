#  Copyright (C) 2025 by Kolja Nolte
#  kolja.nolte@gmail.com
#  https://gitlab.com/thailand-discord/bots/cocobot
#
#  This work is licensed under the MIT License. You are free to use, copy, modify,
#  merge, publish, distribute, sublicense, and/or sell copies of the Software,
#  and to permit persons to whom the Software is furnished to do so, subject to the
#  condition that the above copyright notice and this permission notice shall be
#  included in all
#  copies or substantial portions of the Software.
#
#  For more information, visit: https://opensource.org/licenses/MIT
#
#  Author:    Kolja Nolte
#  Email:     kolja.nolte@gmail.com
#  License:   MIT
#  Date:      2014-2025
#  Package:   cocobot Discord Bot

"""
AI Jail commands for CocoBot.

This module provides slash commands for jailing and unjailing Discord members.
Jailed users have their roles stripped and replaced with a "Jailed" role, while
August Engelhardt harasses them in #ai-jail until they leave or are unjailed.
"""

import json
import logging
import os

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from utils.database import JailedUser, get_db_session, init_db

# Grab the shared discord logger so we stay consistent
logger = logging.getLogger('discord')


class JailCog(commands.Cog):
    """
    Administrative commands for the AI Jail feature.

    Provides /jail and /unjail slash commands (admin-only) and an
    on_member_remove listener for automatic cleanup when jailed users leave.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Load configuration from environment
        self.jail_role_id = int(os.getenv('JAIL_ROLE_ID', '0'))
        self.august_port = os.getenv('AUGUST_INTERNAL_PORT', '17432')
        self.august_secret = os.getenv('AUGUST_INTERNAL_SECRET', '')
        self.august_base_url = f'http://127.0.0.1:{self.august_port}'

    async def _call_august(self, endpoint: str, payload: dict) -> bool:
        """
        Send a POST request to August's internal API.

        Args:
            endpoint: The API endpoint path (e.g. '/start-jail').
            payload: The JSON body to send.

        Returns:
            True if the request succeeded (2xx), False otherwise.
        """
        url = f'{self.august_base_url}{endpoint}'
        headers = {
            'Content-Type': 'application/json',
            'X-Internal-Token': self.august_secret,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status < 300:
                        return True
                    logger.warning(
                        f'August API {endpoint} returned status {resp.status}'
                    )
                    return False
        except aiohttp.ClientError as e:
            logger.error(f'Failed to reach August API at {url}: {e}')
            return False

    @app_commands.command(
        name='jail',
        description='Jail a member — strips roles, assigns Jailed role, and unleashes August.',
    )
    @app_commands.describe(
        user='The member to jail',
        reason='Optional reason for jailing',
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def jail_command(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: str = None,
    ):
        """Jail a Discord member."""
        # Ensure the database is ready
        init_db()

        # Check if user is already jailed
        with next(get_db_session()) as db:
            existing = db.query(JailedUser).filter(
                JailedUser.user_id == str(user.id)
            ).first()
            if existing:
                await interaction.response.send_message(
                    f'⚠️ {user.mention} is already in jail.', ephemeral=True
                )
                return

        # Snapshot current roles (excluding @everyone)
        role_ids = [str(role.id) for role in user.roles if role != interaction.guild.default_role]
        roles_snapshot = json.dumps(role_ids)

        # Strip all roles (except @everyone)
        try:
            await user.remove_roles(
                *[role for role in user.roles if role != interaction.guild.default_role],
                reason=f'AI Jail: {reason or "No reason provided"}',
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                '❌ I do not have permission to remove roles from this user.',
                ephemeral=True,
            )
            return

        # Assign the Jailed role
        jail_role = interaction.guild.get_role(self.jail_role_id)
        if jail_role is None:
            await interaction.response.send_message(
                '❌ Jailed role not found. Check `JAIL_ROLE_ID` in `.env`.',
                ephemeral=True,
            )
            return

        try:
            await user.add_roles(jail_role, reason=f'AI Jail: {reason or "No reason provided"}')
        except discord.Forbidden:
            await interaction.response.send_message(
                '❌ I do not have permission to assign the Jailed role.',
                ephemeral=True,
            )
            return

        # Write record to database
        with next(get_db_session()) as db:
            record = JailedUser(
                user_id=str(user.id),
                username=user.display_name,
                jailed_by=str(interaction.user.id),
                reason=reason,
                roles_snapshot=roles_snapshot,
            )
            db.add(record)
            db.commit()

        # Notify August to start the harassment loop
        await self._call_august('/start-jail', {
            'user_id': str(user.id),
            'username': user.display_name,
        })

        # Respond to the admin
        await interaction.response.send_message(
            f'🔒 {user.mention} has been jailed.', ephemeral=True
        )

        # Attempt to DM the jailed user
        try:
            await user.send(
                '🔒 You have been jailed. You will remain in #ai-jail until an '
                'administrator decides to release you — or until you leave the server.'
            )
        except (discord.Forbidden, discord.HTTPException):
            # User has DMs disabled or something went wrong — not critical
            pass

    @app_commands.command(
        name='unjail',
        description='Unjail a member — restores their roles and stops August.',
    )
    @app_commands.describe(user='The member to unjail')
    @app_commands.checks.has_permissions(administrator=True)
    async def unjail_command(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
    ):
        """Unjail a Discord member and restore their roles."""
        init_db()

        # Look up the jail record
        with next(get_db_session()) as db:
            record = db.query(JailedUser).filter(
                JailedUser.user_id == str(user.id)
            ).first()

            if not record:
                await interaction.response.send_message(
                    f'⚠️ {user.mention} is not currently jailed.', ephemeral=True
                )
                return

            # Grab snapshot before we close the session
            roles_snapshot = json.loads(record.roles_snapshot)
            db.delete(record)
            db.commit()

        # Tell August to stop the harassment loop
        await self._call_august('/stop-jail', {'user_id': str(user.id)})

        # Remove the Jailed role
        jail_role = interaction.guild.get_role(self.jail_role_id)
        if jail_role and jail_role in user.roles:
            try:
                await user.remove_roles(jail_role, reason='AI Jail: Unjailed')
            except discord.Forbidden:
                logger.warning(f'Could not remove Jailed role from {user}')

        # Restore snapshotted roles
        roles_to_restore = []
        for role_id_str in roles_snapshot:
            role = interaction.guild.get_role(int(role_id_str))
            if role and role != interaction.guild.default_role:
                roles_to_restore.append(role)

        if roles_to_restore:
            try:
                await user.add_roles(*roles_to_restore, reason='AI Jail: Roles restored on unjail')
            except discord.Forbidden:
                logger.warning(f'Could not restore some roles for {user}')

        await interaction.response.send_message(
            f'🔓 {user.mention} has been unjailed and their roles have been restored.',
            ephemeral=True,
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Clean up jail records when a jailed member leaves the server."""
        init_db()

        with next(get_db_session()) as db:
            record = db.query(JailedUser).filter(
                JailedUser.user_id == str(member.id)
            ).first()

            if not record:
                return

            db.delete(record)
            db.commit()

        # Tell August to stop the harassment loop
        await self._call_august('/stop-jail', {'user_id': str(member.id)})


async def setup(bot: commands.Bot):
    await bot.add_cog(JailCog(bot))
