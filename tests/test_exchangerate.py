# tests/test_exchangerate.py
import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import discord
from discord.ext import commands
from cogs.exchangerate import ExchangerateCog


@pytest_asyncio.fixture
async def cog():
	bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
	await bot.add_cog(ExchangerateCog(bot))
	return bot.get_cog('ExchangerateCog')


@pytest.fixture
def interaction():
	intr = AsyncMock(spec=discord.Interaction)
	intr.response = AsyncMock()
	return intr


@pytest.mark.asyncio
@patch('cogs.exchangerate.requests.get')
async def test_valid_conversion(mock_get, cog, interaction):
	mock_response = MagicMock()
	mock_response.ok = True
	mock_response.json.return_value = {
		'meta': {
			'last_updated_at': '2024-01-01T12:00:00Z'
		},
		'data': {
			'THB': {
				'value': 35.0
			}
		}
	}
	mock_get.return_value = mock_response

	# Call the callback method directly, passing 'cog' as 'self'
	await cog.exchangerate_command.callback(cog, interaction, from_currency="USD", to_currency="THB", amount=100)

	interaction.response.send_message.assert_awaited_once()
	args, _ = interaction.response.send_message.call_args
	assert "💰 `100` **USD**" in args[0]
	assert "3500.0" in args[0]


@pytest.mark.asyncio
@patch('cogs.exchangerate.requests.get')
async def test_invalid_currency_length(mock_get, cog, interaction):
	# Test with invalid currency codes (length != 3)
	await cog.exchangerate_command.callback(cog, interaction, from_currency="US", to_currency="TH")
	interaction.response.send_message.assert_awaited_once()
	assert "Invalid currency codes" in interaction.response.send_message.call_args[0][0]


@pytest.mark.asyncio
@patch('cogs.exchangerate.requests.get')
async def test_nonexistent_target_currency(mock_get, cog, interaction):
	# Mock a successful API response but without the target currency
	mock_response = MagicMock()
	mock_response.ok = True
	mock_response.json.return_value = {
		'meta': {
			'last_updated_at': '2024-01-01T12:00:00Z'
		},
		'data': {
			# 'THB' is missing
		}
	}
	mock_get.return_value = mock_response

	await cog.exchangerate_command.callback(cog, interaction, from_currency="USD", to_currency="THB", amount=100)

	interaction.response.send_message.assert_awaited_once()
	assert "Invalid target currency" in interaction.response.send_message.call_args[0][0]


@pytest.mark.asyncio
@patch('cogs.exchangerate.requests.get')
async def test_api_failure(mock_get, cog, interaction):
	# Mock a failed API response
	mock_response = MagicMock()
	mock_response.ok = False
	mock_get.return_value = mock_response

	await cog.exchangerate_command.callback(cog, interaction, from_currency="USD", to_currency="THB", amount=100)

	interaction.response.send_message.assert_awaited_once()
	assert "Couldn't convert" in interaction.response.send_message.call_args[0][0]
