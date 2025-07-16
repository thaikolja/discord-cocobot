#  Copyright (C) 2025 by Kolja Nolte
#  kolja.nolte@gmail.com
#  https://gitlab.com/thailand-discord/bots/cocobot
#
#  This work is licensed under the MIT License. You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
#  and to permit persons to whom the Software is furnished to do so, subject to the condition that the above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  For more information, visit: https://opensource.org/licenses/MIT
#
#  Author:    Kolja Nolte
#  Email:     kolja.nolte@gmail.com
#  License:   MIT
#  Date:      2014-2025
#  Package:   cocobot Discord Bot

# Import the discord.py library for interacting with the Discord API
import discord

# Import the regular expression module for pattern matching in text
import re

# Import timedelta for time-related operations
from datetime import timedelta

# Import the commands extension from discord.py for bot command handling
from discord.ext import commands
from discord.ext.commands import HelpCommand

# Import configuration constants from the config file
from config.config import DISCORD_BOT_TOKEN, COCOBOT_VERSION, DISCORD_SERVER_ID

# Import datetime for current time operations
from datetime import datetime

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
	# Air pollution information cog
	'cogs.pollution',
	# Learning-related commands cog
	'cogs.learn'
]


# Define the main bot class inheriting from commands.Bot
class Cocobot(commands.Bot):
	"""
	Represents the Cocobot, an advanced Discord bot providing various features and interactions.

	Cocobot is designed to enhance the user experience in Discord servers through commands,
	events, and member reminders. It includes capabilities for custom command handling,
	cooldown management, and contextual reminders within specific channels. The bot responds
	intuitively based on the content of the messages it receives and performs actions accordingly.

	Attributes:
	    version (str): The version identifier for the bot.
	"""
	# Version identifier for the bot
	version: str = COCOBOT_VERSION

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

		# Set to track users reminded in the visa channel
		self.reminded_users = set()

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

		# Check for visa channel nationality reminder condition
		if message.channel.name == "visa" and "?" in message.content and message.author.id not in self.reminded_users:
			# Send a reminder to mention nationality in the visa channel
			await message.channel.send(
				f"🥥 **Friendly reminder to {message.author.mention}**: Don't forget to **mention your nationality** when asking questions in this channel. Visa rules can vary "
				f"significantly based on your nationality.",
				silent=True,
			)
			# Add user to reminded set
			self.reminded_users.add(message.author.id)
			# Prevent further processing for this message
			return

		# Flag for sending Cocobot info embed
		send_cocobot_info_embed = False

		# Strip whitespace from message content
		normalized_message_content_stripped = message.content.strip()

		# Check if message is exactly '!cocobot'
		is_cocobot_command = normalized_message_content_stripped.lower() == '!cocobot'

		# Check if Cocobot is mentioned in the message
		is_cocobot_mention = any(
			mention.id == self.user.id for mention in message.mentions
		)

		# Set flag if command or mention detected
		if is_cocobot_command or is_cocobot_mention:
			send_cocobot_info_embed = True

		# Send Cocobot info embed if flag is set
		if send_cocobot_info_embed:
			# Create embed for Cocobot info
			embed = discord.Embed(
				timestamp=datetime.now(),
				title=f"🥥 Cocobot at your service!",
				url="https://gitlab.com/thailand-discord/bots/cocobot",
				description=f"Hi, I'm **@cocobot** `v{COCOBOT_VERSION}`, the *actual* useful brother of our dearest August Engelhardt. Type `/coco` to see what I can do for you. I "
				            "promise on the holy coconut, I'm here to help.",
				color=discord.Color.green(),
			)
			# Add bot avatar as thumbnail if available
			if self.user.display_avatar:
				embed.set_thumbnail(url=self.user.display_avatar.url)
				# Set footer text
				embed.set_footer(text=f"© Coconut wisdom since 1875")
			# Send the embed to the channel
			await message.channel.send(embed=embed)
			# Prevent further processing for this message
			return

		# Regular expression pattern to detect the word 'tate'
		tate_pattern = r'(?<!\w)tate(?!\w)'

		# Search for 'tate' in message content
		if re.search(tate_pattern, message.content, re.IGNORECASE):
			# Get current time
			now = datetime.now()

			# Get message author
			user = message.author

			# Check if user is in cooldown dictionary
			if user.id in self.tate_cooldowns:
				# Get last used timestamp
				last_used = self.tate_cooldowns[user.id]

				# Calculate time since last use
				time_since = now - last_used

				# Check if cooldown period has not passed
				if time_since < timedelta(minutes=3):
					# Inform user about cooldown
					await message.channel.send(f"🥥 Sorry, {user.mention}, the Bottom G is tired from all the Bottom G'ing and needs a 5-minute break.")

					# Prevent further processing for this message
					return
				# Update last used timestamp
				self.tate_cooldowns[user.id] = now
			# If user is not in cooldown dictionary
			else:
				# Add user to cooldown dictionary
				self.tate_cooldowns[user.id] = now

			# Create embed for 'tate' GIF
			embed = discord.Embed()
			embed.set_image(url='https://c.tenor.com/fyrqnSBR4gcAAAAd/tenor.gif')

			# Send the embed to the channel
			await message.channel.send(embed=embed)
		# Check for tribute to @Nal
		elif '@Nal' in message.content or any(mention.name == 'nal_9345' for mention in message.mentions):
			# Create embed for Nal tribute
			embed = discord.Embed()
			embed.set_image(url='https://smmallcdn.net/kolja/1749743431468/nal.avif')
			# Send the embed to the channel
			await message.channel.send(embed=embed)

		# Process any commands contained in the message
		await self.process_commands(message)


# Initialize an instance of the Cocobot class
bot = Cocobot()

# Run the bot using the token retrieved from the configuration
bot.run(DISCORD_BOT_TOKEN)
