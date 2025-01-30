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

# Import the requests library for making HTTP requests
import requests

# Import the logging module for logging messages
import logging

# Import the discord library for creating Discord bots
import discord

# Import commands from discord.ext for creating bot commands
from discord.ext import commands

# Import app_commands from discord for creating slash commands
from discord import app_commands

# Import ERROR_MESSAGE constant
from config.config import ERROR_MESSAGE

# Import GOOGLE_MAPS_API_KEY constant from the config module
from config.config import GOOGLE_MAPS_API_KEY

# Import sanitize_url function from utils.helpers for sanitizing URLs
from utils.helpers import sanitize_url

# Configure the logging module to display INFO messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define the LocateCog class as a subclass of commands.Cog
# noinspection PyUnresolvedReferences
class LocateCog(commands.Cog):
	"""
	A Discord Cog for locating addresses within Thailand.
	"""

	# Initialize the LocateCog with a bot instance
	def __init__(self, bot: commands.Bot):
		"""
		Initializes the LocateCog with the given bot instance.

		Parameters:
		bot (commands.Bot): The bot instance to which this cog is added.
		"""
		# Assign the bot instance to self.bot
		self.bot = bot

	# Define a slash command named "locate" with a description
	@app_commands.command(name="locate", description='Finds the address of a location within Thailand')
	# Describe the parameters for the slash command

	@app_commands.describe(location='The address of the location you want to locate (Default: Bangkok)')
	# Define the asynchronous function that handles the "locate" command

	async def locate_command(self, interaction: discord.Interaction, location: str, city: str = 'Bangkok'):
		"""
		A slash command to find the address of a location within Thailand.

		Parameters:
		interaction (discord.Interaction): The interaction object representing the command invocation.
		location (str): The address of the location to locate.
		city (str): The city to search within (default: 'Bangkok').
		"""
		try:
			# Sanitize the location and city for URL safety
			sanitized_location = sanitize_url(location)
			sanitized_city = sanitize_url(city)

			# Construct the API URL for the Google Maps Geocoding API
			api_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={sanitized_location},{sanitized_city}&key={GOOGLE_MAPS_API_KEY}"

			# Send a GET request to the Google Maps API with a timeout of 5 seconds
			response = requests.get(api_url, timeout=5)
			logger.info(f"Successfully geocoded {location} in {city}")

			# Check if the response status code is not 200 (OK)
			if response.status_code != 200:
				# Send the original error message with the response text and status code
				await interaction.response.send_message(response.text + str(response.status_code))

				return

			# Parse the JSON response from the API
			response_data = response.json()

			# Check if the response contains no results
			if not response_data.get('results'):
				# Send the original "not found" message
				await interaction.response.send_message(f"{ERROR_MESSAGE} Are you dumb? Or am I? \"{location.title()}\" in {city.title()} didn't show up on my radar.")
				logger.error('No results found')

				return

			# Extract the first result from the response
			first_result = response_data['results'][0]

			# Get the formatted address from the result
			formatted_address = first_result['formatted_address']

			# Get the latitude and longitude from the result's geometry
			lat = first_result['geometry']['location']['lat']
			lng = first_result['geometry']['location']['lng']

			# Construct the original output message with the location details and a Google Maps link
			output = (
				f"📍 \"**{location.title()}**\" is located at **{formatted_address}**.\n"
				f"Here's a link to a map, you lazy ass: https://www.google.com/maps/place/{lat},{lng}"
			)
			logger.info('Outputting the success message')

			# Send the output message as a response to the interaction
			await interaction.response.send_message(output)

		except requests.exceptions.Timeout:
			# Handle timeout errors specifically
			await interaction.response.send_message(f"{ERROR_MESSAGE} This is all taking too long, I'm out.")
			logger.error('Timeout error')
		except requests.RequestException:
			# Log unexpected errors and notify the user with the original tone
			await interaction.response.send_message(f"{ERROR_MESSAGE} Try again some other time, I guess?")
			logger.error('Unknown request error')


# Define the asynchronous setup function to add the LocateCog to the bot
async def setup(bot: commands.Bot):
	"""
	A setup function to add the LocateCog to the bot.

	Parameters:
	bot (commands.Bot): The bot instance to which this cog is added.
	"""
	# Add an instance of LocateCog to the bot
	await bot.add_cog(LocateCog(bot))
	logger.info("LocateCog loaded successfully")
