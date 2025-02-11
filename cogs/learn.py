import os
import json
import random
import discord
from discord.ext import commands
from discord import app_commands


# Define a cog for fetching random Thai words from a JSON file with in-memory caching
class LearnCog(commands.Cog):
	"""
	Cog that fetches random Thai words from a JSON file with caching in memory.
	"""

	def __init__(self, bot):
		"""
		Initialize the LearnCog instance.
		"""
		self.bot = bot
		self.file_path = '../assets/data/thai-words.json'  # Path to the JSON file
		self.cached_data = None  # Cache to store file content
		self.data_loaded = False  # Track if data is already loaded

	def load_data(self):
		"""
		Loads the JSON data from the file, caching it in memory.
		Called when the bot is ready or the first time a command is run.
		"""
		if os.path.isfile(self.file_path):
			try:
				with open(self.file_path, 'r', encoding='utf-8') as file:
					data = json.load(file)
					if isinstance(data, list):  # Ensure data is a list
						self.cached_data = data
						self.data_loaded = True
			except (json.JSONDecodeError, Exception):
				pass  # Ignore errors during file reading or JSON parsing

	def get_random_thai_word(self):
		"""
		Returns a random Thai word from the cached data.
		Uses the cached data in memory to avoid re-reading the file.
		"""
		return random.choice(self.cached_data) if self.cached_data else "Error: No data available. Please try again later."

	@app_commands.command(name="learn", description="Fetches a random Thai word")
	async def learn(self, interaction: discord.Interaction):
		"""
		Command to send a random Thai word to the user.
		"""
		if not self.data_loaded:
			self.load_data()  # Load data if not already loaded

		word = self.get_random_thai_word()
		if isinstance(word, str) and word.startswith("Error"):
			await interaction.response.send_message(word, ephemeral=True)
		else:
			await interaction.response.send_message(f"Random Thai word: {word.get('word', 'No word available')}", ephemeral=True)

	@commands.Cog.listener()
	async def on_ready(self):
		"""
		Called when the bot is ready. Refreshes the cache if needed.
		"""
		if not self.data_loaded:
			self.load_data()  # Load data if not already loaded


# Define a setup function to add the cog to the bot
async def setup(bot):
	await bot.add_cog(LearnCog(bot))
