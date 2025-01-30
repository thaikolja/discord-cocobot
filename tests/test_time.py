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

# Import pytest for testing framework
import pytest

# Import pytest_asyncio for asynchronous test support
import pytest_asyncio

# Import patch, AsyncMock, and MagicMock for mocking in tests
from unittest.mock import patch, AsyncMock, MagicMock

# Import requests library for making HTTP requests
import requests

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

	# Return an instance of TimeCog initialized with the bot
	return TimeCog(bot)


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
# Patch the requests.get method in the cogs.time module
@patch('cogs.time.requests.get')
async def test_valid_time_response(mock_get, cog, interaction):
	# Create a mock response object for a successful API call
	mock_response = MagicMock()

	# Set the response status to OK
	mock_response.ok = True

	# Define the JSON data to be returned by the mock response
	mock_response.json.return_value = {
		'geo':       {
			'country': 'Thailand',
			'city':    'Bangkok'
		},
		'date_time': '2024-01-01 12:00:00'
	}

	# Set the return value of the mocked requests.get to the mock response
	mock_get.return_value = mock_response

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
# Patch the requests.get method in the cogs.time module
@patch('cogs.time.requests.get')
async def test_invalid_location(mock_get, cog, interaction):
	# Create a mock response object for a failed API call
	mock_response = MagicMock()

	# Set the response status to not OK
	mock_response.ok = False

	# Set the return value of the mocked requests.get to the mock response
	mock_get.return_value = mock_response

	# Execute the time command with an invalid location
	await cog.time_command.callback(cog, interaction, location="Nowhere")

	# Verify that the send_message method was called once with the expected error message
	interaction.response.send_message.assert_awaited_once_with(
		f"{ERROR_MESSAGE} Couldn't find time for `Nowhere`. Maybe it's in a coconut timezone?"
	)


# Mark the following function as an asyncio test
@pytest.mark.asyncio
# Patch the requests.get method in the cogs.time module
@patch('cogs.time.requests.get')
async def test_api_error_handling(mock_get, cog, interaction):
	# Simulate an API error by raising a RequestException
	mock_get.side_effect = requests.exceptions.RequestException()

	# Execute the time command with a valid location
	await cog.time_command.callback(cog, interaction, location="Bangkok")

	# Verify that the send_message method was called once with the expected error message
	interaction.response.send_message.assert_awaited_once_with(
		f"{ERROR_MESSAGE} Couldn't find time for `Bangkok`. Maybe it's in a coconut timezone?"
	)


# Mark the following function as an asyncio test
@pytest.mark.asyncio
# Patch the requests.get method in the cogs.time module
@patch('cogs.time.requests.get')
async def test_default_location(mock_get, cog, interaction):
	# Create a mock response object for a successful API call
	mock_response = MagicMock()

	# Set the response status to OK
	mock_response.ok = True

	# Define the JSON data to be returned by the mock response
	mock_response.json.return_value = {
		'geo':       {
			'country': 'Thailand',
			'city':    'Bangkok'
		},
		'date_time': '2024-01-01 12:00:00'
	}

	# Set the return value of the mocked requests.get to the mock response
	mock_get.return_value = mock_response

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
