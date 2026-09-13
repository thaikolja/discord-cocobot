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

Picks a random pre-written template from assets/data/messages.json and
substitutes the member's server display name. Each template is used once
before the pool reshuffles. Templates are never generated at runtime.
"""

import json
import logging
import os
import random

import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger('discord')

MESSAGES_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'assets', 'data', 'messages.json')
)
NAME_PLACEHOLDER = '{name}'


def _template_from_entry(entry) -> str | None:
    """Return the sentence from a Chrome-locale-style {message: '...'} object."""
    if isinstance(entry, str):
        text = entry
    elif isinstance(entry, dict):
        text = entry.get('message')
    else:
        return None
    if isinstance(text, str) and NAME_PLACEHOLDER in text:
        return text
    return None


def load_leave_messages(path: str = MESSAGES_PATH) -> list[str]:
    """Load static leave templates. Does not call any LLM."""
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
    templates = [_template_from_entry(entry) for entry in values]
    return [template for template in templates if template is not None]


def escape_display_name(display_name: str) -> str:
    """Escape Discord markdown in a display name so **bold** stays intact."""
    return (
        display_name.replace('\\', '\\\\')
        .replace('*', r'\*')
        .replace('_', r'\_')
        .replace('`', r'\`')
    )


def format_leave_message(display_name: str, template: str) -> str:
    """Fill {name} with the member's display name wrapped in Discord bold."""
    return template.replace(
        NAME_PLACEHOLDER,
        f'**{escape_display_name(display_name)}**',
    )


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
    """Draw the next template and insert the display name."""
    template = deck.draw()
    if template is None:
        return f'**{escape_display_name(display_name)}** has left the server'
    return format_leave_message(display_name, template)


class LeaveCog(commands.Cog):
    """Announce member leaves from a static template pool."""

    def __init__(self, bot: commands.Bot, messages_path: str = MESSAGES_PATH):
        self.bot = bot
        raw_id = os.getenv('LEAVE_NOTIFY_CHANNEL_ID', '').strip()
        self.notify_channel_id = int(raw_id) if raw_id.isdigit() else None
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

    def resolve_notify_channel(self, guild: discord.Guild):
        """Return the override channel if configured, else the system channel."""
        if self.notify_channel_id is not None:
            channel = guild.get_channel(self.notify_channel_id)
            if channel is not None:
                return channel
        return guild.system_channel

    async def announce_leave(self, member: discord.Member, channel) -> bool:
        """Post a random leave template. Returns True if the message was sent."""
        if channel is None:
            logger.warning('Leave announcement skipped: no system/notify channel')
            return False
        try:
            await channel.send(pick_leave_message(member.display_name, self.deck))
            return True
        except (discord.Forbidden, discord.HTTPException) as exc:
            logger.error('Failed to send leave announcement: %s', exc)
            return False

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Post a leave announcement for humans who leave, are kicked, or banned."""
        if member.bot:
            return
        await self.announce_leave(member, self.resolve_notify_channel(member.guild))

    @app_commands.command(
        name='simulate-leave',
        description='Dry-run a leave announcement for a member (does not remove them)',
    )
    @app_commands.describe(
        user='The member to announce as leaving (defaults to you)',
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def simulate_leave(
        self,
        interaction: discord.Interaction,
        user: discord.Member = None,
    ):
        """Post a random leave template without anyone leaving."""
        target = user or interaction.user
        message = pick_leave_message(target.display_name, self.deck)
        try:
            await interaction.response.send_message(message)
        except (discord.Forbidden, discord.HTTPException) as exc:
            logger.error('Failed to send leave announcement: %s', exc)


async def setup(bot: commands.Bot):
    await bot.add_cog(LeaveCog(bot))
