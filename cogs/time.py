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

# Import the aiohttp library for asynchronous HTTP requests
import aiohttp

# Import asyncio for handling asynchronous operations
import asyncio

# Import the discord library for interacting with the Discord API
import discord

# Import the commands module from discord.ext to create bot commands
from discord.ext import commands

# Import the app_commands module from discord to create slash commands
from discord import app_commands

# Import the datetime module for handling dates and times
from datetime import datetime

# Import the logging module for tracking bot activities and errors
import logging

# Import configuration constants from the config module
from config.config import ERROR_MESSAGE, LOCALTIME_API_KEY

# Configure basic logging settings to track bot activities
logging.basicConfig(level=logging.INFO)

# Create a logger instance for discord-related logs
logger = logging.getLogger('discord')


# Define a new Cog class for the time command functionality
# noinspection PyUnresolvedReferences
class TimeCog(commands.Cog):
	# Initialize the Cog with the bot instance
	def __init__(self, bot: commands.Bot):
		# Store the bot reference for later use
		self.bot = bot
		# Create a single, reusable ClientSession for the lifetime of the cog.
		# This is more efficient than creating a new one for every command call.
		self.session = aiohttp.ClientSession()

	async def cog_unload(self):
		"""Clean up the aiohttp session when the cog is unloaded."""
		await self.session.close()

	# Define the /time command with description and parameters
	@app_commands.command(
		name="time",
		description='Get the current time at a certain city or country'
	)
	@app_commands.describe(
		location='The city or country for which to get the current time (Default: Bangkok)',
	)
	# Main command function with default parameter for location
	async def time_command(self, interaction: discord.Interaction, location: str = 'Bangkok'):
		# The base URL for the API endpoint
		api_url = 'https://api.ipgeolocation.io/timezone'

		# Pass parameters in a dictionary for safe, automatic URL-encoding
		params = {
			'apiKey':   LOCALTIME_API_KEY,
			'location': location
		}

		try:
			# Use the async session to make a non-blocking GET request
			async with self.session.get(api_url, params=params, timeout=10) as response:
				# Raise an exception if the HTTP response status is an error (4xx or 5xx)
				response.raise_for_status()

				# Parse the JSON response asynchronously
				data = await response.json()

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

		# Catch specific exceptions for better error handling and debugging
		except (aiohttp.ClientError, asyncio.TimeoutError, KeyError) as e:
			# aiohttp.ClientError covers connection issues and bad HTTP responses
			# asyncio.TimeoutError handles request timeouts
			# KeyError handles cases where the API response is missing expected data
			logger.error(f"Error fetching time for {location}: {e}")

			# Send an error message back to the interaction
			await interaction.response.send_message(
				f"{ERROR_MESSAGE} Couldn't find time for `{location}`. Maybe it's in a coconut timezone?"
			)


# Async function to setup and register the Cog
async def setup(bot: commands.Bot):
	# Add the TimeCog to the bot
	await bot.add_cog(TimeCog(bot))
