"""
Admin commands for Cocobot.

This module contains administrative commands that can only be used by server admins.
"""

import discord
from discord.ext import commands


class AdminCog(commands.Cog):
    """
    Administrative commands that can only be used by server admins.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reset_reminder", hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_visa_reminder(self, ctx, member: discord.Member = None):
        """
        Reset the visa reminder status for a user.
        If no user is specified, reset for the command sender.
        Usage: !reset_reminder [@user] (only works for admins)
        """
        if member is None:
            member = ctx.author

        # Reset the visa reminder status for the user
        success = await self.bot.reset_visa_reminder_for_user(str(member.id))

        if success:
            response = f"✅ Visa reminder status reset for {member.mention}. They will be reminded again on their next 'visa' message in the visa channel."
        else:
            response = f"⚠️ {member.mention} was not found in the visa reminder database or was never reminded before."

        # Send an ephemeral message that only the command author can see
        # This is more reliable than trying to delete the command message
        await ctx.send(response, ephemeral=True)


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
