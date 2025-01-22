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

# Import the discord library for creating Discord bots
import discord

# Import commands from discord.ext for creating bot commands
from discord.ext import commands

# Import app_commands from discord for creating slash commands
from discord import app_commands

# Import ERROR_MESSAGE constant from the config module
from config.config import ERROR_MESSAGE

# Import UseAI class from utils.helpers for AI-based translations
from utils.helpers import UseAI


# Define the TranslateCog class as a subclass of commands.Cog
# noinspection PyUnresolvedReferences
class TranslateCog(commands.Cog):
	"""
	A Discord Cog for translating text from one language to another.
	"""

	# Initialize the TranslateCog with a bot instance
	def __init__(self, bot: commands.Bot):
		"""
		Initializes the TranslateCog with the given bot instance.

		Parameters:
		bot (commands.Bot): The bot instance to which this cog is added.
		"""
		# Assign the bot instance to self.bot
		self.bot = bot

	# Define a slash command named "translate" with a description
	@app_commands.command(name="translate", description='Translate text from one language to another')
	# Describe the parameters for the slash command
	@app_commands.describe(
		text='The text to translate',
		from_language='The language code of the source language (Default: Thai)',
		to_language='The language code of the target language (Default: English)'
	)
	# Define the asynchronous function that handles the "translate" command
	async def translate_command(self, interaction: discord.Interaction, text: str, from_language: str = 'Thai', to_language: str = 'English'):
		"""
		A slash command to translate text from one language to another.

		Parameters:
		interaction (discord.Interaction): The interaction object representing the command invocation.
		text (str): The text to translate.
		from_language (str): The language code of the source language. Defaults to 'Thai'.
		to_language (str): The language code of the target language. Defaults to 'English'.
		"""
		# Create an instance of UseAI with 'groq' as the provider
		ai = UseAI('groq')

		# Generate the translation using the AI instance
		output = ai.prompt(f'Translate the text "{text}" from {from_language} to {to_language}. Keep the tone and meaning of the original text.')

		if not output:
			# Send an error message if the translation fails
			await interaction.response.send_message(ERROR_MESSAGE)

		# Send the translated text as a response to the interaction
		await interaction.response.send_message(output)


# Define the asynchronous setup function to add the TranslateCog to the bot
async def setup(bot: commands.Bot):
	"""
	A setup function to add the TranslateCog to the bot.

	Parameters:
	bot (commands.Bot): The bot instance to which this cog is added.
	"""
	# Add an instance of TranslateCog to the bot
	await bot.add_cog(TranslateCog(bot))
