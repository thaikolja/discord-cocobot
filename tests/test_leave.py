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

"""Tests for the leave-announcement cog (cogs/leave.py)."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from discord.ext import commands

from cogs.leave import (
    LeaveCog,
    LeaveMessageDeck,
    MESSAGES_PATH,
    format_leave_message,
    load_leave_messages,
    pick_leave_message,
    setup,
)

SAMPLE_TEMPLATE = '{name} packed a coconut and left.'


def _forbidden():
    response = MagicMock()
    response.status = 403
    return discord.Forbidden(response, 'Missing Permissions')


@pytest.fixture
def leave_cog():
    bot = MagicMock(spec=commands.Bot)
    bot.tree = MagicMock()
    cog = LeaveCog(bot)
    cog.use_templates([SAMPLE_TEMPLATE])
    return cog


@pytest.fixture
def mock_channel():
    channel = MagicMock(spec=discord.TextChannel)
    channel.send = AsyncMock()
    return channel


@pytest.fixture
def mock_guild(mock_channel):
    guild = MagicMock(spec=discord.Guild)
    guild.system_channel = mock_channel
    guild.get_channel = MagicMock(return_value=None)
    return guild


@pytest.fixture
def mock_member(mock_guild):
    member = MagicMock(spec=discord.Member)
    member.id = 12345
    member.bot = False
    member.display_name = 'Kolja'
    member.guild = mock_guild
    return member


@pytest.fixture
def mock_interaction(mock_guild, mock_member, mock_channel):
    interaction = MagicMock(spec=discord.Interaction)
    interaction.guild = mock_guild
    interaction.channel = mock_channel
    interaction.user = mock_member
    interaction.response = MagicMock()
    interaction.response.send_message = AsyncMock()
    return interaction


# ---------------------------------------------------------------------------
# messages.json (generated once, never rewritten at runtime)
# ---------------------------------------------------------------------------

def test_messages_json_has_exactly_50_unique_templates():
    with open(MESSAGES_PATH, encoding='utf-8') as fh:
        data = json.load(fh)
    assert isinstance(data, dict)
    assert not isinstance(data, list)
    entries = list(data.values())
    assert all(isinstance(entry, dict) for entry in entries)
    messages = [entry['message'] for entry in entries]
    assert len(messages) == 50
    assert len(set(messages)) == 50
    assert all('{name}' in message for message in messages)
    assert all('**' not in message for message in messages)


def test_load_leave_messages_reads_the_static_file():
    messages = load_leave_messages()
    assert len(messages) == 50
    assert all('{name}' in message for message in messages)


# ---------------------------------------------------------------------------
# formatting
# ---------------------------------------------------------------------------

def test_format_leave_message_replaces_placeholder():
    assert format_leave_message('Kolja', SAMPLE_TEMPLATE) == (
        '**Kolja** packed a coconut and left.'
    )


def test_format_leave_message_escapes_markdown_in_name():
    result = format_leave_message('foo*bar', '{name} left.')
    assert result == r'**foo\*bar** left.'


def test_deck_draws_each_template_once_before_repeat():
    templates = [f'*({{name}}) {i}*' for i in range(5)]
    deck = LeaveMessageDeck(templates)
    drawn = [deck.draw() for _ in range(5)]
    assert len(drawn) == 5
    assert set(drawn) == set(templates)


def test_deck_refills_after_the_pool_is_exhausted():
    templates = ['*{name} a*', '*{name} b*', '*{name} c*']
    deck = LeaveMessageDeck(templates)
    first = [deck.draw() for _ in range(3)]
    second = [deck.draw() for _ in range(3)]
    assert set(first) == set(templates)
    assert set(second) == set(templates)


def test_deck_never_repeats_the_same_template_twice_in_a_row():
    templates = ['*{name} a*', '*{name} b*', '*{name} c*']
    deck = LeaveMessageDeck(templates)
    drawn = [deck.draw() for _ in range(30)]
    for previous, current in zip(drawn, drawn[1:]):
        assert previous != current


def test_pick_leave_message_uses_the_deck():
    deck = LeaveMessageDeck(['{name} two'])
    assert pick_leave_message('Kolja', deck) == '**Kolja** two'


def test_pick_leave_message_fallback_when_empty():
    assert pick_leave_message('Kolja', LeaveMessageDeck([])) == (
        '**Kolja** has left the server'
    )


def test_leave_module_does_not_import_useai():
    import cogs.leave as leave_mod

    assert not hasattr(leave_mod, 'UseAI')


# ---------------------------------------------------------------------------
# on_member_remove
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_on_member_remove_posts_random_template(
    leave_cog, mock_member, mock_channel
):
    await leave_cog.on_member_remove(mock_member)

    mock_channel.send.assert_awaited_once_with(
        '**Kolja** packed a coconut and left.'
    )


@pytest.mark.asyncio
async def test_on_member_remove_skips_bots(leave_cog, mock_member, mock_channel):
    mock_member.bot = True

    with patch.object(leave_cog.deck, 'draw') as draw:
        await leave_cog.on_member_remove(mock_member)

    mock_channel.send.assert_not_called()
    draw.assert_not_called()


@pytest.mark.asyncio
async def test_on_member_remove_skips_when_no_channel(leave_cog, mock_member):
    mock_member.guild.system_channel = None
    mock_member.guild.get_channel = MagicMock(return_value=None)

    with patch.object(leave_cog.deck, 'draw') as draw:
        await leave_cog.on_member_remove(mock_member)

    draw.assert_not_called()


@pytest.mark.asyncio
async def test_on_member_remove_uses_channel_override(mock_guild, mock_member):
    override = MagicMock(spec=discord.TextChannel)
    override.send = AsyncMock()
    mock_guild.get_channel = MagicMock(return_value=override)

    bot = MagicMock(spec=commands.Bot)
    with patch.dict('os.environ', {'LEAVE_NOTIFY_CHANNEL_ID': '42'}, clear=False):
        cog = LeaveCog(bot)
    cog.use_templates([SAMPLE_TEMPLATE])

    await cog.on_member_remove(mock_member)

    mock_guild.get_channel.assert_called_with(42)
    override.send.assert_awaited_once_with('**Kolja** packed a coconut and left.')
    mock_guild.system_channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_on_member_remove_swallows_forbidden(leave_cog, mock_member, mock_channel):
    mock_channel.send = AsyncMock(side_effect=_forbidden())

    await leave_cog.on_member_remove(mock_member)


# ---------------------------------------------------------------------------
# /simulate-leave (dry-run)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_simulate_leave_posts_announcement(leave_cog, mock_interaction):
    other = MagicMock(spec=discord.Member)
    other.display_name = 'Leaver'
    other.bot = False

    await leave_cog.simulate_leave.callback(leave_cog, mock_interaction, other)

    mock_interaction.response.send_message.assert_awaited_once_with(
        '**Leaver** packed a coconut and left.'
    )


@pytest.mark.asyncio
async def test_simulate_leave_defaults_to_invoker(leave_cog, mock_interaction):
    await leave_cog.simulate_leave.callback(leave_cog, mock_interaction, None)

    mock_interaction.response.send_message.assert_awaited_once_with(
        '**Kolja** packed a coconut and left.'
    )


@pytest.mark.asyncio
async def test_simulate_leave_swallows_forbidden(
    leave_cog, mock_interaction, mock_member
):
    mock_interaction.response.send_message = AsyncMock(side_effect=_forbidden())

    await leave_cog.simulate_leave.callback(leave_cog, mock_interaction, mock_member)


# ---------------------------------------------------------------------------
# setup
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_setup_registers_simulate_command():
    bot = MagicMock(spec=commands.Bot)
    bot.add_cog = AsyncMock()

    await setup(bot)

    bot.add_cog.assert_awaited_once()
    cog = bot.add_cog.call_args[0][0]
    assert isinstance(cog, LeaveCog)
    assert any(cmd.name == 'simulate-leave' for cmd in cog.get_app_commands())
    assert len(cog.templates) == 50
