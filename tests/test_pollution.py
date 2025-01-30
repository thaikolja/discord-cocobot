# tests/test_pollution.py
import discord
import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import requests
from discord.ext import commands
from cogs.pollution import PollutionCog


@pytest_asyncio.fixture
async def cog():
	bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
	return PollutionCog(bot)


@pytest.fixture
def interaction():
	intr = AsyncMock()
	intr.response = AsyncMock()
	return intr


@pytest.mark.asyncio
@patch('cogs.pollution.requests.get')
async def test_valid_city_response(mock_get, cog, interaction):
	mock_response = MagicMock()
	mock_response.ok = True
	mock_response.json.return_value = {
		'status': 'ok',
		'data':   {
			'aqi': 42,
			'city': {
				'name': 'Bangkok'
			},
			'time': {
				'iso': '2024-01-01T12:00:00Z'
			}
		}
	}
	mock_get.return_value = mock_response

	# Call the command's callback directly
	await cog.pollution_command.callback(cog, interaction, city="Bangkok")

	interaction.response.send_message.assert_awaited_once()
	args, _ = interaction.response.send_message.call_args
	assert "🟢" in args[0]
	assert "vacuum sealed coconut" in args[0]
