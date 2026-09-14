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
    DEFAULT_LEAVE_LOG_CHANNEL_ID,
    LeaveCog,
    LeaveMessageDeck,
    MESSAGES_PATH,
    format_leave_log_message,
    format_leave_message,
    load_leave_messages,
    pick_leave_message,
    setup,
)
from utils.security import is_moderator_or_above

SAMPLE_CODA = 'The palm declines to comment.'


def _forbidden():
    response = MagicMock()
    response.status = 403
    return discord.Forbidden(response, 'Missing Permissions')


def _perms(**flags):
    permissions = MagicMock(spec=discord.Permissions)
    permissions.administrator = False
    permissions.moderate_members = False
    permissions.kick_members = False
    permissions.ban_members = False
    permissions.manage_messages = False
    for name, value in flags.items():
        setattr(permissions, name, value)
    return permissions


@pytest.fixture
def mock_channel():
    channel = MagicMock(spec=discord.TextChannel)
    channel.send = AsyncMock()
    return channel


@pytest.fixture
def mock_log_channel():
    channel = MagicMock(spec=discord.TextChannel)
    channel.id = DEFAULT_LEAVE_LOG_CHANNEL_ID
    channel.send = AsyncMock()
    return channel


@pytest.fixture
def mock_last_channel():
    channel = MagicMock(spec=discord.TextChannel)
    channel.id = 777
    channel.send = AsyncMock()
    return channel


@pytest.fixture
def mock_guild(mock_channel, mock_log_channel, mock_last_channel):
    guild = MagicMock(spec=discord.Guild)
    guild.id = 99
    guild.system_channel = mock_channel
    guild.owner_id = 1

    def get_channel(channel_id):
        if channel_id == DEFAULT_LEAVE_LOG_CHANNEL_ID:
            return mock_log_channel
        if channel_id == mock_last_channel.id:
            return mock_last_channel
        return None

    guild.get_channel = MagicMock(side_effect=get_channel)
    return guild


@pytest.fixture
def mock_member(mock_guild):
    member = MagicMock(spec=discord.Member)
    member.id = 12345
    member.bot = False
    member.display_name = 'Kolja'
    member.guild = mock_guild
    member.guild_permissions = _perms()
    return member


@pytest.fixture
def leave_cog():
    bot = MagicMock(spec=commands.Bot)
    bot.tree = MagicMock()
    cog = LeaveCog(bot)
    cog.use_templates([SAMPLE_CODA])
    return cog


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

def test_messages_json_has_exactly_10_unique_codas():
    with open(MESSAGES_PATH, encoding='utf-8') as fh:
        data = json.load(fh)
    assert isinstance(data, dict)
    entries = list(data.values())
    assert all(isinstance(entry, dict) for entry in entries)
    messages = [entry['message'] for entry in entries]
    assert len(messages) == 10
    assert len(set(messages)) == 10
    for message in messages:
        assert '{name}' not in message
        assert '{user}' not in message
        assert '👋' not in message
        assert '**' not in message


def test_load_leave_messages_reads_the_static_file():
    messages = load_leave_messages()
    assert len(messages) == 10
    assert all(isinstance(message, str) and message.strip() for message in messages)


# ---------------------------------------------------------------------------
# formatting
# ---------------------------------------------------------------------------

def test_format_leave_message_uses_prefix_and_coda():
    assert format_leave_message('Kolja', SAMPLE_CODA) == (
        '👋 **Kolja** has left the server. The palm declines to comment.'
    )


def test_format_leave_message_escapes_markdown_in_name():
    result = format_leave_message('foo*bar', SAMPLE_CODA)
    assert result == r'👋 **foo\*bar** has left the server. The palm declines to comment.'


def test_format_leave_log_message_is_plain():
    assert format_leave_log_message('Kolja', 12345) == 'Kolja (12345) left the server.'
    assert '👋' not in format_leave_log_message('Kolja', 12345)


def test_deck_draws_each_template_once_before_repeat():
    templates = [f'coda {i}' for i in range(5)]
    deck = LeaveMessageDeck(templates)
    drawn = [deck.draw() for _ in range(5)]
    assert len(drawn) == 5
    assert set(drawn) == set(templates)


def test_deck_refills_after_the_pool_is_exhausted():
    templates = ['coda a', 'coda b', 'coda c']
    deck = LeaveMessageDeck(templates)
    first = [deck.draw() for _ in range(3)]
    second = [deck.draw() for _ in range(3)]
    assert set(first) == set(templates)
    assert set(second) == set(templates)


def test_deck_never_repeats_the_same_template_twice_in_a_row():
    templates = ['coda a', 'coda b', 'coda c']
    deck = LeaveMessageDeck(templates)
    drawn = [deck.draw() for _ in range(30)]
    for previous, current in zip(drawn, drawn[1:]):
        assert previous != current


def test_pick_leave_message_uses_the_deck():
    deck = LeaveMessageDeck(['The coconut court shall compose itself.'])
    assert pick_leave_message('Kolja', deck) == (
        '👋 **Kolja** has left the server. The coconut court shall compose itself.'
    )


def test_pick_leave_message_fallback_when_empty():
    assert pick_leave_message('Kolja', LeaveMessageDeck([])) == (
        '👋 **Kolja** has left the server.'
    )


