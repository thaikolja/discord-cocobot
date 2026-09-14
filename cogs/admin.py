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

"""Staff slash commands for Cocobot."""

import discord
from discord import app_commands
from discord.ext import commands

from utils.security import is_moderator_or_above


class AdminCog(commands.Cog):
    """Administrative slash commands for server staff."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='reset-reminder',
        description='Reset a member visa-channel reminder (staff only)',
    )
    @app_commands.describe(user='The member whose visa reminder should be reset')
    @app_commands.guild_only()
    @app_commands.default_permissions(moderate_members=True)
    async def reset_reminder(
        self,
        interaction: discord.Interaction,
        user: discord.Member = None,
    ):
        """Reset visa reminder status. Ephemeral; staff only."""
        if not isinstance(interaction.user, discord.Member) or not is_moderator_or_above(
            interaction.user
        ):
            await interaction.response.send_message(
                '❌ Only moderators and above can use `/reset-reminder`.',
                ephemeral=True,
            )
            return

        member = user or interaction.user
        success = await self.bot.reset_visa_reminder_for_user(str(member.id))
        if success:
            response = (
                f"✅ Visa reminder status reset for {member.mention}. "
                "They will be reminded again on their next visa-channel message."
            )
        else:
            response = (
                f"⚠️ {member.mention} was not found in the visa reminder database "
                "or was never reminded before."
            )
        await interaction.response.send_message(response, ephemeral=True)


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
