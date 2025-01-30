#!/usr/bin/env python3

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

# Import the discord.py library for Discord bot functionality
import discord

# Import regular expression library for pattern matching
import re

# Import datetime and timedelta for time-related operations
from datetime import datetime, timedelta

# Import commands extension from discord.py for bot commands
from discord.ext import commands

# Import configuration file containing bot token and server ID
from config.config import DISCORD_BOT_TOKEN, DISCORD_SERVER_ID

# Import logging module for logging functionality
import logging

# Set up basic logging configuration with INFO level
logging.basicConfig(level=logging.INFO)

# Create a logger instance named 'discord'
logger = logging.getLogger('discord')

# List of initial extensions (cogs) to load at startup
INITIAL_EXTENSIONS = [
	'cogs.time',  # Time-related commands
	'cogs.exchangerate',  # Currency exchange rate commands
	'cogs.weather',  # Weather information commands
	'cogs.transliterate',  # Text transliteration commands
	'cogs.translate',  # Translation commands
	'cogs.locate',  # Location-related commands
	'cogs.pollution'  # Pollution information commands
]


# Define the main bot class inheriting from commands.Bot
class Cocobot(commands.Bot):
	# Bot version string
	version: str = '2.0.0'

	# Constructor method to initialize the bot
	def __init__(self):
		# Create default intents with all settings
		intents = discord.Intents.default()

		# Enable member tracking intent
		intents.members = True

		# Enable message content intent for reading messages
		intents.message_content = True

		# Call super constructor with command prefix and intents
		super().__init__(command_prefix='!', intents=intents)

		# Initialize cooldown dictionary for tracking command usage
		self.tate_cooldowns = {}

	# Setup hook that runs after the bot is ready but before on_ready
	async def setup_hook(self):
		# Iterate through each extension in INITIAL_EXTENSIONS
		for extension in INITIAL_EXTENSIONS:
			try:
				# Attempt to load the extension
				await self.load_extension(extension)

				# Log successful extension load
				logger.info(f'Loaded extension: {extension}')
			except Exception as e:
				# Log error if extension fails to load
				logger.error(f'Failed to load extension {extension}. {type(e).__name__}: {e}')

		# Create a guild object using the server ID from config
		guild = discord.Object(id=DISCORD_SERVER_ID)

		# Copy global commands to the guild
		self.tree.copy_global_to(guild=guild)

		# Sync the command tree with the guild
		await self.tree.sync(guild=guild)

		# Log successful command tree sync
		logger.info('Command tree synced.')

	# Event that triggers when the bot is fully ready
	async def on_ready(self):
		# Log that the bot is ready with the username
		logger.info(f'🥥 {self.user} is ready!')

	# Event that triggers for every message received
	async def on_message(self, message):
		# Check if the message is from the bot itself
		if message.author == self.user:
			# If so, return and do nothing
			return

		# Regular expression pattern to match 'tate' as a whole word
		tate_pattern = r'(?<!\w)tate(?!\w)'

		# Check if the message content matches the tate pattern (case insensitive)
		if re.search(tate_pattern, message.content, re.IGNORECASE):
			# Get current timestamp
			now = datetime.now()

			# Get the message author
			user = message.author

			# Check if user is in cooldown dictionary
			if user.id in self.tate_cooldowns:
				# Get last used timestamp
				last_used = self.tate_cooldowns[user.id]

				# Calculate time since last use
				time_since = now - last_used

				# Check if less than 5 minutes have passed
				if time_since < timedelta(minutes=5):
					# Send cooldown message and return
					await message.channel.send(f"🥥 Sorry, {user.mention}, the Bottom G is tired from all the Bottom G'ing and needs a 5-minute break. ")
					return

				# Reset cooldown timer
				self.tate_cooldowns[user.id] = now
			else:
				# Set initial cooldown timer
				self.tate_cooldowns[user.id] = now

			# Send the Tate GIF response
			await message.channel.send(embed=discord.Embed().set_image(url='https://c.tenor.com/fyrqnSBR4gcAAAAd/tenor.gif'))

		# Process any commands in the message
		await self.process_commands(message)


# Create an instance of the Cocobot class
bot = Cocobot()

# Run the bot with the token from configuration
bot.run(DISCORD_BOT_TOKEN)
