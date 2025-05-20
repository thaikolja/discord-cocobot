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

# Importing the os module to interact with the operating system
import os

# Importing the json module to handle JSON data
import json

# Importing the discord module to interact with the Discord API
import discord

# Importing the random module to generate random numbers
import random

# Importing the commands module from discord.ext to create bot commands
from discord.ext import commands

# Importing the app_commands module from discord to create application commands
from discord import app_commands

# Importing the ERROR_MESSAGE constant from the config module
from config.config import ERROR_MESSAGE


# Defining a new class LearnCog that inherits from commands.Cog
# noinspection PyUnresolvedReferences
class LearnCog(commands.Cog):
	# Initializing the LearnCog class with a bot instance
	def __init__(self, bot: commands.Bot):

		# Assigning the bot instance to the self.bot attribute
		self.bot = bot

	# Defining a new application command named "learn" with a description
	@app_commands.command(name="learn", description='Displays one of 250 core Thai words and its translation')
	# Defining an asynchronous method learn_command that handles the "learn" command
	async def learn_command(self, interaction: discord.Interaction):

		# Specifying the file path to the JSON file containing the word list
		word_list_path = './assets/data/thai-words.json'

		# Checking if the word list file exists
		if not os.path.isfile(word_list_path):
			# Sending an error message to the interaction if the file does not exist
			await interaction.response.send_message(f"{ERROR_MESSAGE}: No vocabulary found.")
			# Returning from the function to prevent further execution
			return

		# Attempting to open and read the content of the word list file
		try:
			# Opening the word list file in read mode with UTF-8 encoding
			with open(word_list_path, 'r', encoding='utf-8') as file:
				# Loading the JSON data from the file
				data = json.load(file)
		# Catching potential JSON decoding errors
		except json.JSONDecodeError:
			# Handling potential errors in parsing JSON data
			await interaction.response.send_message(f"{ERROR_MESSAGE}: Failed to read vocabulary data. The file may be corrupted.")
			# Returning from the function to prevent further execution
			return
		# Catching all other exceptions
		except Exception as e:
			# Catching all other exceptions and displaying the error message
			await interaction.response.send_message(f"{ERROR_MESSAGE}: An unexpected error occurred: {str(e)}")
			# Returning from the function to prevent further execution
			return

		# Checking if the word list is empty
		if not data:
			# Sending an error message to the interaction if the word list is empty
			await interaction.response.send_message(f"{ERROR_MESSAGE}: I found the vocabulary file, but it contains no words. Weird.")
			# Returning from the function to prevent further execution
			return

		# Selecting a random word from the word list
		word = random.choice(data)

		# Checking if the selected word contains necessary fields
		if not word.get('english') or not word.get('thai') or not word.get('transliteration'):
			# Sending an error message to the interaction if the word is missing key data
			await interaction.response.send_message(f"{ERROR_MESSAGE}: Something's wrong with this word entry. Missing key data.")
			# Returning from the function to prevent further execution
			return

		# Sending a sentence with the word's English translation, Thai translation, and transliteration
		await interaction.response.send_message(f'💡 **"{word["english"]}"** means **"{word["thai"]}"** in Thai and is spoken like `{word["transliteration"]}`')


# Defining an asynchronous setup function to add the LearnCog to the bot
async def setup(bot: commands.Bot):

	# Adding the LearnCog to the bot
	await bot.add_cog(LearnCog(bot))
