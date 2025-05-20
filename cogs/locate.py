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

# Import the requests module to make HTTP requests to external APIs
import requests

# Import the logging module to log important events and errors
import logging

# Import the Discord module for interacting with the Discord API
import discord

# Import the commands module from discord.ext to create bot commands
from discord.ext import commands

# Import the app_commands module from discord to create slash commands
from discord import app_commands

# Import configuration constants and helper functions from the config module
from config.config import ERROR_MESSAGE  # Custom error message format
from config.config import GOOGLE_MAPS_API_KEY  # API key for Google Maps
from utils.helpers import sanitize_url  # Function to sanitize URLs

# Configure the logging module to show timestamps and set the logging level
logging.basicConfig(level=logging.INFO)  # Set logging level to INFO
logger = logging.getLogger(__name__)  # Create a logger instance for this module


# Define a new Cog class for handling location-based commands
# noinspection PyUnresolvedReferences
class LocateCog(commands.Cog):
	"""
	A Discord Cog for locating addresses within Thailand.
	"""

	# Initialize the Cog with the bot instance
	def __init__(self, bot: commands.Bot):
		"""
		Initializes the LocateCog with the given bot instance.

		Parameters:
		bot (commands.Bot): The bot instance to which this cog is added.
		"""
		self.bot = bot  # Store the bot instance for later use

	# Define a slash command for location lookup
	@app_commands.command(
		name="locate",
		description='Finds the address of a location within Thailand'
	)
	@app_commands.describe(
		location='The address of the location you want to locate (Default: Bangkok)',
		city='The city to search within (Default: Bangkok)'
	)
	async def locate_command(
		self,
		interaction: discord.Interaction,
		location: str,
		city: str = 'Bangkok'
	):
		"""
		A slash command to find the address of a location within Thailand.

		Parameters:
		interaction (discord.Interaction): The interaction object
		location (str): The address to locate
		city (str): The city to search within (default: 'Bangkok')
		"""
		try:
			# Sanitize the input to make it URL-safe
			sanitized_location = sanitize_url(location)
			sanitized_city = sanitize_url(city)

			# Construct the API request URL with the sanitized inputs
			api_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={sanitized_location},{sanitized_city}&key={GOOGLE_MAPS_API_KEY}"

			# Send a GET request to the Google Maps API with a timeout
			response = requests.get(api_url, timeout=5)
			logger.info(f"Successfully geocoded {location} in {city}")

			if response.status_code != 200:
				await interaction.response.send_message(f"{ERROR_MESSAGE} Try again some other time, I guess?")
				return

			# Parse the JSON response from the API
			response_data = response.json()

			# Check if there are any results in the response
			if not response_data.get('results'):
				await interaction.response.send_message(f"{ERROR_MESSAGE} Are you dumb? Or am I? \"{location.title()}\" in {city.title()} didn't show up on my radar.")
				logger.error('No results found')
				return

			# Extract the first result from the response
			first_result = response_data['results'][0]

			# Get the formatted address from the result
			formatted_address = first_result['formatted_address']

			# Extract latitude and longitude coordinates
			lat = first_result['geometry']['location']['lat']
			lng = first_result['geometry']['location']['lng']

			# Construct the output message with location details
			output = (
				f"📍 \"**{location.title()}**\" is located at **{formatted_address}**.\n"
				f"Here's a link to a map, you lazy ass: https://www.google.com/maps/place/{lat},{lng}"
			)
			logger.info('Outputting the success message')

			# Send the response back to Discord
			await interaction.response.send_message(output)

		except requests.exceptions.Timeout:
			# Handle timeout errors
			await interaction.response.send_message(f"{ERROR_MESSAGE} This is all taking too long, I'm out.")
			logger.error('Timeout error')
		except requests.RequestException:
			# Catch-all for other request-related errors
			await interaction.response.send_message(f"{ERROR_MESSAGE} Try again some other time, I guess?")
			logger.error('Unknown request error')


# Define the setup function to add the Cog to the bot
async def setup(bot: commands.Bot):
	"""
	A setup function to add the LocateCog to the bot.

	Parameters:
	bot (commands.Bot): The bot instance to which this cog is added.
	"""
	# Add the Cog to the bot
	await bot.add_cog(LocateCog(bot))
	logger.info("LocateCog loaded successfully")
