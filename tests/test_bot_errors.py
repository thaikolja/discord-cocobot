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

"""Permission-denied replies must be ephemeral (slash) or private (prefix)."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from discord import app_commands
from discord.ext import commands

from bot import (
    PERMISSION_DENIED_MESSAGE,
    _send_prefix_permission_denied,
    is_bare_bot_mention,
    send_ephemeral,
)


@pytest.mark.asyncio
async def test_send_ephemeral_uses_response_when_not_done():
    interaction = MagicMock()
    interaction.response.is_done.return_value = False
    interaction.response.send_message = AsyncMock()
    interaction.followup.send = AsyncMock()

    await send_ephemeral(interaction, PERMISSION_DENIED_MESSAGE)

    interaction.response.send_message.assert_awaited_once_with(
        PERMISSION_DENIED_MESSAGE, ephemeral=True
    )
    interaction.followup.send.assert_not_called()


@pytest.mark.asyncio
async def test_send_ephemeral_uses_followup_when_done():
    interaction = MagicMock()
    interaction.response.is_done.return_value = True
    interaction.response.send_message = AsyncMock()
    interaction.followup.send = AsyncMock()

    await send_ephemeral(interaction, PERMISSION_DENIED_MESSAGE)

    interaction.followup.send.assert_awaited_once_with(
        PERMISSION_DENIED_MESSAGE, ephemeral=True
    )


@pytest.mark.asyncio
async def test_app_command_check_failure_is_ephemeral():
    from bot import Cocobot

    bot = MagicMock(spec=Cocobot)
    interaction = MagicMock()
    interaction.response.is_done.return_value = False
    interaction.response.send_message = AsyncMock()
    interaction.followup.send = AsyncMock()
    interaction.command = MagicMock()
    interaction.command.name = 'simulate-leave'
    interaction.user = 'Kolja'

    await Cocobot.on_app_command_error(
        bot, interaction, app_commands.CheckFailure('nope')
    )

    interaction.response.send_message.assert_awaited_once_with(
        PERMISSION_DENIED_MESSAGE, ephemeral=True
    )
    interaction.followup.send.assert_not_called()


@pytest.mark.asyncio
async def test_prefix_permission_denied_never_posts_to_channel():
    ctx = MagicMock()
    ctx.interaction = None
    ctx.send = AsyncMock()
    ctx.author.send = AsyncMock()

    await _send_prefix_permission_denied(ctx)

    ctx.send.assert_not_called()
    ctx.author.send.assert_awaited_once_with(PERMISSION_DENIED_MESSAGE)


def test_bare_bot_mention_is_true_for_mention_only():
    bot = MagicMock()
    bot.id = 42
    assert is_bare_bot_mention('<@42>', [bot], 42) is True
    assert is_bare_bot_mention('<@!42>', [bot], 42) is True


def test_bare_bot_mention_is_false_with_extra_text_or_bang_command():
    bot = MagicMock()
    bot.id = 42
    assert is_bare_bot_mention('<@42> hello', [bot], 42) is False
    assert is_bare_bot_mention('!cocobot', [bot], 42) is False
    assert is_bare_bot_mention('!cocobot', [], 42) is False
    assert is_bare_bot_mention('!test', [], 42) is False
    assert is_bare_bot_mention('!auto', [], 42) is False


def _fake_message(message_id, channel_id=10, author_id=20):
    message = MagicMock()
    message.id = message_id
    message.channel.id = channel_id
    message.author.id = author_id
    return message


def test_info_card_claim_is_once_per_message():
    from bot import Cocobot

    bot = Cocobot.__new__(Cocobot)
    bot._info_card_message_ids = set()
    bot._info_card_last_at = {}
    first = _fake_message(1, channel_id=1, author_id=1)
    assert bot._claim_info_card(first) is True
    assert bot._claim_info_card(first) is False


def test_info_card_claim_debounces_same_author_channel():
    from bot import Cocobot

    bot = Cocobot.__new__(Cocobot)
    bot._info_card_message_ids = set()
    bot._info_card_last_at = {}
    first = _fake_message(1, channel_id=99, author_id=7)
    second = _fake_message(2, channel_id=99, author_id=7)
    assert bot._claim_info_card(first) is True
    assert bot._claim_info_card(second) is False


@pytest.mark.asyncio
async def test_command_not_found_never_replies():
    from bot import Cocobot

    bot = MagicMock(spec=Cocobot)
    ctx = MagicMock()
    ctx.send = AsyncMock()
    ctx.command = None
    error = commands.CommandNotFound()

    await Cocobot.on_command_error(bot, ctx, error)

    ctx.send.assert_not_called()
