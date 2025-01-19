import discord
from discord import app_commands
from discord.ext import commands
from config.config import DISCORD_BOT_TOKEN, DISCORD_SERVER_ID

# List of cogs to load
initial_extensions = ['cogs.time', 'cogs.weather']


class Cocobot(commands.Bot):
	"""
	A custom Discord bot class for the Cocobot.
	"""

	version: str = '1.2.4'

	def __init__(self):
		"""
		Initialize the Cocobot with specified intents and command prefix.
		"""
		# Define intents
		intents = discord.Intents.default()
		intents.members = True
		intents.message_content = True  # Ensure this intent is enabled in the Developer Portal

		# Initialize the superclass with command prefix and intents
		super().__init__(command_prefix='!', intents=intents)

	# Initialize the command tree for slash commands
	# self.tree = app_commands.CommandTree(self)

	async def setup_hook(self):
		"""
		A setup hook that runs before the bot connects to Discord.
		It loads all extensions and syncs the command tree.
		"""
		# Load each extension (cog)
		for extension in initial_extensions:
			try:
				await self.load_extension(extension)
				print(f'Loaded extension: {extension}')
			except Exception as e:
				print(f'Failed to load extension {extension}.')
				print(f'{type(e).__name__}: {e}')

		# Sync the command tree to the specified guild
		guild = discord.Object(id=DISCORD_SERVER_ID)
		self.tree.copy_global_to(guild=guild)
		await self.tree.sync(guild=guild)
		print('Command tree synced.')

	async def on_ready(self):
		"""
		Event handler called when the bot is ready.
		"""
		print(f'Logged in as {self.user} (ID: {self.user.id})')
		print('------')


# Initialize the bot
bot = Cocobot()

# Run the bot
bot.run(DISCORD_BOT_TOKEN)
