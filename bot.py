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

# Import the discord.py library for interacting with the Discord API
import discord

# Import the regular expression module for pattern matching in text
import re

# Import datetime and timedelta from the datetime module for time-related operations
from datetime import datetime, timedelta

# Import the commands extension from discord.py for bot command handling
from discord.ext import commands

# Import configuration constants from the config file
from config.config import DISCORD_BOT_TOKEN, DISCORD_SERVER_ID

# Import the logging module for tracking bot activities and errors
import logging

# Configure basic logging settings to track bot activities
logging.basicConfig(level=logging.INFO)

# Create a logger instance for discord-related logs
logger = logging.getLogger('discord')

# List of initial extensions (cogs) to load on startup
INITIAL_EXTENSIONS = [
	# Time-related commands cog
	'cogs.time',
	# Currency exchange functionality cog
	'cogs.exchangerate',
	# Weather information commands cog
	'cogs.weather',
	# Text transliteration commands cog
	'cogs.transliterate',
	# Translation commands cog
	'cogs.translate',
	# Geolocation commands cog
	'cogs.locate',
	# Air pollution information cog
	'cogs.pollution',
	# Learning-related commands cog
	'cogs.learn',
	#	'cogs.quiz',  # TODO: Thai vocabulary quiz commands
]


# Define the main bot class inheriting from commands.Bot
class Cocobot(commands.Bot):
	"""
	The main bot class that handles initialization, command loading, and event processing.

	Inherits from discord.ext.commands.Bot to provide bot functionalities.
	"""
	# Version identifier for the bot
	version: str = '2.2.1'

	# Constructor method to initialize the bot
	def __init__(self):
		"""
		Initializes the Cocobot instance, setting up intents and command prefix.
		"""
		# Initialize default Discord intents
		intents = discord.Intents.default()
		# Enable member-related intents for tracking member information
		intents.members = True
		# Enable message content intent to read message content
		intents.message_content = True
		# Call the parent class constructor with command prefix and intents
		super().__init__(command_prefix='!', intents=intents)
		# Dictionary to track cooldowns for the 'tate' command per user
		self.tate_cooldowns = {}

	# Setup hook to load extensions and sync commands
	async def setup_hook(self):
		"""
		Asynchronous setup hook called after login but before connecting to the websocket.
		Loads initial extensions (cogs) and synchronizes the application command tree.
		"""
		# Iterate through the list of initial extensions
		for extension in INITIAL_EXTENSIONS:
			# Try to load the current extension
			try:
				# Asynchronously load the extension
				await self.load_extension(extension)
				# Log successful loading of the extension
				logger.info(f'Loaded extension: {extension}')
			# Catch any exception during extension loading
			except Exception as e:
				# Log the failure to load the extension along with the error details
				logger.error(f'Failed to load extension {extension}. {type(e).__name__}: {e}')

		# Create a discord.Object representing the target guild using its ID
		guild = discord.Object(id=DISCORD_SERVER_ID)
		# Copy global application commands to the specified guild
		self.tree.copy_global_to(guild=guild)
		# Synchronize the application command tree with the specified guild
		await self.tree.sync(guild=guild)
		# Log that the command tree synchronization is complete
		logger.info('Command tree synced.')

	# Event that triggers when the bot is ready and online
	async def on_ready(self):
		"""
		Event handler called when the bot has successfully connected to Discord and is ready.
		Logs a confirmation message indicating the bot is online.
		"""
		# Log an informational message indicating the bot is ready, including its username
		logger.info(f'🥥 {self.user} is ready!')

	# Event that triggers for every message received
	async def on_message(self, message):
		"""
		Event handler called for every message received in channels the bot has access to.
		Handles the 'tate' response with cooldown and processes other commands.

		Args:
			message (discord.Message): The message object received.
		"""
		# Check if the message author is the bot itself to prevent self-responses
		if message.author == self.user:
			# Exit the handler if the message is from the bot
			return

		# Define the regular expression pattern to detect the word 'tate' case-insensitively, ensuring it's a whole word
		tate_pattern = r'(?<!\w)tate(?!\w)'
		# Search for the 'tate' pattern within the message content, ignoring case
		if re.search(tate_pattern, message.content, re.IGNORECASE):
			# Get the current date and time
			now = datetime.now()
			# Get the author of the message
			user = message.author

			# Check if the user ID exists in the tate_cooldowns dictionary
			if user.id in self.tate_cooldowns:
				# Retrieve the timestamp of the last time the user triggered the 'tate' response
				last_used = self.tate_cooldowns[user.id]
				# Calculate the time elapsed since the last usage
				time_since = now - last_used
				# Check if the elapsed time is less than 5 minutes
				if time_since < timedelta(minutes=5):
					# Send a message informing the user about the cooldown
					await message.channel.send(f"🥥 Sorry, {user.mention}, the Bottom G is tired from all the Bottom G'ing and needs a 5-minute break. ")
					# Exit the handler as the user is on cooldown
					return

				# Update the last usage timestamp for the user in the cooldowns dictionary
				self.tate_cooldowns[user.id] = now

			# If the user is not in the cooldowns dictionary (first time or cooldown expired)
			else:
				# Add the user to the cooldowns dictionary with the current timestamp
				self.tate_cooldowns[user.id] = now

			# Create a Discord embed object
			embed = discord.Embed()
			# Set the image URL for the embed
			embed.set_image(url='https://c.tenor.com/fyrqnSBR4gcAAAAd/tenor.gif')
			# Send the embed containing the GIF image to the channel where the message was received
			await message.channel.send(embed=embed)

		# Process any commands contained in the message
		await self.process_commands(message)


# Initialize an instance of the Cocobot class
bot = Cocobot()
# Run the bot using the token retrieved from the configuration
bot.run(DISCORD_BOT_TOKEN)
