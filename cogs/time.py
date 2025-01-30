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

# Import the requests library to handle HTTP requests
import requests

# Import the discord library to interact with Discord's API
import discord

# Import the commands extension from discord to create bot commands
from discord.ext import commands

# Import app_commands from discord for creating application (slash) commands
from discord import app_commands

# Import the datetime class from the datetime module for handling date and time
from datetime import datetime

# Import constants ERROR_MESSAGE and LOCALTIME_API_KEY from the config module
from config.config import ERROR_MESSAGE, LOCALTIME_API_KEY

# Import the sanitize_url function from the helpers module in utils
from utils.helpers import sanitize_url


# Define the TimeCog class, which is a subclass of commands.Cog
# noinspection PyUnresolvedReferences
class TimeCog(commands.Cog):
	"""
	A Discord Cog for fetching and displaying the current time for a specified location.
	"""

	# Initialize the cog with a reference to the bot
	def __init__(self, bot: commands.Bot):
		"""
		Initializes the TimeCog with the given bot instance.

		Parameters:
		bot (commands.Bot): The bot instance to which this cog is added.
		"""
		self.bot = bot

	# Define a slash command named "time" with a description
	@app_commands.command(name="time", description='Get the current time at a certain city or country')
	# Describe the "location" parameter for the slash command
	@app_commands.describe(location='The city or country for which to get the current time (Default: Bangkok)')
	# Define the asynchronous function that handles the "time" command
	async def time_command(self, interaction: discord.Interaction, location: str = 'Bangkok'):
		"""
		A slash command to get the current time for a specified location.

		Parameters:
		interaction (discord.Interaction): The interaction object representing the command invocation.
		location (str): The city or country for which to get the current time. Defaults to 'Bangkok'.
		"""
		# Construct the API URL with the sanitized location and API key
		api_url = sanitize_url(f'https://api.ipgeolocation.io/timezone?apiKey={LOCALTIME_API_KEY}&location={location}')

		# Make a GET request to the API URL
		response = requests.get(api_url)

		# Check if the response status is not OK (i.e., not in the 200-399 range)
		if not response.ok:
			# Send an error message to the user indicating the location might not exist
			await interaction.response.send_message(f"{ERROR_MESSAGE} Does `{location}` even exist?!")
			# Exit the function early since the request was unsuccessful
			return

		# Parse the JSON data from the response
		data = response.json()

		# Extract the country from the geo information in the data
		country = data['geo']['country']

		# Extract the city from the geo information or default to the provided location
		city = data['geo']['city'] or location

		# Parse the date_time string into a datetime object
		time = datetime.strptime(data['date_time'], '%Y-%m-%d %H:%M:%S')

		# Format the output string with the city, country, and formatted time
		output = f"🕓 In **{city}**, **{country}**, it's currently `{time.strftime('%A, %b %d, %H:%M')}`"

		# Send the formatted time information to the user
		await interaction.response.send_message(output)


# Define the asynchronous setup function to add the TimeCog to the bot
async def setup(bot: commands.Bot):
	"""
	A setup function to add the TimeCog to the bot.

	Parameters:
	bot (commands.Bot): The bot instance to which this cog is added.
	"""
	# Add an instance of TimeCog to the bot
	await bot.add_cog(TimeCog(bot))
