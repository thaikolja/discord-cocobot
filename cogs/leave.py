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

"""
Leave announcements for Cocobot.

Picks a random pre-written coda from assets/data/messages.json and prefixes
it with a waving-hand line that names the member. Each coda is used once
before the pool reshuffles. Templates are never generated at runtime.
"""

import json
import logging
import os
import random

import discord
from discord import app_commands
from discord.ext import commands

from utils.security import is_moderator_or_above

logger = logging.getLogger('discord')

MESSAGES_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'assets', 'data', 'messages.json')
)
LEAVE_PREFIX_EMOJI = '👋'
DEFAULT_LEAVE_LOG_CHANNEL_ID = 1513856672966246410
FORBIDDEN_CODA_MARKERS = ('{name}', '{user}', LEAVE_PREFIX_EMOJI, '**')


def _coda_from_entry(entry) -> str | None:
    """Return a leave coda from a Chrome-locale-style {message: '...'} object."""
    if isinstance(entry, str):
        text = entry
    elif isinstance(entry, dict):
        text = entry.get('message')
    else:
        return None
    if not isinstance(text, str):
        return None
    coda = text.strip()
    if not coda:
        return None
    if any(marker in coda for marker in FORBIDDEN_CODA_MARKERS):
        return None
    return coda


def load_leave_messages(path: str = MESSAGES_PATH) -> list[str]:
    """Load static leave codas. Does not call any LLM."""
    with open(path, encoding='utf-8') as fh:
        data = json.load(fh)
    if isinstance(data, dict):
        def sort_key(key: str):
            try:
                return (0, int(key))
            except (TypeError, ValueError):
                return (1, str(key))

        values = [data[key] for key in sorted(data, key=sort_key)]
    else:
        values = data
    templates = [_coda_from_entry(entry) for entry in values]
    return [template for template in templates if template is not None]


def escape_display_name(display_name: str) -> str:
    """Escape Discord markdown in a display name so **bold** stays intact."""
    return (
        display_name.replace('\\', '\\\\')
        .replace('*', r'\*')
        .replace('_', r'\_')
        .replace('`', r'\`')
    )


def format_leave_message(display_name: str, coda: str = '') -> str:
    """Build the public leave line: emoji, bold name, then the static coda."""
    bold_name = f'**{escape_display_name(display_name)}**'
    prefix = f'{LEAVE_PREFIX_EMOJI} {bold_name} has left the server.'
    stripped = coda.strip()
    if stripped:
        return f'{prefix} {stripped}'
    return prefix


def format_leave_log_message(display_name: str, user_id: int | str) -> str:
    """Build the professional #logs line. No emoji, no lore."""
    return f'{display_name} ({user_id}) left the server.'


class LeaveMessageDeck:
    """Shuffle-bag of templates: each line is used once before any repeat."""

    def __init__(self, templates: list[str]):
        self._source = list(templates)
        self._bag: list[str] = []
        self._last: str | None = None

    def draw(self) -> str | None:
        """Return the next unused template, reshuffling after the bag is empty."""
        if not self._source:
            return None
        if not self._bag:
            self._refill()
        template = self._bag.pop()
        self._last = template
        return template

    def _refill(self) -> None:
        self._bag = list(self._source)
        random.shuffle(self._bag)
        if (
            self._last is not None
            and len(self._bag) > 1
            and self._bag[-1] == self._last
        ):
            self._bag[0], self._bag[-1] = self._bag[-1], self._bag[0]


def pick_leave_message(display_name: str, deck: LeaveMessageDeck) -> str:
    """Draw the next coda and wrap it in the public leave prefix."""
    coda = deck.draw() or ''
    return format_leave_message(display_name, coda)


