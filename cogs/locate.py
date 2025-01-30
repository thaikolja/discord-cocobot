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

import requests  # For making HTTP requests to external APIs
import logging  # For logging important events and errors

# Import Discord-related modules for bot functionality
import discord  # Main Discord API library
from discord.ext import commands  # For creating bot commands
from discord import app_commands  # For slash command functionality

# Import configuration constants and helper functions
from config.config import ERROR_MESSAGE  # Custom error message format
from config.config import GOOGLE_MAPS_API_KEY  # API key for Google Maps
from utils.helpers import sanitize_url  # Function to sanitize URLs

# Configure logging to show timestamps and set the logging level
logging.basicConfig(level=logging.INFO)  # Set logging level to INFO
logger = logging.getLogger(__name__)  # Create logger instance for this module


# Define a new Cog class for location-based commands
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

			# Check if the response was successful (status code 200)
			if response.status_code != 200:
				await interaction.response.send_message(response.text + str(response.status_code))
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
