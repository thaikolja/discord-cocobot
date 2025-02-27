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
logger = logging.getLogger('discord')

# List of initial extensions (cogs) to load on startup
INITIAL_EXTENSIONS = [
	'cogs.time',  # Time-related commands
	'cogs.exchangerate',  # Currency exchange functionality
	'cogs.weather',  # Weather information commands
	'cogs.transliterate',  # Text transliteration commands
	'cogs.translate',  # Translation commands
	'cogs.locate',  # Geolocation commands
	'cogs.pollution',  # Air pollution information
	'cogs.learn'  # Learning-related commands
]


# Define the main bot class inheriting from commands.Bot
class Cocobot(commands.Bot):
	# Version identifier for the bot
	version: str = '2.0.2'

	# Constructor method to initialize the bot
	def __init__(self):
		# Initialize bot with specified command prefix and intents
		intents = discord.Intents.default()
		intents.members = True  # Enable member-related intents
		intents.message_content = True  # Enable message content intent
		super().__init__(command_prefix='!', intents=intents)
		self.tate_cooldowns = {}  # Dictionary to track cooldowns for the 'tate' command

	# Setup hook to load extensions and sync commands
	async def setup_hook(self):
		# Load all extensions on startup
		for extension in INITIAL_EXTENSIONS:
			try:
				await self.load_extension(extension)
				logger.info(f'Loaded extension: {extension}')
			except Exception as e:
				logger.error(f'Failed to load extension {extension}. {type(e).__name__}: {e}')

		# Sync command tree with the specified guild
		guild = discord.Object(id=DISCORD_SERVER_ID)
		self.tree.copy_global_to(guild=guild)
		await self.tree.sync(guild=guild)
		logger.info('Command tree synced.')

	# Event that triggers when the bot is ready and online
	async def on_ready(self):
		logger.info(f'🥥 {self.user} is ready!')

	# Event that triggers for every message received
	async def on_message(self, message):
		# Ignore messages sent by the bot itself
		if message.author == self.user:
			return

		# Regular expression pattern to detect 'tate' in messages
		tate_pattern = r'(?<!\w)tate(?!\w)'
		if re.search(tate_pattern, message.content, re.IGNORECASE):
			now = datetime.now()
			user = message.author

			# Check if the user is on cooldown
			if user.id in self.tate_cooldowns:
				last_used = self.tate_cooldowns[user.id]
				time_since = now - last_used

				if time_since < timedelta(minutes=5):
					await message.channel.send(f"🥥 Sorry, {user.mention}, the Bottom G is tired from all the Bottom G'ing and needs a 5-minute break. ")
					return

				self.tate_cooldowns[user.id] = now
			else:
				self.tate_cooldowns[user.id] = now

			# Send embedded image as a response
			await message.channel.send(embed=discord.Embed().set_image(url='https://c.tenor.com/fyrqnSBR4gcAAAAd/tenor.gif'))

		# Process other commands
		await self.process_commands(message)


# Initialize and run the bot with the token from config
bot = Cocobot()
bot.run(DISCORD_BOT_TOKEN)
