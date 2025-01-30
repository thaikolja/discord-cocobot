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

# Import the discord.py library for Discord functionality
import discord

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
		A slash command to translate text from one language to another.
		"""
		# Create an instance of the UseAI helper with Groq as the provider
		ai = UseAI(provider='groq')

		# Use the AI to translate the given text between languages
		output = ai.prompt(
			f'Translate the text "{text}" from {from_language} to {to_language}. '
			'Keep the tone and meaning of the original text.'
		)

		# Check if the translation output was successful
		if not output:
			# Send error message if translation failed
			await interaction.response.send_message(ERROR_MESSAGE)
		else:
			# Send the translated text back to the channel
			await interaction.response.send_message(
				f"🇹🇭 {output}"
			)


# Define the asynchronous setup function to add the TranslateCog to the bot
async def setup(bot: commands.Bot):
	# Add an instance of TranslateCog to the bot
	await bot.add_cog(TranslateCog(bot))
