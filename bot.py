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

# Import the discord library
import discord

# Import commands from discord.ext
from discord.ext import commands

# Import the bot token and server ID from config
from config.config import DISCORD_BOT_TOKEN, DISCORD_SERVER_ID

# Import the logging library for better logging practices
import logging

# Configure the logging settings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')

# Define a list of initial extensions (Cogs) to load
INITIAL_EXTENSIONS = [
	'cogs.time',
	'cogs.exchangerate',
	'cogs.weather',
	'cogs.transliterate',
	'cogs.translate',
	'cogs.locate',
]


# Define the Cocobot class, a subclass of commands.Bot
class Cocobot(commands.Bot):
	# Define the version of the bot
	version: str = '2.0.0'

	# Initialize the Cocobot instance
	def __init__(self):
		# Create default intents
		intents = discord.Intents.default()

		# Enable the members intent
		intents.members = True

		# Enable the message content intent
		intents.message_content = True

		# Initialize the parent class with command prefix and intents
		super().__init__(command_prefix='!', intents=intents)

	# Setup hook to load extensions and sync command tree
	async def setup_hook(self):
		# Iterate through each extension in INITIAL_EXTENSIONS
		for extension in INITIAL_EXTENSIONS:
			try:
				# Attempt to load the extension
				await self.load_extension(extension)
				# Log success message
				logger.info(f'Loaded extension: {extension}')
			except Exception as e:
				# Log failure message with exception details
				logger.error(f'Failed to load extension {extension}. {type(e).__name__}: {e}')

		# Create a guild object with the server ID
		guild = discord.Object(id=DISCORD_SERVER_ID)

		# Copy global command tree to the specified guild
		self.tree.copy_global_to(guild=guild)

		# Synchronize the command tree with the guild
		await self.tree.sync(guild=guild)

		# Log that the command tree has been synced
		logger.info('Command tree synced.')

	# Event handler for when the bot is ready
	async def on_ready(self):
		# Log the bot's username and ID
		logger.info(f'🥥 {self.user} is ready!')


# Create an instance of the Cocobot
bot = Cocobot()

# Run the bot with the specified token
bot.run(DISCORD_BOT_TOKEN)
