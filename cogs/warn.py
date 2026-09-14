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

# Kicks and role fails belong in logs, not just ephemeral replies
import logging

# WARNED_ROLE_ID from the environment
import os

# Member, Embed, Forbidden, HTTPException
import discord

# Slash commands, guild_only, default_permissions
from discord import app_commands

# Cog base
from discord.ext import commands

# Warnings live in the DB; sessions and init too
from utils.database import DatabaseManager, get_db_session, init_db

# Sanitize reasons; escape markdown so embeds don't explode
from utils.security import InputSanitizer, escape_markdown

# Module logger
logger = logging.getLogger(__name__)


# Three strikes, then a kick — coconut justice
class WarnCog(commands.Cog):
    """Slash command for warning members and kicking them on the third warning."""

    # Strike three is the door
    MAX_WARNINGS = 3

    # Default reason if the mod is too busy to type
    DEFAULT_REASON = 'Probably not read the #rules ¯\\_(ツ)_/¯'

    # Footer since 1875, allegedly
    FOOTER_TEXT = '© Coconut wisdom since 1875'

    def __init__(self, bot: commands.Bot):
        # Bot handle
        self.bot = bot

        # 0 means "role not configured"; don't crash on missing env
        self.warned_role_id = int(os.getenv('WARNED_ROLE_ID', '0'))

    # Mods and above: admin, timeout, kick, ban, or manage messages
    @staticmethod
    def _is_moderator(member: discord.Member) -> bool:
        """Return whether the member has moderator-or-higher privileges."""
        # Snapshot permissions once
        permissions = member.guild_permissions

        # Any of these bits counts as staff
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
        # Don't warn other bots; they don't read #rules
        if target.bot:
            # Original copy
            return '❌ Bots cannot be warned.'

        # No self-warn for the bit
        if target.id == moderator.id:
            # Original copy
            return '❌ You cannot warn yourself.'

        # DMs have no guild hierarchy
        if interaction.guild is None:
            # Original copy
            return '❌ This command can only be used in a server.'

        # Owner is above coconut law
        if target.id == interaction.guild.owner_id:
            # Original copy
            return '❌ The server owner cannot be warned.'

        # Staff-on-staff is a ticket, not /warn
        if self._is_moderator(target):
            # Original copy
            return '❌ Moderators and above cannot be warned.'

        # Role positions; missing top_role → 0
        moderator_role_position = getattr(moderator.top_role, 'position', 0)

        # Same for the accused
        target_role_position = getattr(target.top_role, 'position', 0)

        # Owner can warn down; everyone else must outrank the target
        if (
            moderator.id != interaction.guild.owner_id
            and target_role_position >= moderator_role_position
        ):
            # Original copy
            return '❌ You can only warn members below your highest role.'

        # Need the bot member to check kick perms
        bot_member = interaction.guild.me or interaction.guild.get_member(self.bot.user.id)

        # Cache miss on ourselves: weird, fail closed
        if bot_member is None:
            # Original copy
            return '❌ I could not verify my server permissions.'

        # Kick is required for strike three
        if not bot_member.guild_permissions.kick_members:
            # Original copy
            return '❌ I need the **Kick Members** permission for the warning system.'

        # Bot must sit above the target
        bot_role_position = getattr(bot_member.top_role, 'position', 0)

        # Target too high for the coconut
        if target_role_position >= bot_role_position:
            # Original copy
            return '❌ I cannot moderate or kick that member because their top role is too high.'

        # All checks passed
        return None

    # 1st, 2nd, 3rd, then boring th
    @staticmethod
    def _format_ordinal(number: int) -> str:
        """Return a human-friendly ordinal string."""
        # 11th, 12th, 13th are the English trap
        if 10 <= number % 100 <= 20:
            # Always th in the teens
            suffix = 'th'

        # Everyone else: 1st 2nd 3rd else th
        else:
            # Dict lookup beats another if-ladder
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(number % 10, 'th')

        # Glue number and suffix
        return f'{number}{suffix}'

    # Look up the warned role by configured id
    @staticmethod
    def _get_warned_role(guild: discord.Guild, role_id: int) -> discord.Role | None:
        """Return the configured warned role, if available."""
        # 0 or negative: not configured
        if role_id <= 0:
            # Caller will warn in logs
            return None

        # May still be None if the role was deleted
        return guild.get_role(role_id)

    # Can we actually assign this role?
    @staticmethod
    def _can_manage_role(
        guild: discord.Guild,
        bot_member: discord.Member,
        role: discord.Role | None,
    ) -> bool:
        """Check whether the bot can assign or remove the configured role."""
        # Missing or @everyone: no
        if role is None or role == guild.default_role:
            # Fail closed
            return False

        # Bot top role must be strictly above the warned role
        return getattr(bot_member.top_role, 'position', 0) > getattr(role, 'position', 0)

    async def _sync_warned_role(
        self,
        guild: discord.Guild,
        member: discord.Member,
        should_have_role: bool,
    ) -> str | None:
        """Assign or remove the warned role and return a user-facing note on failure."""
        # Resolve ourselves
        bot_member = guild.me or guild.get_member(self.bot.user.id)

        # Can't check hierarchy without a Member
        if bot_member is None:
            # Log for ops
            logger.warning('Could not resolve bot member for warned role management.')

            # Warning still recorded
            return '⚠️ Warning recorded, but I could not verify my role permissions.'

        # Fetch the role
        warned_role = self._get_warned_role(guild, self.warned_role_id)

        # Missing config or deleted role
        if warned_role is None:
            # Log
            logger.warning('WARNED_ROLE_ID is not configured or the warned role is missing.')

            # User note
            return '⚠️ Warning recorded, but the configured warned role was not found.'

        # Hierarchy fail
        if not self._can_manage_role(guild, bot_member, warned_role):
            # Include role id
            logger.warning('Warned role %s is above the bot role hierarchy.', warned_role.id)

            # User note
            return '⚠️ Warning recorded, but I could not manage the configured warned role.'

        # Add or remove as needed
        try:
            # Should have it and doesn't
            if should_have_role and warned_role not in member.roles:
                # Audit log reason
                await member.add_roles(warned_role, reason='Warning system: warned role assigned')

            # Shouldn't have it but does
            elif not should_have_role and warned_role in member.roles:
                # Kick path clears the role
                await member.remove_roles(
                    warned_role,
                    reason='Warning system: warned role removed',
                )

        # Missing Manage Roles
        except discord.Forbidden:
            # Log the member
            logger.warning('Missing permissions while managing warned role for %s.', member)

            # User note
            return '⚠️ Warning recorded, but I do not have permission to manage the warned role.'

        # Discord said no for some other HTTP reason
        except discord.HTTPException as exc:
            # Error level
            logger.error('Discord rejected warned role update for %s: %s', member, exc)

            # User note
            return '⚠️ Warning recorded, but Discord rejected the warned role update.'

        # Role in the desired state
        return None

    # Embed for channel and optional DM
    @staticmethod
    def _build_warning_embed(
        member: discord.Member,
        moderator: discord.Member,
        reason: str,
        warning_number: int,
        kicked: bool,
    ) -> discord.Embed:
        """Build a warning card embed for the channel and optional DM."""
        # Strike three: red
        if kicked:
            # Title
            title = '🛑 Warning limit reached'

            # Color
            color = discord.Color.red()

        # Second: orange, last chance
        elif warning_number == 2:
            # Title
            title = '⚠️ Final warning'

            # Color
            color = discord.Color.orange()

        # First: gold
        else:
            # Title
            title = '⚠️ Warning issued'

            # Color
            color = discord.Color.gold()

        # "1st" etc. for the sermon
        ordinal = WarnCog._format_ordinal(warning_number)

        # Original user-facing copy; don't punch it up
        summary = (
            "You've just been warned by a coconut. Isn't that embarrassing? "
            f'Anyway, **this is your {ordinal} warning**. Warning #3 results '
            'in a kick off this server. You can still join again.'
        )

        # Card body
        embed = discord.Embed(
            title=title,
            description=summary,
            color=color,
            timestamp=discord.utils.utcnow(),
        )

        # Who got it
        embed.add_field(name='Member', value=member.mention, inline=True)

        # Who issued it
        embed.add_field(name='Moderator', value=moderator.mention, inline=True)

        # Why
        embed.add_field(name='Reason', value=reason, inline=False)

        # Footer
        embed.set_footer(text=WarnCog.FOOTER_TEXT)

        # Thumbnail if they have an avatar
        if member.display_avatar:
            # URL from display_avatar
            embed.set_thumbnail(url=member.display_avatar.url)

        # Ready to send
        return embed

    # DM is best-effort; closed DMs shouldn't fail the command
    @staticmethod
    async def _try_notify_member(member: discord.Member, embed: discord.Embed) -> None:
        """Attempt to DM the warned member without failing the command."""
        # Try the DM
        try:
            # Same embed as the channel
            await member.send(embed=embed)

        # Privacy settings or HTTP
        except (discord.Forbidden, discord.HTTPException):
            # Info, not error — this is common
            logger.info('Could not DM warning card to %s', member)

    # /warn
    @app_commands.command(
        name='warn',
        description='Warn a member. The third warning automatically kicks them.',
    )
    # Servers only
    @app_commands.guild_only()
    # Discord UI hint; we still check _is_moderator
    @app_commands.default_permissions(moderate_members=True)
    # Parameter help
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
        # Need a guild and a Member invoker
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            # Ephemeral
            await interaction.response.send_message(
                '❌ This command can only be used by moderators inside a server.',
                ephemeral=True,
            )

            # Stop
            return

        # Permission bit check
        if not self._is_moderator(interaction.user):
            # Ephemeral
            await interaction.response.send_message(
                '❌ Only moderators and above can use `/warn`.',
                ephemeral=True,
            )

            # Stop
            return

        # Hierarchy and bot perms
        validation_error = self._validate_target(interaction, interaction.user, user)

        # Any string is a hard stop
        if validation_error:
            # Show the specific no
            await interaction.response.send_message(validation_error, ephemeral=True)

            # Stop
            return

        # Ensure tables exist
        init_db()

        # Cap length, strip junk
        sanitized_reason = InputSanitizer.sanitize_text(
            reason or self.DEFAULT_REASON,
            max_length=500,
        )

        # Safe for embeds
        display_reason = escape_markdown(sanitized_reason)

        # String ids for the DB
        guild_id = str(interaction.guild.id)

        # Target id
        user_id = str(user.id)

        # Defer; DB + kick can exceed 3s
        await interaction.response.defer()

        # One session for read/create
        with get_db_session() as db:
            # Active cycle only
            active_warnings = DatabaseManager.get_active_warnings(db, guild_id, user_id)

            # How many already
            warning_count = len(active_warnings)

            # Already at max: don't insert another row
            if warning_count >= self.MAX_WARNINGS:
                # Treat as strike three
                warning_number = self.MAX_WARNINGS

            # Insert a new warning
            else:
                # Persist
                warning_entry = DatabaseManager.create_warning_entry(
                    db=db,
                    guild_id=guild_id,
                    user_id=user_id,
                    username=user.display_name,
                    moderator_id=str(interaction.user.id),
                    moderator_name=interaction.user.display_name,
                    reason=sanitized_reason or None,
                )

                # Number from the row
                warning_number = warning_entry.warning_number

        # Kick if we hit the cap
        should_kick = warning_number >= self.MAX_WARNINGS

        # Build the card
        embed = self._build_warning_embed(
            member=user,
            moderator=interaction.user,
            reason=display_reason,
            warning_number=warning_number,
            kicked=should_kick,
        )

        # DM first; kick would make this harder
        await self._try_notify_member(user, embed)

        # Role on if staying, off if kicking
        role_note = await self._sync_warned_role(
            guild=interaction.guild,
            member=user,
            should_have_role=not should_kick,
        )

        # The door
        if should_kick:
            # Attempt kick
            try:
                # Audit reason
                await user.kick(reason='User has been warned too many times.')

            # Role too low or missing perm at kick time
            except discord.Forbidden:
                # Ephemeral followup
                await interaction.followup.send(
                    '❌ I could not kick that member. Please check my role position and permissions.',
                    ephemeral=True,
                )

                # Don't clear warnings if kick failed
                return

            # Other Discord errors
            except discord.HTTPException as exc:
                # Log
                logger.error('Failed to kick warned member %s: %s', user, exc)

                # Ephemeral
                await interaction.followup.send(
                    '❌ Discord rejected the kick request. Please try again.',
                    ephemeral=True,
                )

                # Keep the cycle
                return

            # Kick succeeded: reset active warnings
            with get_db_session() as db:
                # History stays; active count goes to zero
                DatabaseManager.clear_active_warnings(db, guild_id, user_id)

        # Role note or None as content
        followup_message = role_note or None

        # Public-ish followup with the embed
        await interaction.followup.send(content=followup_message, embed=embed)

    # /resetwarnings
    @app_commands.command(
        name='resetwarnings',
        description='Reset a member’s active warning count.',
    )
    # Guild only
    @app_commands.guild_only()
    # Same default perm hint
    @app_commands.default_permissions(moderate_members=True)
    # Who to reset
    @app_commands.describe(user='The member whose warnings should be reset')
    async def resetwarnings_command(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
    ):
        """Reset the active warning cycle for a member without deleting history."""
        # Guild + Member invoker
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            # Ephemeral
            await interaction.response.send_message(
                '❌ This command can only be used by moderators inside a server.',
                ephemeral=True,
            )

            # Stop
            return

        # Staff check
        if not self._is_moderator(interaction.user):
            # Ephemeral
            await interaction.response.send_message(
                '❌ Only moderators and above can use `/resetwarnings`.',
                ephemeral=True,
            )

            # Stop
            return

        # Tables
        init_db()

        # Guild id string
        guild_id = str(interaction.guild.id)

        # User id string
        user_id = str(user.id)

        # Session for count + clear
        with get_db_session() as db:
            # Active only
            active_warnings = DatabaseManager.get_active_warnings(db, guild_id, user_id)

            # How many we'd clear
            cleared_count = len(active_warnings)

            # Nothing to do
            if cleared_count == 0:
                # Ephemeral info
                await interaction.response.send_message(
                    f'ℹ️ {user.mention} has no active warnings to reset.',
                    ephemeral=True,
                )

                # Stop
                return

            # Clear the cycle
            DatabaseManager.clear_active_warnings(db, guild_id, user_id)

        # Drop the warned role
        role_note = await self._sync_warned_role(
            guild=interaction.guild,
            member=user,
            should_have_role=False,
        )

        # Confirm, append role note if any
        await interaction.response.send_message(
            f'✅ Reset {cleared_count} active warning(s) for {user.mention}.'
            + (f' {role_note}' if role_note else ''),
            ephemeral=True,
        )


# Load WarnCog
async def setup(bot: commands.Bot):
    # Attach
    await bot.add_cog(WarnCog(bot))
