# Copyright (C) 2025 by Kolja Nolte
# kolja.nolte@gmail.com
# https://gitlab.com/thaikolja/discord-cocobot
#
# This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
# You are free to use, share, and adapt this work for non-commercial purposes, provided that you:
# - Give appropriate credit to the original author.
# - Provide a link to the license.
# - Distribute your contributions under the same license.
#
# For more information, visit: https://creativecommons.org/licenses/by-nc-sa/4.0/
#
# Author:    Kolja Nolte
# Email:     kolja.nolte@gmail.com
# License:   CC BY-NC-SA 4.0
# Date:      2014-2025
# Package:   Thailand Discord

# Import pytest for testing functionality
import pytest

# Import pytest_asyncio for handling async tests
import pytest_asyncio

# Import mocking utilities from unittest.mock
from unittest.mock import patch, MagicMock, AsyncMock

# Import requests library for HTTP requests
import requests

# Import Discord.py library for Discord bot functionality
import discord

# Import commands extension from Discord.py
from discord.ext import commands

# Import the LocateCog class from cogs.locate module
from cogs.locate import LocateCog

# Import the error message from config
from config.config import ERROR_MESSAGE


# Fixture to create and configure the bot with LocateCog
@pytest_asyncio.fixture
async def cog():
	# Create a new Discord bot with default settings
	bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

	# Add the LocateCog to the bot
	await bot.add_cog(LocateCog(bot))

	# Return the loaded cog instance
	return bot.get_cog('LocateCog')


# Fixture to create a mock Discord interaction
@pytest.fixture
def interaction():
	# Create a mock Interaction object with response capabilities
	intr = MagicMock(spec=discord.Interaction)

	# Mock the response object and its send_message method
	intr.response = MagicMock()
	intr.response.send_message = AsyncMock()

	# Return the mocked interaction object
	return intr


# Test case for valid location response handling
@pytest.mark.asyncio
@patch('cogs.locate.requests.get')
async def test_valid_location_response(mock_get, cog, interaction):
	# Create a mock response object with successful status code
	mock_response = MagicMock()
	mock_response.status_code = 200

	# Set up mock JSON response with test data
	mock_response.json.return_value = {
		'results': [{
			'formatted_address': 'Test Address',
			'geometry':          {
				'location': {
					'lat': 13.7563,
					'lng': 100.5018
				}
			}
		}]
	}

	# Configure the mock to return our mock response
	mock_get.return_value = mock_response

	# Execute the locate command with test parameters
	await cog.locate_command.callback(cog, interaction, location="Test Location", city="Test City")

	# Assert that the response was sent with the expected message
	interaction.response.send_message.assert_awaited_once_with(
		"📍 \"**Test Location**\" is located at **Test Address**.\n"
		"Here's a link to a map, you lazy ass: https://www.google.com/maps/place/13.7563,100.5018"
	)


# Test case for handling invalid location responses
@pytest.mark.asyncio
@patch('cogs.locate.requests.get')
async def test_invalid_location_response(mock_get, cog, interaction):
	# Create a mock response object with empty results
	mock_response = MagicMock()
	mock_response.status_code = 200

	# Set up mock JSON response with empty results array
	mock_response.json.return_value = {
		'results': []
	}

	# Configure the mock to return our mock response
	mock_get.return_value = mock_response

	# Execute the locate command with invalid parameters
	await cog.locate_command.callback(cog, interaction, location="Nowhere", city="Nowhere")

	# Assert that the response was sent with the expected error message
	interaction.response.send_message.assert_awaited_once_with(
		f"{ERROR_MESSAGE} Are you dumb? Or am I? \"Nowhere\" in Nowhere didn't show up on my radar."
	)


# Test case for handling API errors
@pytest.mark.asyncio
@patch('cogs.locate.requests.get')
async def test_api_error_handling(mock_get, cog, interaction):
	# Create a mock response object with error status code
	mock_response = MagicMock()
	mock_response.status_code = 500

	# Set up mock response text
	mock_response.text = "Internal Server Error"

	# Configure the mock to return our mock response
	mock_get.return_value = mock_response

	# Execute the locate command with test parameters
	await cog.locate_command.callback(cog, interaction, location="Test", city="Test")

	# Assert that the response was sent with the expected error message
	interaction.response.send_message.assert_awaited_once_with(
		f"{ERROR_MESSAGE} Try again some other time, I guess?"
	)


# Test case for handling request timeouts
@pytest.mark.asyncio
@patch('cogs.locate.requests.get')
async def test_timeout_error(mock_get, cog, interaction):
	# Configure the mock to raise a Timeout exception
	mock_get.side_effect = requests.exceptions.Timeout()

	# Execute the locate command with test parameters
	await cog.locate_command.callback(cog, interaction, location="Test", city="Test")

	# Assert that the response was sent with the expected timeout message
	interaction.response.send_message.assert_awaited_once_with(
		f"{ERROR_MESSAGE} This is all taking too long, I'm out."
	)
