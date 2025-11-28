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


# Mark the test as asynchronous using pytest_asyncio
@pytest.mark.asyncio
# Use patch to mock the aiohttp ClientSession
@patch('cogs.pollution.aiohttp.ClientSession')
# Define the test function with mocked dependencies
async def test_valid_city_response(mock_session_class, cog, interaction):
    # Create mock session and response objects
    mock_session = MagicMock()
    mock_response = MagicMock()

    # Set up the async context managers
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    # Set up the response
    mock_response.status = 200
    mock_response.json = AsyncMock(
        return_value={
            'status': 'ok',
            'data': {
                'aqi': 42,
                'city': {'name': 'Bangkok'},
                'time': {'iso': '2024-01-01T12:00:00Z'},
            },
        }
    )

    # Set up the response as an async context manager
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    # Set up session.get to return the response object
    mock_session.get = MagicMock(return_value=mock_response)

    # Set the mock session class to return our mock session
    mock_session_class.return_value = mock_session

    # Call the command's callback directly with test parameters
    await cog.pollution_command.callback(cog, interaction, city="Bangkok")

    # Assert that send_message was called exactly once
    interaction.response.send_message.assert_awaited_once()
    # Get the arguments passed to send_message
    args, _ = interaction.response.send_message.call_args
    # Assert that the response contains the expected AQI symbol
    assert "🟢" in args[0]
    # Assert that the response contains the coconut reference
    assert "vacuum sealed coconut" in args[0]
