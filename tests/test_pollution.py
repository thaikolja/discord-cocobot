#  Copyright (C) 2025 by Kolja Nolte
#  kolja.nolte@gmail.com
#  https://gitlab.com/thailand-discord/bots/cocobot
#
#  This work is licensed under the MIT License. You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
#  and to permit persons to whom the Software is furnished to do so, subject to the condition that the above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  For more information, visit: https://opensource.org/licenses/MIT
#
#  Author:    Kolja Nolte
#  Email:     kolja.nolte@gmail.com
#  License:   MIT
#  Date:      2014-2025
#  Package:   cocobot Discord Bot

# Import mocking utilities from unittest.mock
from unittest.mock import AsyncMock, MagicMock, patch

# Import the discord library for interacting with Discord
import discord

# Import pytest for unit testing functionality
import pytest

# Import pytest_asyncio for asynchronous test support
import pytest_asyncio

# Import commands extension from discord.ext
from discord.ext import commands

# Import PollutionCog class from pollution cog file
from cogs.pollution import PollutionCog
from tests.conftest import build_mock_aiohttp_session


# Define an asynchronous fixture to set up the cog for testing
@pytest_asyncio.fixture
async def cog():
    # Create a new Bot instance with default settings
    bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
    # Return the PollutionCog instance with the bot
    return PollutionCog(bot)


# Define a fixture to create a mock Interaction object
@pytest.fixture
def interaction():
    # Create an AsyncMock for the interaction object
    intr = AsyncMock()
    # Create an AsyncMock for the response object
    intr.response = AsyncMock()
    # Return the mock interaction object
    return intr


def _pollution_payload(city_name='Bangkok', aqi=42):
    return {
        'status': 'ok',
        'data': {
            'aqi': aqi,
            'city': {'name': city_name},
            'time': {'iso': '2024-01-01T12:00:00Z'},
        },
    }


# Mark the test as asynchronous using pytest_asyncio
@pytest.mark.asyncio
# Use patch to mock the aiohttp ClientSession
@patch('cogs.pollution.aiohttp.ClientSession')
@patch('cogs.pollution.DatabaseManager.async_get_cache_entry', return_value=None)
@patch('cogs.pollution.DatabaseManager.async_set_cache_entry')
# Define the test function with mocked dependencies
async def test_valid_city_response(mock_set_cache, mock_get_cache, mock_session_class, cog, interaction):
    build_mock_aiohttp_session(mock_session_class, _pollution_payload())

    await cog.pollution_command.callback(cog, interaction, city="Bangkok")

    # Assert that send_message was called exactly once
    interaction.response.send_message.assert_awaited_once()
    # Get the arguments passed to send_message
    args, _ = interaction.response.send_message.call_args
    # Assert that the response contains the expected AQI symbol
    assert "🟢" in args[0]
    # Assert that the response contains the coconut reference
    assert "vacuum sealed coconut" in args[0]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'channel_name,passed_city,expected_cache_key',
    [
        ('chiang-mai', None, 'pollution:chiang mai'),
        ('other', None, 'pollution:bangkok'),
        ('chiang-mai', 'Phuket', 'pollution:phuket'),
    ],
    ids=['channel-default', 'unmapped-channel-fallback', 'explicit-override'],
)
@patch('cogs.pollution.aiohttp.ClientSession')
@patch('cogs.pollution.DatabaseManager.async_get_cache_entry', return_value=None)
@patch('cogs.pollution.DatabaseManager.async_set_cache_entry')
async def test_city_resolution(
    mock_set_cache, mock_get_cache, mock_session_class,
    cog, interaction, channel_name, passed_city, expected_cache_key,
):
    build_mock_aiohttp_session(mock_session_class, _pollution_payload())

    interaction.channel = MagicMock()
    interaction.channel.name = channel_name

    await cog.pollution_command.callback(cog, interaction, city=passed_city)

    assert mock_set_cache.call_args.args[0] == expected_cache_key
