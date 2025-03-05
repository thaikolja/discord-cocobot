#  Copyright (C) 2025 by Kolja Nolte
#  kolja.nolte@gmail.com
#  https://gitlab.com/thaikolja/discord-cocobot
#
#  This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
#  You are free to use, share, and adapt this work for non-commercial purposes, provided that you:
#  - Give appropriate credit to the original author.
#  - Provide a link to the license.
#  - Distribute your contributions under the same license.
#
#  For more information, visit: https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#  Author:    Kolja Nolte
#  Email:     kolja.nolte@gmail.com
#  License:   CC BY-NC-SA 4.0
#  Date:      2014-2025
#  Package:   Thailand Discord

# Import the discord library for interacting with Discord
import discord

# Import pytest for unit testing functionality
import pytest

# Import pytest_asyncio for asynchronous test support
import pytest_asyncio

# Import mocking utilities from unittest.mock
from unittest.mock import patch, AsyncMock, MagicMock

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
# Use patch to mock the requests.get method
@patch('cogs.pollution.requests.get')
# Define the test function with mocked dependencies
async def test_valid_city_response(mock_get, cog, interaction):
	# Create a mock response object
	mock_response = MagicMock()
	# Set the response.ok property to True
	mock_response.ok = True
	# Define the mock JSON response data
	mock_response.json.return_value = {
		'status': 'ok',
		'data':   {
			'aqi':  42,
			'city': {
				'name': 'Bangkok'
			},
			'time': {
				'iso': '2024-01-01T12:00:00Z'
			}
		}
	}
	# Set the mock_get return value to the mock_response
	mock_get.return_value = mock_response

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
