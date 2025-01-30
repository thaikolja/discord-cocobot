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

# Import pytest for test framework functionality
import pytest

# Import pytest_asyncio for handling async tests
import pytest_asyncio

# Import mocking utilities from unittest.mock
from unittest.mock import patch, AsyncMock

# Import discord library for Discord-related functionality
import discord

# Import commands extension from discord.ext
from discord.ext import commands

# Import TranslateCog class from translate cog file
from cogs.translate import TranslateCog

# Import ERROR_MESSAGE constant from config
from config.config import ERROR_MESSAGE


# Fixture to create and return a TranslateCog instance with a bot
@pytest_asyncio.fixture
async def cog():
	# Create a new Bot instance with default settings
	bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
	# Return the TranslateCog instance
	return TranslateCog(bot)


# Fixture to create a mock Interaction object
@pytest.fixture
def interaction():
	# Create an AsyncMock for the interaction object
	intr = AsyncMock()
	# Create an AsyncMock for the response object
	intr.response = AsyncMock()
	# Return the mocked interaction object
	return intr


# Mark the test as async and patch the UseAI.prompt method
@pytest.mark.asyncio
@patch('utils.helpers.UseAI.prompt')
async def test_successful_translation(mock_prompt, cog, interaction):
	# Set up the mock to return "Hello world"
	mock_prompt.return_value = "Hello world"
	# Call the translate command with test parameters
	await cog.translate_command.callback(
		cog,
		interaction,
		text="สวัสดีชาวโลก",
		from_language="Thai",
		to_language="English"
	)
	# Verify response was sent once with expected message
	interaction.response.send_message.assert_awaited_once_with("🇹🇭 Hello world")
	# Verify prompt was called with correct translation request
	mock_prompt.assert_called_once_with(
		'Translate the text "สวัสดีชาวโลก" from Thai to English. Keep the tone and meaning of the original text.'
	)


# Mark the test as async and patch the UseAI.prompt method
@pytest.mark.asyncio
@patch('utils.helpers.UseAI.prompt')
async def test_empty_translation_response(mock_prompt, cog, interaction):
	# Set up the mock to return an empty string
	mock_prompt.return_value = ""
	# Call the translate command with test parameters
	await cog.translate_command.callback(
		cog,
		interaction,
		text="Test",
		from_language="English",
		to_language="Thai"
	)
	# Verify response was sent once
	assert interaction.response.send_message.await_count == 1
	# Verify error message was sent
	interaction.response.send_message.assert_awaited_once_with(ERROR_MESSAGE)


# Mark the test as async and patch the UseAI.prompt method
@pytest.mark.asyncio
@patch('utils.helpers.UseAI.prompt')
async def test_translation_with_default_params(mock_prompt, cog, interaction):
	# Set up the mock to return "สวัสดี"
	mock_prompt.return_value = "สวัสดี"
	# Call the translate command with default parameters
	await cog.translate_command.callback(cog, interaction, text="Hello")
	# Verify prompt was called with correct translation request
	mock_prompt.assert_called_once_with(
		'Translate the text "Hello" from Thai to English. Keep the tone and meaning of the original text.'
	)
	# Verify response was sent with expected message
	interaction.response.send_message.assert_awaited_once_with("🇹🇭 สวัสดี")


# Mark the test as async and patch the UseAI.prompt method
@pytest.mark.asyncio
@patch('utils.helpers.UseAI.prompt')
async def test_translation_with_special_characters(mock_prompt, cog, interaction):
	# Set up the mock to return "¿Cómo estás?"
	mock_prompt.return_value = "¿Cómo estás?"
	# Call the translate command with special characters
	await cog.translate_command.callback(
		cog,
		interaction,
		text="How are you?",
		from_language="English",
		to_language="Spanish"
	)
	# Verify prompt was called with correct translation request
	mock_prompt.assert_called_once_with(
		'Translate the text "How are you?" from English to Spanish. Keep the tone and meaning of the original text.'
	)
	# Verify response was sent with expected message
	interaction.response.send_message.assert_awaited_once_with("🇹🇭 ¿Cómo estás?")