class LeaveCog(commands.Cog):
    """Announce member leaves from a static template pool."""

    def __init__(self, bot: commands.Bot, messages_path: str = MESSAGES_PATH):
        self.bot = bot
        raw_log = os.getenv('LEAVE_LOG_CHANNEL_ID', str(DEFAULT_LEAVE_LOG_CHANNEL_ID)).strip()
        self.log_channel_id = (
            int(raw_log) if raw_log.isdigit() else DEFAULT_LEAVE_LOG_CHANNEL_ID
        )
        self._last_channel_ids: dict[tuple[int, int], int] = {}
        try:
            templates = load_leave_messages(messages_path)
        except (OSError, json.JSONDecodeError) as exc:
            logger.error('Failed to load leave messages from %s: %s', messages_path, exc)
            templates = []
        self.use_templates(templates)

    def use_templates(self, templates: list[str]) -> None:
        """Replace the template pool and reset the no-repeat deck."""
        self.templates = list(templates)
        self.deck = LeaveMessageDeck(self.templates)

    def remember_last_channel(self, guild_id: int, user_id: int, channel_id: int) -> None:
        """Remember the last text channel a member spoke in."""
        self._last_channel_ids[(guild_id, user_id)] = channel_id

    def pop_last_channel(self, guild: discord.Guild, user_id: int):
        """Return the last text channel for this member, or None if they never spoke."""
        channel_id = self._last_channel_ids.pop((guild.id, user_id), None)
        if channel_id is None:
            return None
        return guild.get_channel(channel_id)

    def resolve_log_channel(self, guild: discord.Guild):
        """Return the professional logs channel, or None if it is missing."""
        return guild.get_channel(self.log_channel_id)

    async def announce_leave(self, member: discord.Member, channel) -> bool:
        """Post a random leave template. Returns True if the message was sent."""
        if channel is None:
            logger.warning('Leave announcement skipped: no last-message channel')
            return False
        try:
            await channel.send(pick_leave_message(member.display_name, self.deck))
            return True
        except (discord.Forbidden, discord.HTTPException) as exc:
            logger.error('Failed to send leave announcement: %s', exc)
            return False

    async def log_leave(self, member: discord.Member) -> None:
        """Post a professional leave line to #logs. Must not raise to callers."""
        channel = self.resolve_log_channel(member.guild)
        if channel is None:
            logger.warning(
                'Leave log skipped: channel %s not found', self.log_channel_id
            )
            return
        try:
            await channel.send(
                format_leave_log_message(member.display_name, member.id)
            )
        except (discord.Forbidden, discord.HTTPException) as exc:
            logger.error('Failed to send leave log: %s', exc)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Track the last guild text channel each human spoke in."""
        if message.author.bot or message.guild is None:
            return
        channel_id = getattr(message.channel, 'id', None)
        if channel_id is None:
            return
        self.remember_last_channel(message.guild.id, message.author.id, channel_id)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Post a leave announcement for humans who leave, are kicked, or banned."""
        if member.bot:
            return
        fun_channel = self.pop_last_channel(member.guild, member.id)
        if fun_channel is not None:
            await self.announce_leave(member, fun_channel)
        await self.log_leave(member)

    @app_commands.command(
        name='simulate-leave',
        description='Dry-run a leave announcement for a member (does not remove them)',
    )
    @app_commands.describe(
        user='The member to announce as leaving (defaults to you)',
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(moderate_members=True)
    async def simulate_leave(
        self,
        interaction: discord.Interaction,
        user: discord.Member = None,
    ):
        """Post a random leave template without anyone leaving."""
        if not isinstance(interaction.user, discord.Member) or not is_moderator_or_above(
            interaction.user
        ):
            try:
                await interaction.response.send_message(
                    '❌ Only moderators and above can use `/simulate-leave`.',
                    ephemeral=True,
                )
            except (discord.Forbidden, discord.HTTPException) as exc:
                logger.error('Failed to send leave announcement: %s', exc)
            return

        target = user or interaction.user
        message = pick_leave_message(target.display_name, self.deck)
        try:
            await interaction.response.send_message(message)
        except (discord.Forbidden, discord.HTTPException) as exc:
            logger.error('Failed to send leave announcement: %s', exc)


async def setup(bot: commands.Bot):
    await bot.add_cog(LeaveCog(bot))
