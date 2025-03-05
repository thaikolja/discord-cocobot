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

# Import pytest framework for testing
import pytest

# Import mocking utilities from unittest.mock
from unittest.mock import patch, AsyncMock

# Import Discord commands extension
from discord.ext import commands

# Import Discord Intents for bot permissions
from discord import Intents

# Import the TranslateCog class from cogs.translate module
from cogs.translate import TranslateCog


# Fixture to create a bot instance with default configuration
@pytest.fixture
def bot():
	# Create a default intents object for the bot
	intents = Intents.default()

	# Initialize and return a new Bot instance with specified prefix and intents
	return commands.Bot(command_prefix="!", intents=intents)


# Fixture to create an instance of TranslateCog with the bot instance
@pytest.fixture
def cog(bot):
	# Initialize and return a new TranslateCog instance with the bot
	return TranslateCog(bot)


# Fixture to create a mock Discord interaction object
@pytest.fixture
def interaction():
	# Return an AsyncMock object to simulate Discord interaction
	return AsyncMock()


# Test case for successful translation with specified languages
@pytest.mark.asyncio
@patch('utils.helpers.UseAI.prompt')
async def test_successful_translation(mock_prompt, cog, interaction):
	# Set up mock response from AI with expected translation
	mock_prompt.return_value = "Hello world"

	# Call the translate command with test parameters
	await cog.translate_command.callback(
		cog,
		interaction,
		text="สวัสดีชาวโลก",
		from_language="Thai",
		to_language="English"
	)

	# Verify interaction response was deferred once
	interaction.response.defer.assert_awaited_once()

	# Verify followup message was sent with translated text
	interaction.followup.send.assert_awaited_once_with("📚️ **Translation:** Hello world")

	# Verify AI prompt was called with correct translation parameters
	mock_prompt.assert_called_once_with(
		'Translate the text "สวัสดีชาวโลก" from Thai to English. Keep the tone and meaning of the original text. Stay accurate.'
	)


# Test case for translation using default parameters
@pytest.mark.asyncio
@patch('utils.helpers.UseAI.prompt')
async def test_translation_with_default_params(mock_prompt, cog, interaction):
	# Set up mock response from AI with expected translation
	mock_prompt.return_value = "สวัสดี"

	# Call the translate command with text only, using default languages
	await cog.translate_command.callback(cog, interaction, text="Hello")

	# Verify interaction response was deferred once
	interaction.response.defer.assert_awaited_once()

	# Verify followup message was sent with translated text
	interaction.followup.send.assert_awaited_once_with("📚️ **Translation:** สวัสดี")

	# Verify AI prompt was called with default translation parameters
	mock_prompt.assert_called_once_with(
		'Translate the text "Hello" from Thai to English. Keep the tone and meaning of the original text. Stay accurate.'
	)


# Test case for translation with special characters
@pytest.mark.asyncio
@patch('utils.helpers.UseAI.prompt')
async def test_translation_with_special_characters(mock_prompt, cog, interaction):
	# Set up mock response from AI with expected translation
	mock_prompt.return_value = "¿Cómo estás?"

	# Call the translate command with text and language parameters
	await cog.translate_command.callback(
		cog,
		interaction,
		text="How are you?",
		from_language="English",
		to_language="Spanish"
	)

	# Verify interaction response was deferred once
	interaction.response.defer.assert_awaited_once()

	# Verify followup message was sent with translated text
	interaction.followup.send.assert_awaited_once_with("📚️ **Translation:** ¿Cómo estás?")

	# Verify AI prompt was called with correct translation parameters
	mock_prompt.assert_called_once_with(
		'Translate the text "How are you?" from English to Spanish. Keep the tone and meaning of the original text. Stay accurate.'
	)
