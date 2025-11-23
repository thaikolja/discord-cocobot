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

# Import pytest for testing framework
import pytest

# Import pytest_asyncio for asynchronous test support
import pytest_asyncio

# Import patch, AsyncMock, and MagicMock for mocking in tests
from unittest.mock import patch, AsyncMock, MagicMock

# Import aiohttp for mocking async HTTP requests
import aiohttp

# Import discord library for Discord bot functionality
import discord

# Import commands from discord.ext for creating bot commands
from discord.ext import commands

# Import TimeCog from the cogs module for testing time-related commands
from cogs.time import TimeCog

# Import ERROR_MESSAGE constant from the config module for error handling
from config.config import ERROR_MESSAGE


# Define a fixture for creating an instance of TimeCog
@pytest_asyncio.fixture
async def cog():
	# Create a new bot instance with a command prefix and default intents
	bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

	# Create and return an instance of TimeCog initialized with the bot
	cog_instance = TimeCog(bot)
	yield cog_instance
	
	# Cleanup: close the session after tests
	await cog_instance.session.close()


# Define a fixture for mocking interaction responses
@pytest.fixture
def interaction():
	# Create an asynchronous mock for interaction
	intr = AsyncMock()

	# Create a mock response attribute for the interaction
	intr.response = AsyncMock()

	# Return the mocked interaction
	return intr


# Mark the following function as an asyncio test
@pytest.mark.asyncio
async def test_valid_time_response(cog, interaction):
	# Create a mock response object for a successful API call
	mock_response = AsyncMock()

	# Set the response status to OK
	mock_response.raise_for_status = MagicMock()

	# Define the JSON data to be returned by the mock response
	mock_response.json = AsyncMock(return_value={
		'geo':       {
			'country': 'Thailand',
			'city':    'Bangkok'
		},
		'date_time': '2024-01-01 12:00:00'
	})

	# Mock the session.get to return a context manager
	mock_cm = MagicMock()
	mock_cm.__aenter__ = AsyncMock(return_value=mock_response)
	mock_cm.__aexit__ = AsyncMock(return_value=None)
	
	with patch.object(cog.session, 'get', return_value=mock_cm):
		# Execute the time command with a specified location
		await cog.time_command.callback(cog, interaction, location="Bangkok")

		# Verify that the send_message method was called once
		interaction.response.send_message.assert_awaited_once()

		# Get the arguments passed to the send_message method
		args, _ = interaction.response.send_message.call_args

		# Assert that the response contains the expected city information
		assert "🕓 In **Bangkok**" in args[0]

		# Assert that the response contains the expected time
		assert "12:00" in args[0]


# Mark the following function as an asyncio test
@pytest.mark.asyncio
async def test_invalid_location(cog, interaction):
	# Create a mock response object for a failed API call
	mock_response = AsyncMock()
	mock_response.raise_for_status = MagicMock(side_effect=aiohttp.ClientError("API Error"))

	# Mock the session.get to return a context manager
	mock_cm = MagicMock()
	mock_cm.__aenter__ = AsyncMock(return_value=mock_response)
	mock_cm.__aexit__ = AsyncMock(return_value=None)
	
	with patch.object(cog.session, 'get', return_value=mock_cm):
		# Execute the time command with an invalid location
		await cog.time_command.callback(cog, interaction, location="Nowhere")

		# Verify that the send_message method was called once with the expected error message
		interaction.response.send_message.assert_awaited_once_with(
			f"{ERROR_MESSAGE} Couldn't find time for `Nowhere`. Maybe it's in a coconut timezone?"
		)


# Mark the following function as an asyncio test
@pytest.mark.asyncio
async def test_api_error_handling(cog, interaction):
	# Simulate an API error by raising a ClientError
	mock_cm = MagicMock()
	mock_cm.__aenter__ = AsyncMock(side_effect=aiohttp.ClientError("Connection error"))
	mock_cm.__aexit__ = AsyncMock(return_value=None)
	
	with patch.object(cog.session, 'get', return_value=mock_cm):
		# Execute the time command with a valid location
		await cog.time_command.callback(cog, interaction, location="Bangkok")

		# Verify that the send_message method was called once with the expected error message
		interaction.response.send_message.assert_awaited_once_with(
			f"{ERROR_MESSAGE} Couldn't find time for `Bangkok`. Maybe it's in a coconut timezone?"
		)


# Mark the following function as an asyncio test
@pytest.mark.asyncio
async def test_default_location(cog, interaction):
	# Create a mock response object for a successful API call
	mock_response = AsyncMock()
	mock_response.raise_for_status = MagicMock()

	# Define the JSON data to be returned by the mock response
	mock_response.json = AsyncMock(return_value={
		'geo':       {
			'country': 'Thailand',
			'city':    'Bangkok'
		},
		'date_time': '2024-01-01 12:00:00'
	})

	# Mock the session.get to return a context manager
	mock_cm = MagicMock()
	mock_cm.__aenter__ = AsyncMock(return_value=mock_response)
	mock_cm.__aexit__ = AsyncMock(return_value=None)
	
	with patch.object(cog.session, 'get', return_value=mock_cm):
		# Execute the time command without specifying a location (default)
		await cog.time_command.callback(cog, interaction)

		# Verify that the send_message method was called once
		interaction.response.send_message.assert_awaited_once()

		# Get the arguments passed to the send_message method
		args, _ = interaction.response.send_message.call_args

		# Assert that the response contains the expected city information
		assert "🕓 In **Bangkok**" in args[0]

		# Assert that the response contains the expected time
		assert "12:00" in args[0]
