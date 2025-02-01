# test_translate.py
import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock
import discord
from discord.ext import commands
from cogs.translate import TranslateCog
from config.config import ERROR_MESSAGE
import openai


@pytest_asyncio.fixture
async def cog():
	bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
	return TranslateCog(bot)


@pytest.fixture
def interaction():
	intr = AsyncMock()
	intr.response = AsyncMock()
	intr.followup = AsyncMock()
	return intr


@pytest.mark.asyncio
@patch('utils.helpers.UseAI.prompt')
async def test_successful_translation(mock_prompt, cog, interaction):
	mock_prompt.return_value = "Hello world"
	await cog.translate_command.callback(
		cog,
		interaction,
		text="สวัสดีชาวโลก",
		from_language="Thai",
		to_language="English"
	)
	interaction.response.defer.assert_awaited_once()
	interaction.followup.send.assert_awaited_once_with("📚️ Hello world")
	mock_prompt.assert_called_once_with(
		'Translate the text "สวัสดีชาวโลก" from Thai to English. Keep the tone and meaning of the original text.'
	)


@pytest.mark.asyncio
@patch('utils.helpers.UseAI.prompt')
async def test_empty_translation_response(mock_prompt, cog, interaction):
	mock_prompt.return_value = ""
	await cog.translate_command.callback(
		cog,
		interaction,
		text="Test",
		from_language="English",
		to_language="Thai"
	)
	interaction.response.defer.assert_awaited_once()
	interaction.followup.send.assert_awaited_once_with(ERROR_MESSAGE)


@pytest.mark.asyncio
@patch('utils.helpers.UseAI.prompt')
async def test_translation_with_default_params(mock_prompt, cog, interaction):
	mock_prompt.return_value = "สวัสดี"
	await cog.translate_command.callback(cog, interaction, text="Hello")
	interaction.response.defer.assert_awaited_once()
	interaction.followup.send.assert_awaited_once_with("📚️ สวัสดี")
	mock_prompt.assert_called_once_with(
		'Translate the text "Hello" from Thai to English. Keep the tone and meaning of the original text.'
	)


@pytest.mark.asyncio
@patch('utils.helpers.UseAI.prompt')
async def test_translation_with_special_characters(mock_prompt, cog, interaction):
	mock_prompt.return_value = "¿Cómo estás?"
	await cog.translate_command.callback(
		cog,
		interaction,
		text="How are you?",
		from_language="English",
		to_language="Spanish"
	)
	interaction.response.defer.assert_awaited_once()
	interaction.followup.send.assert_awaited_once_with("📚️ ¿Cómo estás?")
	mock_prompt.assert_called_once_with(
		'Translate the text "How are you?" from English to Spanish. Keep the tone and meaning of the original text.'
	)


@pytest.mark.asyncio
@patch('utils.helpers.UseAI.prompt')
async def test_translation_timeout(mock_prompt, cog, interaction):
	mock_prompt.side_effect = openai.APITimeoutError("Request timed out")
	await cog.translate_command.callback(
		cog,
		interaction,
		text="Test",
		from_language="English",
		to_language="Thai"
	)
	interaction.response.defer.assert_awaited_once()
	interaction.followup.send.assert_awaited_once_with("⏰ Request timed out after 10 seconds")


@pytest.mark.asyncio
@patch('utils.helpers.UseAI.prompt')
async def test_translation_general_error(mock_prompt, cog, interaction):
	mock_prompt.side_effect = Exception("API failure")
	await cog.translate_command.callback(
		cog,
		interaction,
		text="Test",
		from_language="English",
		to_language="Thai"
	)
	interaction.response.defer.assert_awaited_once()
	interaction.followup.send.assert_awaited_once_with("❌ Error: API failure")
