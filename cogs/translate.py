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

# Import the discord module for interacting with the Discord API
import discord  # For interacting with the Discord API

# Import the openai module for interacting with OpenAI's API
import openai  # For interacting with OpenAI's API

# Import the commands module from discord.ext for creating bot commands
from discord.ext import commands  # For creating bot commands

# Import the app_commands module from discord for defining slash commands
from discord import app_commands  # For defining slash commands

# Import the ERROR_MESSAGE from the config module
from config.config import ERROR_MESSAGE  # Import custom error message from configuration

# Import the UseAI helper utility from the utils.helpers module
from utils.helpers import UseAI  # Import AI helper utility

# Import the logging module for error tracking and logging purposes
import logging  # Import logging module for error tracking

# Configure the logger for this module to track activities and errors
logger = logging.getLogger(__name__)


# noinspection PyUnresolvedReferences
# Define a new Cog class for translation functionality
class TranslateCog(commands.Cog):
	"""
	A Discord Cog for translating text from one language to another.
	"""

	# Constructor to initialize the TranslateCog class with the given bot instance
	def __init__(self, bot: commands.Bot):
		"""
		Initializes the TranslateCog class with the given bot instance.

		Parameters:
		bot (commands.Bot): The bot instance to which this cog is added
		"""
		# Store the bot instance for later use
		self.bot = bot

	# Define a new slash command for translation
	@app_commands.command(
		name="translate",
		description='Translate text from one language to another'
	)
	# Provide descriptions for command parameters
	@app_commands.describe(
		text='The text to translate',
		from_language='The language code of the source language (Default: Thai)',
		to_language='The language code of the target language (Default: English)'
	)
	# Main function to handle the translation command
	async def translate_command(
		self,
		interaction: discord.Interaction,
		text: str,
		from_language: str = 'Thai',
		to_language: str = 'English'
	):
		"""
		Handles the /translate command to translate text from one language to another.

		Parameters:
		interaction (discord.Interaction): The interaction object representing the command invocation
		text (str): The text to translate
		from_language (str): The language code of the source language (Default: Thai)
		to_language (str): The language code of the target language (Default: English)
		"""

		# Defer the response to avoid timeout
		await interaction.response.defer()

		try:
			# Initialize the AI helper with the preferred provider
			ai = UseAI(provider='sambanova')
			# Set AI response parameters
			ai.temperature = 0.3
			ai.top_p = 0.3
			# Construct the prompt for the AI to process
			prompt = (
				f'Translate the text "{text}" from {from_language} to {to_language}. '
				f'Keep the tone and meaning of the original text. Stay accurate.'
			)

			# Get the response from the AI
			output = ai.prompt(prompt)

			# Check if the response is valid
			if not output:
				# Send error message if response is empty
				await interaction.followup.send(ERROR_MESSAGE)
				return

			# Send the translated text back to the user
			await interaction.followup.send(f"📚️ **Translation:** {output}")
		except openai.APITimeoutError:
			# Handle API timeout errors
			await interaction.followup.send("⏰ Request timed out after 10 seconds")
		except Exception as e:
			# Handle other exceptions
			await interaction.followup.send(f"❌ Error: {str(e)}")


# Define the asynchronous setup function to add the TranslateCog to the bot
async def setup(bot: commands.Bot):
	"""
	A setup function to add the TranslateCog to the bot.

	Parameters:
	bot (commands.Bot): The bot instance to which this cog is added
	"""
	# Add an instance of TranslateCog to the bot
	await bot.add_cog(TranslateCog(bot))
