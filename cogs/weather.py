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

# Import the logging library for logging purposes
import logging  # Import the logging module for logging

# Import the aiohttp library for making asynchronous HTTP requests
import aiohttp  # Import the aiohttp client for async requests

# Import the discord library for interacting with the Discord API
import discord  # Import the discord library for API interactions

# Import the commands module from discord.ext for command handling
from discord.ext import commands  # Import commands extension for handling bot commands

# Import the app_commands module from discord for slash command support
from discord import app_commands  # Import app_commands for slash commands

# Import the sanitize_url function from the utils.helpers module
from utils.helpers import sanitize_url  # Import a function to sanitize URLs

# Import the WEATHERAPI_API_KEY and ERROR_MESSAGE constants from the config.config module
from config.config import WEATHERAPI_API_KEY, ERROR_MESSAGE  # Import API key and error message

# Set up the logger for this file
logger = logging.getLogger(__name__)  # Initialize a logger for this module


# Define a class WeatherCog that inherits from commands.Cog
class WeatherCog(commands.Cog):
	"""
	A Cog representing weather-related commands for a Discord bot.
	"""

	# Initialize the WeatherCog with a bot instance
	def __init__(self, bot: commands.Bot):
		"""
		Initializes the WeatherCog with a bot instance and sets up an aiohttp session.
		"""
		self.bot = bot  # Assign the bot object to the instance
		self.session = aiohttp.ClientSession()  # Create an aiohttp client session

	# Ensure the aiohttp session is closed when the cog is unloaded
	async def cog_unload(self):
		"""
		Closes the aiohttp session when the cog is unloaded.
		"""
		await self.session.close()  # Close the aiohttp session

	# Define a slash command with the name 'weather' and a description
	@app_commands.command(name="weather", description="Get the current weather for a location")
	# Describe the parameters for the weather command
	@app_commands.describe(
		location='The location you want the weather for (Default: Bangkok)',
		units='Choose the unit system: Metric (°C) or Imperial (°F). (Default: Metric)'
	)
	# Provide choices for the units parameter
	@app_commands.choices(
		units=[
			app_commands.Choice(name="Civilized Units (°C)", value="metric"),
			app_commands.Choice(name="Freedom Units (°F)", value="imperial")
		]
	)
	# Define the asynchronous weather_command function
	async def weather_command(
		self,
		interaction: discord.Interaction,
		location: str = 'Bangkok',  # Set the default location to Bangkok
		units: app_commands.Choice[str] = None  # Use the Choice object directly or default later
	):
		#: Defer the interaction response to avoid timeouts
		await interaction.response.defer(ephemeral=False)  # Defer the response

		# Determine units, default to metric if not provided or invalid
		units_value = units.value if units else 'metric'  # Set units value
		unit_symbol = "°C" if units_value == "metric" else "°F"  # Set the unit symbol
		temp_key = 'temp_c' if units_value == "metric" else 'temp_f'  # Set the temperature key
		feelslike_key = 'feelslike_c' if units_value == "metric" else 'feelslike_f'  # Set the feelslike key

		# Sanitize the location input
		sanitized_location = sanitize_url(location)  # Sanitize the location input
		# Construct the API URL using the sanitized location and API key
		api_url = f"https://api.weatherapi.com/v1/current.json?key={WEATHERAPI_API_KEY}&q={sanitized_location}"  # Construct the API URL

		try:
			# Use the async session to send a GET request
			async with self.session.get(api_url, timeout=10) as response:  # Send GET request
				# Raise an exception if the request was unsuccessful (status code >= 400)
				response.raise_for_status()  # Raise exception if not OK
				# Parse the response JSON data asynchronously
				data = await response.json()  # Parse JSON response

			# Validate essential keys exist before trying to access nested data
			if not data or 'location' not in data or 'current' not in data:
				# Log an error message if the data is incomplete
				logger.error(f"Incomplete weather data received for {location}. Response: {data}")  # Log incomplete data
				# Send a follow-up message to the interaction with an error message
				await interaction.followup.send(
					f"{ERROR_MESSAGE} Received incomplete data from the weather service. The API might have changed or data could be missing."  # Send incomplete data error
				)
				# Exit the function if essential data points are missing
				return  # Return early if data is incomplete

			# Extract location data safely using .get()
			location_data = data.get('location', {})  # Extract location data
			# Extract current data safely using .get()
			current_data = data.get('current', {})  # Extract current weather data
			# Extract condition data safely using .get()
			condition_data = current_data.get('condition', {})  # Extract condition data

			# Extract the city name from the location data, defaulting to 'Unknown City'
			city = location_data.get('name', 'Unknown City')  # Extract city name
			# Extract the country name from the location data, defaulting to 'Unknown Country'
			country = location_data.get('country', 'Unknown Country')  # Extract country name
			# Extract the temperature from the current data, using the appropriate key
			temperature = current_data.get(temp_key)  # Extract temperature
			# Extract the feels-like temperature from the current data, using the appropriate key
			feels_like = current_data.get(feelslike_key)  # Extract feels-like temperature
			# Extract the humidity from the current data
			humidity = current_data.get('humidity')  # Extract humidity
			# Extract the condition text from the condition data, defaulting to 'unknown condition'
			condition = condition_data.get('text', 'unknown condition').lower()  # Extract condition text
			# Extract the condition icon URL from the condition data, prefix with 'https:' if available
			icon_url = "https:" + condition_data.get('icon') if condition_data.get('icon') else None  # Extract icon URL

			# Check if essential data points were retrieved successfully
			if temperature is None or feels_like is None or humidity is None:
				# Log an error message if essential data points are missing
				logger.error(f"Missing key weather metrics for {location}. Data: {current_data}")  # Log missing data
				# Send a follow-up message to the interaction with an error message
				await interaction.followup.send(
					f"{ERROR_MESSAGE} Failed to parse essential weather details. The API might have changed or data could be corrupt."  # Send missing data error
				)
				# Exit the function if essential data points are missing
				return  # Exit on missing data

			# Create a Discord Embed for richer output
			embed = discord.Embed(
				title=f"Weather in {city}, {country}",
				description=f"Currently **{condition}**.",
				color=discord.Color.blue()  # Use the blue color
			)  # Create a new embed
			# Set the thumbnail of the embed if an icon URL is available
			if icon_url:
				embed.set_thumbnail(url=icon_url)  # Set the thumbnail

			# Add fields to the embed with temperature, feels-like temperature, and humidity
			embed.add_field(name="Temperature", value=f"`{temperature}{unit_symbol}`", inline=True)  # Add temperature field
			embed.add_field(name="Feels Like", value=f"`{feels_like}{unit_symbol}`", inline=True)  # Add feels-like field
			embed.add_field(name="Humidity", value=f"`{humidity}%`", inline=True)  # Add humidity field

			# Set the footer of the embed with the requester's name and units
			embed.set_footer(text=f"Units: {units_value.capitalize()}")  # Set the footer
			# Set the timestamp of the embed to the current UTC time
			embed.timestamp = discord.utils.utcnow()  # Set the embed timestamp

			# Send the embed as a follow-up
			await interaction.followup.send(embed=embed)  # Send the embed

		# Handle HTTP errors specifically
		except aiohttp.ContentTypeError as e:
			# Log an error message with the exception details
			logger.error(f"JSON Decode Error for {location}: {e}. Response status: {response.status}, content type: {response.content_type}")  # Log JSON decode error
			# Send a generic decoding error message as a follow-up
			await interaction.followup.send(
				f"{ERROR_MESSAGE} The weather service sent back gibberish instead of data. Possibly a configuration issue."  # Send JSON error message
			)
		except aiohttp.ClientResponseError as e:
			# Log an error message with the status code and message
			logger.error(f"HTTP error {e.status} for {location}: {e.message}")  # Log the HTTP error
			# Construct an error message for the user
			error_message = f"{ERROR_MESSAGE} The weather service responded with an error ({e.status}). Please check the location or try again later."  # Initialize error message
			# Override the error message for the 401 unauthorized status code
			if e.status == 401:
				error_message = f"{ERROR_MESSAGE} Invalid API key. Check the configuration."  # Adjust error message for 401 error
			# Override the error message for specific status (e.g., 400 Bad Request)
			elif e.status == 400:  # Handle 400 Bad Request specifically
				error_message = f"{ERROR_MESSAGE} Invalid location: '{location}'. Please verify if the location is correct."  # Adjust error message for 400 error
			# Send the error message as a follow-up
			await interaction.followup.send(error_message)  # Send the error message

		# Handle other aiohttp/network related errors
		except aiohttp.ClientError as e:
			# Log an error message with the exception details
			logger.error(f"AIOHTTP ClientError during weather API call for {location}: {e}")  # Log client error
			# Send a network error message as a follow-up
			await interaction.followup.send(
				f"{ERROR_MESSAGE} Couldn't reach the weather service. Check your network or try again."  # Send network error message
			)
		# Handle timeouts
		except TimeoutError:
			# Log a timeout error message
			logger.error(f"Request timed out for weather API call for {location}")  # Log a timeout error
			# Send a timeout error message as a follow-up
			await interaction.followup.send(
				f"{ERROR_MESSAGE} The weather service took too long to respond. The server might be napping."  # Send timeout error message
			)
		# Handle any other unexpected exceptions
		except Exception as e:
			# Log an exception message with a traceback
			logger.exception(f"Unexpected error in weather command for {location}: {e}")  # Log unexpected error
			# Send a generic unexpected error message as a follow-up
			await interaction.followup.send(
				f"{ERROR_MESSAGE} An unexpected error occurred. I blame cosmic rays. Or missing semicolons."  # Send unexpected error message
			)


# Define a function to add the WeatherCog to the bot
async def setup(bot: commands.Bot):
	"""
	A setup function to add the WeatherCog to the bot.
	"""
	await bot.add_cog(WeatherCog(bot))  # Add the WeatherCog to the provided bot instance
