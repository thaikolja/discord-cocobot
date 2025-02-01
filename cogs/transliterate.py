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

# Import the discord.py library to create Discord bots and interact with the Discord API
import discord

# Import the commands extension from discord.ext to create bot commands
from discord.ext import commands

# Import app_commands from discord to enable slash command functionality
from discord import app_commands

# Import the UseAI class from utils.helpers to handle AI-based transliterations
from utils.helpers import UseAI


# Define a new Cog class named Transliterate that inherits from commands.Cog
# This Cog will handle the transliteration functionality of the bot
# noinspection PyUnresolvedReferences
class Transliterate(commands.Cog):
	"""
	A Discord Cog for transliterating Thai text to Latin script.

	This class contains functionality to convert Thai text into Latin characters
	using an AI provider for accurate transliteration.
	"""

	# Constructor method to initialize the Transliterate Cog
	def __init__(self, bot: commands.Bot):
		"""
		Initializes the Transliterate class with the given bot instance.

		Parameters:
		bot (commands.Bot): The bot instance to which this cog is added
		"""
		# Store the bot instance for later use
		self.bot = bot

	# Define a slash command named "transliterate" with description
	@app_commands.command(
		name="transliterate",
		description='Transliterate Thai text to Latin script'
	)
	# Describe the parameter for the slash command
	@app_commands.describe(
		text='The text to transliterate'
	)
	# Define the asynchronous function to handle the "transliterate" command
	async def transliterate_command(
		self,
		interaction: discord.Interaction,
		text: str
	):
		# Defer the response immediately
		await interaction.response.defer()

		prompt = (
			f"Transliterate the Thai text '{text}' into Latin characters only. "
			f"Use diacritics to display the tone markers for every consonant and vowel. "
			f"Separate syllables with a dash. Separate words with a space. "
			f"Make it readable for English readers."
		)

		ai = UseAI(provider='perplexity')
		answer = ai.prompt(prompt)

		# Send the result using follow-up
		await interaction.followup.send(f"✍️ {answer}")


# Define the asynchronous setup function to register the Transliterate cog
async def setup(bot: commands.Bot):
	"""
	A setup function to add the Transliterate cog to the bot.

	Parameters:
	bot (commands.Bot): The bot instance to which this cog is added
	"""
	# Add the Transliterate cog to the bot using add_cog method
	await bot.add_cog(Transliterate(bot))
