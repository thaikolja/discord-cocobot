# Copyright (C) 2025 by Kolja Nolte
# kolja.nolte@gmail.com
# https://gitlab.com/thaikolja/discord-cocobot
#
# This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
# You are free to use, share, and adapt this work for non-commercial purposes, provided that you:
# - Give appropriate credit to the original author.
# - Provide a link to the license.
# - Distribute your contributions under the same license.
#
# For more information, visit: https://creativecommons.org/licenses/by-nc-sa/4.0/
#
# Author:    Kolja Nolte
# Email:     kolja.nolte@gmail.com
# License:   CC BY-NC-SA 4.0
# Date:      2014-2025
# Package:   Thailand Discord

# Import the requests library to make HTTP requests to external APIs
import requests

# Import the discord library for interacting with the Discord API
import discord

# Import the commands module from discord.ext to create bot commands
from discord.ext import commands

# Import the app_commands module from discord to create slash commands
from discord import app_commands

# Import the datetime module for handling dates and times
from datetime import datetime

# Import configuration constants from the config module
from config.config import ERROR_MESSAGE, LOCALTIME_API_KEY

# Import the sanitize_url helper function from utils.helpers
from utils.helpers import sanitize_url


# Define a new Cog class for the time command functionality
# noinspection PyUnresolvedReferences
class TimeCog(commands.Cog):
	# Initialize the Cog with the bot instance
	def __init__(self, bot: commands.Bot):
		# Store the bot reference for later use
		self.bot = bot

	# Define the /time command with description and parameters
	@app_commands.command(
		name="time",
		description='Get the current time at a certain city or country'
	)
	@app_commands.describe(
		location='The city or country for which to get the current time (Default: Bangkok)'
	)
	# Main command function with default parameter for location
	async def time_command(self, interaction: discord.Interaction, location: str = 'Bangkok'):
		# Use try-except block for error handling
		try:
			# Construct and sanitize the API URL with the location parameter
			api_url = sanitize_url(f'https://api.ipgeolocation.io/timezone?apiKey={LOCALTIME_API_KEY}&location={location}')

			# Make a GET request to the API endpoint
			response = requests.get(api_url)

			# Check if the response was successful
			if not response.ok:
				# Raise an exception if the response was not successful
				raise requests.exceptions.RequestException()

			# Parse the JSON response from the API
			data = response.json()

			# Extract country from the response data
			country = data['geo']['country']

			# Get city from response data, fallback to location if not available
			city = data['geo']['city'] or location

			# Parse the date_time string into a datetime object
			time = datetime.strptime(data['date_time'], '%Y-%m-%d %H:%M:%S')

			# Format the output message with the extracted information
			output = f"🕓 In **{city}**, **{country}**, it's currently `{time.strftime('%A, %b %d, %H:%M')}`"

			# Send the response back to the interaction
			await interaction.response.send_message(output)

		# Catch any exceptions that occur during the process
		except (requests.exceptions.RequestException, KeyError):
			# Send an error message if something goes wrong
			await interaction.response.send_message(
				f"{ERROR_MESSAGE} Couldn't find time for `{location}`. Maybe it's in a coconut timezone?"
			)


# Async function to setup and register the Cog
async def setup(bot: commands.Bot):
	# Add the TimeCog to the bot
	await bot.add_cog(TimeCog(bot))
