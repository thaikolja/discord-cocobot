# tests/test_time.py
import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import requests
import discord
from discord.ext import commands
from cogs.time import TimeCog
from config.config import ERROR_MESSAGE


@pytest_asyncio.fixture
async def cog():
	bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
	return TimeCog(bot)


@pytest.fixture
def interaction():
	intr = AsyncMock()
	intr.response = AsyncMock()
	return intr


@pytest.mark.asyncio
@patch('cogs.time.requests.get')
async def test_valid_time_response(mock_get, cog, interaction):
	# Mock API response
	mock_response = MagicMock()
	mock_response.ok = True
	mock_response.json.return_value = {
		'geo':       {
			'country': 'Thailand',
			'city':    'Bangkok'
		},
		'date_time': '2024-01-01 12:00:00'
	}
	mock_get.return_value = mock_response

	# Execute command
	await cog.time_command.callback(cog, interaction, location="Bangkok")

	# Verify response
	interaction.response.send_message.assert_awaited_once()
	args, _ = interaction.response.send_message.call_args
	assert "🕓 In **Bangkok**" in args[0]
	assert "12:00" in args[0]


@pytest.mark.asyncio
@patch('cogs.time.requests.get')
async def test_invalid_location(mock_get, cog, interaction):
	# Mock API failure
	mock_response = MagicMock()
	mock_response.ok = False
	mock_get.return_value = mock_response

	# Execute command
	await cog.time_command.callback(cog, interaction, location="Nowhere")

	# Verify error message
	interaction.response.send_message.assert_awaited_once_with(
		f"{ERROR_MESSAGE} Couldn't find time for `Nowhere`. Maybe it's in a coconut timezone?"
	)


@pytest.mark.asyncio
@patch('cogs.time.requests.get')
async def test_api_error_handling(mock_get, cog, interaction):
	# Simulate API error
	mock_get.side_effect = requests.exceptions.RequestException()

	# Execute command
	await cog.time_command.callback(cog, interaction, location="Bangkok")

	# Verify error message
	interaction.response.send_message.assert_awaited_once_with(
		f"{ERROR_MESSAGE} Couldn't find time for `Bangkok`. Maybe it's in a coconut timezone?"
	)


@pytest.mark.asyncio
@patch('cogs.time.requests.get')
async def test_default_location(mock_get, cog, interaction):
	# Mock API response
	mock_response = MagicMock()
	mock_response.ok = True
	mock_response.json.return_value = {
		'geo':       {
			'country': 'Thailand',
			'city':    'Bangkok'
		},
		'date_time': '2024-01-01 12:00:00'
	}
	mock_get.return_value = mock_response

	# Execute command with default location
	await cog.time_command.callback(cog, interaction)

	# Verify response
	interaction.response.send_message.assert_awaited_once()
	args, _ = interaction.response.send_message.call_args
	assert "🕓 In **Bangkok**" in args[0]
	assert "12:00" in args[0]
