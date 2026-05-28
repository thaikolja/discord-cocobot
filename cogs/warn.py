#  Copyright (C) 2026 by Kolja Nolte
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
#  Date:      2024-2026
#  Package:   cocobot Discord Bot


"""Moderator warning system for Cocobot."""

import logging
import os

import discord
from discord import app_commands
from discord.ext import commands

from utils.database import DatabaseManager, get_db_session, init_db
from utils.security import InputSanitizer, escape_markdown

logger = logging.getLogger(__name__)


class WarnCog(commands.Cog):
    """Slash command for warning members and kicking them on the third warning."""

    MAX_WARNINGS = 3
    DEFAULT_REASON = 'Probably not read the #rules ¯\\_(ツ)_/¯'
    FOOTER_TEXT = '© Coconut wisdom since 1875'

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.warned_role_id = int(os.getenv('WARNED_ROLE_ID', '0'))

    @staticmethod
    def _is_moderator(member: discord.Member) -> bool:
        """Return whether the member has moderator-or-higher privileges."""
        permissions = member.guild_permissions
        return any(
            (
                permissions.administrator,
                permissions.moderate_members,
                permissions.kick_members,
                permissions.ban_members,
                permissions.manage_messages,
            )
        )

    def _validate_target(
        self,
        interaction: discord.Interaction,
        moderator: discord.Member,
        target: discord.Member,
    ) -> str | None:
        """Validate moderator and bot hierarchy for the warning target."""
        if target.bot:
            return '❌ Bots cannot be warned.'

        if target.id == moderator.id:
            return '❌ You cannot warn yourself.'

        if interaction.guild is None:
            return '❌ This command can only be used in a server.'

        if target.id == interaction.guild.owner_id:
            return '❌ The server owner cannot be warned.'

        if self._is_moderator(target):
            return '❌ Moderators and above cannot be warned.'

        moderator_role_position = getattr(moderator.top_role, 'position', 0)
        target_role_position = getattr(target.top_role, 'position', 0)

        if (
            moderator.id != interaction.guild.owner_id
            and target_role_position >= moderator_role_position
        ):
            return '❌ You can only warn members below your highest role.'

        bot_member = interaction.guild.me or interaction.guild.get_member(self.bot.user.id)
        if bot_member is None:
            return '❌ I could not verify my server permissions.'

        if not bot_member.guild_permissions.kick_members:
            return '❌ I need the **Kick Members** permission for the warning system.'

        bot_role_position = getattr(bot_member.top_role, 'position', 0)
        if target_role_position >= bot_role_position:
            return '❌ I cannot moderate or kick that member because their top role is too high.'

        return None

    @staticmethod
    def _format_ordinal(number: int) -> str:
        """Return a human-friendly ordinal string."""
        if 10 <= number % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(number % 10, 'th')
        return f'{number}{suffix}'

    @staticmethod
    def _get_warned_role(guild: discord.Guild, role_id: int) -> discord.Role | None:
        """Return the configured warned role, if available."""
        if role_id <= 0:
            return None
        return guild.get_role(role_id)

    @staticmethod
    def _can_manage_role(
        guild: discord.Guild,
        bot_member: discord.Member,
        role: discord.Role | None,
    ) -> bool:
        """Check whether the bot can assign or remove the configured role."""
        if role is None or role == guild.default_role:
            return False
        return getattr(bot_member.top_role, 'position', 0) > getattr(role, 'position', 0)

    async def _sync_warned_role(
        self,
        guild: discord.Guild,
        member: discord.Member,
        should_have_role: bool,
    ) -> str | None:
        """Assign or remove the warned role and return a user-facing note on failure."""
        bot_member = guild.me or guild.get_member(self.bot.user.id)
        if bot_member is None:
            logger.warning('Could not resolve bot member for warned role management.')
            return '⚠️ Warning recorded, but I could not verify my role permissions.'

        warned_role = self._get_warned_role(guild, self.warned_role_id)
        if warned_role is None:
            logger.warning('WARNED_ROLE_ID is not configured or the warned role is missing.')
            return '⚠️ Warning recorded, but the configured warned role was not found.'

        if not self._can_manage_role(guild, bot_member, warned_role):
            logger.warning('Warned role %s is above the bot role hierarchy.', warned_role.id)
            return '⚠️ Warning recorded, but I could not manage the configured warned role.'

        try:
            if should_have_role and warned_role not in member.roles:
                await member.add_roles(warned_role, reason='Warning system: warned role assigned')
            elif not should_have_role and warned_role in member.roles:
                await member.remove_roles(
                    warned_role,
                    reason='Warning system: warned role removed',
                )
        except discord.Forbidden:
            logger.warning('Missing permissions while managing warned role for %s.', member)
            return '⚠️ Warning recorded, but I do not have permission to manage the warned role.'
        except discord.HTTPException as exc:
            logger.error('Discord rejected warned role update for %s: %s', member, exc)
            return '⚠️ Warning recorded, but Discord rejected the warned role update.'

        return None

    @staticmethod
    def _build_warning_embed(
        member: discord.Member,
        moderator: discord.Member,
        reason: str,
        warning_number: int,
        kicked: bool,
    ) -> discord.Embed:
        """Build a warning card embed for the channel and optional DM."""
        if kicked:
            title = '🛑 Warning limit reached'
            color = discord.Color.red()
        elif warning_number == 2:
            title = '⚠️ Final warning'
            color = discord.Color.orange()
        else:
            title = '⚠️ Warning issued'
            color = discord.Color.gold()

        ordinal = WarnCog._format_ordinal(warning_number)
        summary = (
            "You've just been warned by a coconut. Isn't that embarrassing? "
            f'Anyway, **this is your {ordinal} warning**. Warning #3 results '
            'in a kick off this server. You can still join again.'
        )

        embed = discord.Embed(
            title=title,
            description=summary,
            color=color,
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name='Member', value=member.mention, inline=True)
        embed.add_field(name='Moderator', value=moderator.mention, inline=True)
        embed.add_field(name='Reason', value=reason, inline=False)
        embed.set_footer(text=WarnCog.FOOTER_TEXT)

        if member.display_avatar:
            embed.set_thumbnail(url=member.display_avatar.url)

        return embed

    @staticmethod
    async def _try_notify_member(member: discord.Member, embed: discord.Embed) -> None:
        """Attempt to DM the warned member without failing the command."""
        try:
            await member.send(embed=embed)
        except (discord.Forbidden, discord.HTTPException):
            logger.info('Could not DM warning card to %s', member)

    @app_commands.command(
        name='warn',
        description='Warn a member. The third warning automatically kicks them.',
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(moderate_members=True)
    @app_commands.describe(
        user='The member to warn',
        reason='Reason for the warning (optional)',
    )
    async def warn_command(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: str | None = None,
    ):
        """Warn a member and kick them automatically on the third warning."""
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message(
                '❌ This command can only be used by moderators inside a server.',
                ephemeral=True,
            )
            return

        if not self._is_moderator(interaction.user):
            await interaction.response.send_message(
                '❌ Only moderators and above can use `/warn`.',
                ephemeral=True,
            )
            return

        validation_error = self._validate_target(interaction, interaction.user, user)
        if validation_error:
            await interaction.response.send_message(validation_error, ephemeral=True)
            return

        init_db()
        sanitized_reason = InputSanitizer.sanitize_text(
            reason or self.DEFAULT_REASON,
            max_length=500,
        )
        display_reason = escape_markdown(sanitized_reason)
        guild_id = str(interaction.guild.id)
        user_id = str(user.id)

        await interaction.response.defer()

        with get_db_session() as db:
            active_warnings = DatabaseManager.get_active_warnings(db, guild_id, user_id)
            warning_count = len(active_warnings)

            if warning_count >= self.MAX_WARNINGS:
                warning_number = self.MAX_WARNINGS
            else:
                warning_entry = DatabaseManager.create_warning_entry(
                    db=db,
                    guild_id=guild_id,
                    user_id=user_id,
                    username=user.display_name,
                    moderator_id=str(interaction.user.id),
                    moderator_name=interaction.user.display_name,
                    reason=sanitized_reason or None,
                )
                warning_number = warning_entry.warning_number

        should_kick = warning_number >= self.MAX_WARNINGS
        embed = self._build_warning_embed(
            member=user,
            moderator=interaction.user,
            reason=display_reason,
            warning_number=warning_number,
            kicked=should_kick,
        )

        await self._try_notify_member(user, embed)

        role_note = await self._sync_warned_role(
            guild=interaction.guild,
            member=user,
            should_have_role=not should_kick,
        )

        if should_kick:
            try:
                await user.kick(reason='User has been warned too many times.')
            except discord.Forbidden:
                await interaction.followup.send(
                    '❌ I could not kick that member. Please check my role position and permissions.',
                    ephemeral=True,
                )
                return
            except discord.HTTPException as exc:
                logger.error('Failed to kick warned member %s: %s', user, exc)
                await interaction.followup.send(
                    '❌ Discord rejected the kick request. Please try again.',
                    ephemeral=True,
                )
                return

            with get_db_session() as db:
                DatabaseManager.clear_active_warnings(db, guild_id, user_id)

        followup_message = role_note or None
        await interaction.followup.send(content=followup_message, embed=embed)

    @app_commands.command(
        name='resetwarnings',
        description='Reset a member’s active warning count.',
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(moderate_members=True)
    @app_commands.describe(user='The member whose warnings should be reset')
    async def resetwarnings_command(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
    ):
        """Reset the active warning cycle for a member without deleting history."""
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message(
                '❌ This command can only be used by moderators inside a server.',
                ephemeral=True,
            )
            return

        if not self._is_moderator(interaction.user):
            await interaction.response.send_message(
                '❌ Only moderators and above can use `/resetwarnings`.',
                ephemeral=True,
            )
            return

        init_db()
        guild_id = str(interaction.guild.id)
        user_id = str(user.id)

        with get_db_session() as db:
            active_warnings = DatabaseManager.get_active_warnings(db, guild_id, user_id)
            cleared_count = len(active_warnings)

            if cleared_count == 0:
                await interaction.response.send_message(
                    f'ℹ️ {user.mention} has no active warnings to reset.',
                    ephemeral=True,
                )
                return

            DatabaseManager.clear_active_warnings(db, guild_id, user_id)

        role_note = await self._sync_warned_role(
            guild=interaction.guild,
            member=user,
            should_have_role=False,
        )

        await interaction.response.send_message(
            f'✅ Reset {cleared_count} active warning(s) for {user.mention}.'
            + (f' {role_note}' if role_note else ''),
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(WarnCog(bot))
