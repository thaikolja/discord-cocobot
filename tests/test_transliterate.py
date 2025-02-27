# test_transliterate.py
import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock
import discord
from discord.ext import commands
from cogs.transliterate import Transliterate
from config.config import ERROR_MESSAGE


@pytest_asyncio.fixture
async def cog():
	bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
	return Transliterate(bot)


@pytest.fixture
def interaction():
	intr = AsyncMock()
	intr.response = AsyncMock()
	intr.followup = AsyncMock()
	return intr


def validate_transliteration(output: str) -> bool:
	"""Basic validation of transliteration format"""
	return any(c in output for c in ["-", " ", "à", "è", "ù"]) if output else False


@pytest.mark.asyncio
@patch('utils.helpers.UseAI.prompt')
async def test_transliteration_flow(mock_prompt, cog, interaction):
	mock_prompt.return_value = "sà-wàt-dii"

	await cog.transliterate_command.callback(
		cog,
		interaction,
		text="สวัสดี"
	)

	interaction.response.defer.assert_awaited_once()
	interaction.followup.send.assert_awaited_once()

	response_text = interaction.followup.send.call_args[0][0]
	assert validate_transliteration(response_text)


@pytest.mark.asyncio
@patch('utils.helpers.UseAI.prompt')
async def test_error_handling(mock_prompt, cog, interaction):
	mock_prompt.side_effect = Exception("API Error")

	await cog.transliterate_command.callback(
		cog,
		interaction,
		text="ทดสอบ"
	)

	interaction.followup.send.assert_awaited_once_with(
		f"✍️ {ERROR_MESSAGE}"
	)


@pytest.mark.asyncio
@patch('utils.helpers.UseAI.prompt')
async def test_prompt_construction(mock_prompt, cog, interaction):
	test_cases = [
		("สวัสดี", "สวัสดี"),
		("A", "A"),
		("X" * 500, "X" * 500)
	]

	for input_text, expected in test_cases:
		mock_prompt.reset_mock()
		await cog.transliterate_command.callback(cog, interaction, text=input_text)

		args, kwargs = mock_prompt.call_args
		assert f"'{expected}'" in args[0]
		# Verify default strict mode
		assert len(args) >= 2 or kwargs.get('strict', True) is True


@pytest.mark.asyncio
@patch('utils.helpers.UseAI.prompt')
async def test_empty_response_handling(mock_prompt, cog, interaction):
	mock_prompt.return_value = ""

	await cog.transliterate_command.callback(
		cog,
		interaction,
		text="ทดสอบ"
	)

	interaction.followup.send.assert_awaited_once_with(f"✍️ {ERROR_MESSAGE}")
