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

"""
This module provides a Discord Cog for translating text from one language to another using AI.
"""

# Import the discord.py library for Discord functionality
import discord

import openai

# Import commands extension from discord.py for creating bot commands
from discord.ext import commands

# Import app_commands from discord for slash command functionality
from discord import app_commands

# Import the error message constant from config
from config.config import ERROR_MESSAGE

# Import the UseAI helper class from utils.helpers
from utils.helpers import UseAI


# Define a new Cog class for translation functionality
# noinspection PyUnresolvedReferences
class TranslateCog(commands.Cog):
	"""
	A Discord Cog for translating text from one language to another.
	"""

	# Initialize the TranslateCog with a bot instance
	def __init__(self, bot: commands.Bot):
		"""
		Initializes the TranslateCog class with the given bot instance.

		Parameters:
		bot (commands.Bot): The bot instance to which this cog is added
		"""
		# Store the bot instance for later use
		self.bot = bot

	# Define a slash command for translation
	@app_commands.command(
		name="translate",
		description='Translate text from one language to another'
	)
	# Describe the command parameters
	@app_commands.describe(
		text='The text to translate',
		from_language='The language code of the source language (Default: Thai)',
		to_language='The language code of the target language (Default: English)'
	)
	# Define the asynchronous function that handles the "translate" command
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
			ai = UseAI(provider='groq')
			output = ai.prompt(f'Translate the text "{text}" from {from_language} to {to_language}. Keep the tone and meaning of the original text.')
			if not output:
				await interaction.followup.send(ERROR_MESSAGE)
				return
			await interaction.followup.send(f"📚️ {output}")
		except openai.APITimeoutError:
			await interaction.followup.send("⏰ Request timed out after 10 seconds")
		except Exception as e:
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
