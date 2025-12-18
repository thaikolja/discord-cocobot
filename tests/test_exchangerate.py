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

# Import patch, AsyncMock, and MagicMock for mocking in tests
from unittest.mock import AsyncMock, MagicMock, patch

# Import discord library for Discord bot interactions
import discord

# Import the pytest framework for testing
import pytest

# Import pytest-asyncio for testing asynchronous code
import pytest_asyncio

# Import the ExchangerateCog class from the cogs module
from cogs.exchangerate import ExchangerateCog


# Define a fixture for creating an instance of the ExchangerateCog
@pytest_asyncio.fixture
async def cog(mock_bot):
    # Add the ExchangerateCog to the mock bot instance
    await mock_bot.add_cog(ExchangerateCog(mock_bot))

    # Return the ExchangerateCog instance from the bot
    return mock_bot.get_cog('ExchangerateCog')


# Define a fixture for creating a mock interaction object
@pytest.fixture
def interaction():
    # Create an AsyncMock object that simulates a Discord interaction
    intr = AsyncMock(spec=discord.Interaction)

    # Create a mock response attribute for the interaction
    intr.response = AsyncMock()

    # Return the mock interaction object
    return intr


# Mark this function as an asynchronous test case
@pytest.mark.asyncio
# Patch the aiohttp.ClientSession to mock API calls
@patch('cogs.exchangerate.aiohttp.ClientSession')
async def test_valid_conversion(mock_session_class, cog, interaction):
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
            'meta': {'last_updated_at': '2024-01-01T12:00:00Z'},
            'data': {'THB': {'value': 35.0}},
        }
    )

    # Set up the response as an async context manager (for "async with session.get() as response:")
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    # Set up session.get to return the response object (not a coroutine)
    # When you do "async with session.get(url) as response:", Python calls session.get(url) which should return
    # an object that can be used in an async context manager
    mock_session.get = MagicMock(return_value=mock_response)

    # Set the mock session class to return our mock session
    mock_session_class.return_value = mock_session

    # Access the command's callback dynamically
    command = cog.bot.tree.get_command("exchangerate")
    callback = command.callback

    # Call the exchangerate_command method directly with test parameters
    await callback(cog, interaction, from_currency="USD", to_currency="THB", amount=100)

    # Assert that the send_message method was called once
    interaction.response.send_message.assert_awaited_once()

    # Get the arguments passed to the send_message method
    args, _ = interaction.response.send_message.call_args

    # Check if the response contains the expected amount and currency
    assert "💰 `100` **USD**" in args[0]

    # Check if the response contains the converted value
    assert "3500.0" in args[0]


# Mark this function as an asynchronous test case
@pytest.mark.asyncio
async def test_invalid_currency_length(cog, interaction):
    # Access the command's callback dynamically
    command = cog.bot.tree.get_command("exchangerate")
    callback = command.callback

    # Test the command with invalid currency codes (length not equal to 3)
    await callback(cog, interaction, from_currency="US", to_currency="TH")

    # Assert that the send_message method was called once
    interaction.response.send_message.assert_awaited_once()

    # Check if the response contains the expected error message for invalid currency codes
    assert "Invalid currency codes" in interaction.response.send_message.call_args[0][0]


# Mark this function as an asynchronous test case
@pytest.mark.asyncio
# Patch the aiohttp.ClientSession to mock API calls
@patch('cogs.exchangerate.aiohttp.ClientSession')
async def test_nonexistent_target_currency(mock_session_class, cog, interaction):
    # Create mock session and response objects
    mock_session = MagicMock()
    mock_response = MagicMock()

    # Set up the async context managers
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    # Set up the response with missing target currency
    mock_response.status = 200
    mock_response.json = AsyncMock(
        return_value={
            'meta': {'last_updated_at': '2024-01-01T12:00:00Z'},
            'data': {
                # 'THB' is intentionally missing to simulate the error case
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

    # Access the command's callback dynamically
    command = cog.bot.tree.get_command("exchangerate")
    callback = command.callback

    # Call the exchangerate_command method with the test parameters
    await callback(cog, interaction, from_currency="USD", to_currency="THB", amount=100)

    # Assert that the send_message method was called once
    interaction.response.send_message.assert_awaited_once()

    # Check if the response contains the expected error message for invalid target currency
    assert (
        "Invalid target currency" in interaction.response.send_message.call_args[0][0]
    )


# Mark this function as an asynchronous test case
@pytest.mark.asyncio
# Patch the aiohttp.ClientSession to mock API calls
@patch('cogs.exchangerate.aiohttp.ClientSession')
async def test_api_failure(mock_session_class, cog, interaction):
    # Create mock session and response objects
    mock_session = MagicMock()
    mock_response = MagicMock()

    # Set up the async context managers
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    # Set up the response to indicate a failed request
    mock_response.status = 500
    mock_response.json = AsyncMock(return_value={})

    # Set up the response as an async context manager
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    # Set up session.get to return the response object
    mock_session.get = MagicMock(return_value=mock_response)

    # Set the mock session class to return our mock session
    mock_session_class.return_value = mock_session

    # Access the command's callback dynamically
    command = cog.bot.tree.get_command("exchangerate")
    callback = command.callback

    # Call the exchangerate_command method with the test parameters
    await callback(cog, interaction, from_currency="USD", to_currency="THB", amount=100)

    # Assert that the send_message method was called once
    interaction.response.send_message.assert_awaited_once()

    # Check if the response contains the expected error message for API failure
    assert "Couldn't convert" in interaction.response.send_message.call_args[0][0]
