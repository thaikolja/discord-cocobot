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

# Import required testing modules
import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock

# Import Discord and commands module for bot functionality
import discord
from discord.ext import commands

# Import the Transliterate cog to test
from cogs.transliterate import Transliterate

# Import configuration for error messages
from config.config import ERROR_MESSAGE


# Fixture to create and return a Transliterate cog instance with a bot
@pytest_asyncio.fixture
async def cog():
	# Create a new bot instance with default command prefix and intents
	bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
	# Return the Transliterate cog instance
	return Transliterate(bot)


# Fixture to create a mocked Discord interaction
@pytest.fixture
def interaction():
	# Create an AsyncMock for the interaction object
	intr = AsyncMock()
	# Mock the response and followup methods
	intr.response = AsyncMock()
	intr.followup = AsyncMock()
	# Return the mocked interaction
	return intr


# Helper function to validate transliteration output format
def validate_transliteration(output: str) -> bool:
	"""Basic validation of transliteration format"""
	# Check if output contains any of the required characters
	return any(c in output for c in ["-", " ", "à", "è", "ù"]) if output else False


# Test the main transliteration flow
@pytest.mark.asyncio
@patch('utils.helpers.UseAI.prompt')
async def test_transliteration_flow(mock_prompt, cog, interaction):
	# Set up mock response from AI
	mock_prompt.return_value = "sà-wàt-dii"

	# Call the transliterate command with test input
	await cog.transliterate_command.callback(
		cog,
		interaction,
		text="สวัสดี"
	)

	# Verify response was deferred
	interaction.response.defer.assert_awaited_once()

	# Verify followup message was sent
	interaction.followup.send.assert_awaited_once()

	# Get the response text from followup message
	response_text = interaction.followup.send.call_args[0][0]

	# Assert that response is valid
	assert validate_transliteration(response_text)


# Test error handling for API exceptions
@pytest.mark.asyncio
@patch('utils.helpers.UseAI.prompt')
async def test_error_handling(mock_prompt, cog, interaction):
	# Set up mock to raise an exception
	mock_prompt.side_effect = Exception("API Error")

	# Call the transliterate command with test input
	await cog.transliterate_command.callback(
		cog,
		interaction,
		text="ทดสอบ"
	)

	# Verify error message was sent
	interaction.followup.send.assert_awaited_once_with(
		f"✍️ {ERROR_MESSAGE}"
	)


# Test prompt construction with various inputs
@pytest.mark.asyncio
@patch('utils.helpers.UseAI.prompt')
async def test_prompt_construction(mock_prompt, cog, interaction):
	# Define test cases with input and expected output
	test_cases = [
		("สวัสดี", "สวัสดี"),
		("A", "A"),
		("X" * 500, "X" * 500)
	]

	# Iterate through each test case
	for input_text, expected in test_cases:
		# Reset mock before each test case
		mock_prompt.reset_mock()

		# Call the transliterate command
		await cog.transliterate_command.callback(cog, interaction, text=input_text)

		# Get the arguments used in mock call
		args, kwargs = mock_prompt.call_args

		# Verify input text appears in prompt
		assert f"'{expected}'" in args[0]

		# Verify default strict mode is enabled
		assert len(args) >= 2 or kwargs.get('strict', True) is True


# Test handling of empty responses from AI
@pytest.mark.asyncio
@patch('utils.helpers.UseAI.prompt')
async def test_empty_response_handling(mock_prompt, cog, interaction):
	# Set up mock to return empty string
	mock_prompt.return_value = ""

	# Call the transliterate command with test input
	await cog.transliterate_command.callback(
		cog,
		interaction,
		text="ทดสอบ"
	)

	# Verify error message was sent
	interaction.followup.send.assert_awaited_once_with(f"✍️ {ERROR_MESSAGE}")
