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

from bot import (
    PERMISSION_DENIED_MESSAGE,
    _send_prefix_permission_denied,
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