def test_leave_module_does_not_import_useai():
    import cogs.leave as leave_mod

    assert not hasattr(leave_mod, 'UseAI')


def test_owner_counts_as_staff(mock_member, mock_guild):
    mock_guild.owner_id = mock_member.id
    assert is_moderator_or_above(mock_member) is True


def test_moderator_permission_counts_as_staff(mock_member):
    mock_member.guild_permissions = _perms(moderate_members=True)
    assert is_moderator_or_above(mock_member) is True


def test_ordinary_member_is_not_staff(mock_member):
    assert is_moderator_or_above(mock_member) is False


# ---------------------------------------------------------------------------
# on_member_remove
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_on_member_remove_posts_fun_line_in_last_channel(
    leave_cog, mock_member, mock_channel, mock_last_channel, mock_log_channel
):
    leave_cog.remember_last_channel(mock_member.guild.id, mock_member.id, mock_last_channel.id)

    await leave_cog.on_member_remove(mock_member)

    mock_last_channel.send.assert_awaited_once_with(
        '👋 **Kolja** has left the server. The palm declines to comment.'
    )
    mock_channel.send.assert_not_called()
    mock_log_channel.send.assert_awaited_once_with('Kolja (12345) left the server.')


@pytest.mark.asyncio
async def test_on_member_remove_skips_bots(
    leave_cog, mock_member, mock_channel, mock_log_channel
):
    mock_member.bot = True

    with patch.object(leave_cog.deck, 'draw') as draw:
        await leave_cog.on_member_remove(mock_member)

    mock_channel.send.assert_not_called()
    mock_log_channel.send.assert_not_called()
    draw.assert_not_called()


@pytest.mark.asyncio
async def test_on_member_remove_logs_only_when_member_never_spoke(
    leave_cog, mock_member, mock_channel, mock_last_channel, mock_log_channel
):
    await leave_cog.on_member_remove(mock_member)

    mock_channel.send.assert_not_called()
    mock_last_channel.send.assert_not_called()
    mock_log_channel.send.assert_awaited_once_with('Kolja (12345) left the server.')


@pytest.mark.asyncio
async def test_log_failure_does_not_block_fun_announcement(
    leave_cog, mock_member, mock_last_channel, mock_log_channel
):
    leave_cog.remember_last_channel(mock_member.guild.id, mock_member.id, mock_last_channel.id)
    mock_log_channel.send = AsyncMock(side_effect=_forbidden())

    await leave_cog.on_member_remove(mock_member)

    mock_last_channel.send.assert_awaited_once()


@pytest.mark.asyncio
async def test_on_message_remembers_last_text_channel(
    leave_cog, mock_member, mock_last_channel
):
    message = MagicMock(spec=discord.Message)
    message.author = mock_member
    message.author.bot = False
    message.guild = mock_member.guild
    message.channel = mock_last_channel

    await leave_cog.on_message(message)

    assert leave_cog.pop_last_channel(mock_member.guild, mock_member.id) is mock_last_channel


@pytest.mark.asyncio
async def test_on_member_remove_swallows_forbidden(
    leave_cog, mock_member, mock_last_channel
):
    leave_cog.remember_last_channel(mock_member.guild.id, mock_member.id, mock_last_channel.id)
    mock_last_channel.send = AsyncMock(side_effect=_forbidden())

    await leave_cog.on_member_remove(mock_member)


# ---------------------------------------------------------------------------
# /simulate-leave (dry-run)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_simulate_leave_posts_only_in_invoking_channel(
    leave_cog, mock_interaction, mock_channel, mock_last_channel, mock_log_channel
):
    mock_interaction.user.guild_permissions = _perms(moderate_members=True)
    other = MagicMock(spec=discord.Member)
    other.id = 999
    other.display_name = 'Leaver'
    other.bot = False
    leave_cog.remember_last_channel(mock_interaction.guild.id, other.id, mock_last_channel.id)

    await leave_cog.simulate_leave.callback(leave_cog, mock_interaction, other)

    mock_interaction.response.send_message.assert_awaited_once_with(
        '👋 **Leaver** has left the server. The palm declines to comment.'
    )
    mock_channel.send.assert_not_called()
    mock_last_channel.send.assert_not_called()
    mock_log_channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_simulate_leave_defaults_to_invoker(leave_cog, mock_interaction):
    mock_interaction.guild.owner_id = mock_interaction.user.id

    await leave_cog.simulate_leave.callback(leave_cog, mock_interaction, None)

    mock_interaction.response.send_message.assert_awaited_once_with(
        '👋 **Kolja** has left the server. The palm declines to comment.'
    )


@pytest.mark.asyncio
async def test_simulate_leave_rejects_ordinary_members(leave_cog, mock_interaction):
    await leave_cog.simulate_leave.callback(leave_cog, mock_interaction, None)

    mock_interaction.response.send_message.assert_awaited_once()
    args, kwargs = mock_interaction.response.send_message.call_args
    assert 'Only moderators and above' in args[0]
    assert kwargs.get('ephemeral') is True


@pytest.mark.asyncio
async def test_simulate_leave_swallows_forbidden(
    leave_cog, mock_interaction, mock_member
):
    mock_interaction.guild.owner_id = mock_member.id
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
    assert len(cog.templates) == 10
