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

# Import necessary modules for Discord bot functionality
import discord  # For interacting with the Discord API

from discord.ext import commands  # For creating bot commands

from discord import app_commands  # For defining slash commands

from config.config import ERROR_MESSAGE  # Import custom error message from configuration

from utils.helpers import UseAI  # Import AI helper utility

import logging  # Import logging module for error tracking

# Configure logging to track activities and errors specific to this module
logger = logging.getLogger(__name__)


# noinspection PyUnresolvedReferences
class Transliterate(commands.Cog):
	"""
	A Discord Cog that provides functionality to transliterate Thai text into Latin script.

	This cog uses an AI service to perform the transliteration, ensuring accurate and readable results.
	It follows the Discord.py cog structure for clean and maintainable code organization.
	"""

	# Initialize the Transliterate cog with the bot instance
	def __init__(self, bot: commands.Bot):
		"""
		Initialize the Transliterate cog with the bot instance.

		Args:
						bot (commands.Bot): The Discord bot instance this cog is attached to.
		"""
		self.bot = bot

	@app_commands.command(
		name="transliterate",
		description='Transliterate Thai text into Latin script with tone markers.'
	)
	@app_commands.describe(
		text='The Thai text to be transliterated into Latin script.'
	)
	async def transliterate_command(
		self,
		interaction: discord.Interaction,
		text: str
	):
		"""
		Handle the /transliterate command by processing the input text and returning the transliterated result.

		Args:
						interaction (discord.Interaction): The interaction that triggered this command.
						text (str): The Thai text to be transliterated.
		"""
		# Defer the response to let Discord know we're processing the command
		await interaction.response.defer()

		try:
			# Initialize the AI helper with the preferred provider
			ai = UseAI(provider='google')

			# Construct the prompt for the AI to process
			prompt = (
				f"Transliterate the Thai text '{text}' into Latin characters only. "
				f"Use diacritics to display the tone markers for every consonant and vowel. "
				f"Separate syllables with a dash. Separate individual words with a whitespace. "
				f"Make it readable for English readers."
				f"Replace the character 'ก' with 'g', replace 'ป' with 'bp', and replace 'ต' with 'dt'. "
			)

			# Get the response from the AI
			answer = ai.prompt(prompt)

			# Check if the response is valid
			if not answer:
				raise ValueError("No response received from the AI service.")

			# Clean up the response for output
			cleaned_answer = ' '.join(answer.strip().split())
			cleaned_answer = cleaned_answer.replace(':', '')  # Remove any colon characters
			transliteration = cleaned_answer.strip()

			# Send the transliterated text back to the user
			await interaction.followup.send(f"✍️ **Transliteration:** {transliteration}")

		except Exception as e:
			# Log any errors that occur during processing
			logger.error(f"Transliteration error: {str(e)}")
			# Send a friendly error message to the user
			await interaction.followup.send(f"✍️ {ERROR_MESSAGE}")


# Function to add the Transliterate cog to the bot
async def setup(bot: commands.Bot):
	"""
	Add the Transliterate cog to the bot.

	Args:
					bot (commands.Bot): The Discord bot instance to add the cog to.
	"""
	await bot.add_cog(Transliterate(bot))