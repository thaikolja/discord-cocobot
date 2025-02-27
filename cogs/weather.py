# Copyright and licensing information
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

# Import the discord library for interacting with the Discord API
import discord

# Import the commands module from discord.ext to create bot commands
from discord.ext import commands

# Import the app_commands module from discord to define slash commands
from discord import app_commands

# Import the sanitize_url function from utils.helpers to clean location inputs
from utils.helpers import sanitize_url

# Import the WEATHERAPI_API_KEY from config to access the weather API key
from config.config import WEATHERAPI_API_KEY

# Import the ERROR_MESSAGE from config to access the error message template
from config.config import ERROR_MESSAGE


# Define a class named WeatherCog that inherits from commands.Cog
# noinspection PyUnresolvedReferences
class WeatherCog(commands.Cog):
	"""
	A Discord Cog for fetching and displaying the current weather for a specified location.
	"""

	# Define the constructor method to initialize the WeatherCog with the bot instance
	def __init__(self, bot: commands.Bot):
		"""
		Initializes the WeatherCog with the given bot instance.

		Parameters:
		bot (commands.Bot): The bot instance to which this cog is added.
		"""
		# Assign the bot instance to the instance variable self.bot
		self.bot = bot

	# Define a slash command named "weather" with a description
	@app_commands.command(name="weather", description="Get the current weather for a location")
	# Describe the parameters for the "weather" command
	@app_commands.describe(
		location='The location you want the weather for (Default: Bangkok)',
		units='Choose the unit system: Metric (°C) or Imperial (°F). (Default: Metric)'
	)
	# Define choices for the units parameter
	@app_commands.choices(
		units=[
			app_commands.Choice(name="Civilized Units (°C)", value="metric"),
			app_commands.Choice(name="Freedom Units (°F)", value="imperial")
		]
	)
	# Define the asynchronous weather_command method to handle the "weather" command
	async def weather_command(
		self,
		interaction: discord.Interaction,
		location: str = 'Bangkok',
		units: str = 'metric'
	):
		"""
		A slash command to get the current weather for a specified location.

		Parameters:
		interaction (discord.Interaction): The interaction object representing the command invocation.
		location (str): The location for which to get the current weather.
		units (Optional[app_commands.Choice[str]]): The unit system for temperature. Defaults to Metric if not specified.
		"""
		# Determine the units to use for temperature; default to 'metric' if units is None
		units_value = units if units else 'metric'
		# Set the unit symbol based on the units_value
		unit_symbol = "°C" if units_value == "metric" else "°F"

		# Construct the API URL with the sanitized location
		api_url = f"https://api.weatherapi.com/v1/current.json?key={WEATHERAPI_API_KEY}&q={sanitize_url(location)}"

		# Make the API request to fetch weather data
		response = requests.get(api_url)

		# Check if the response was successful
		if not response.ok:
			# If the response is not successful, send an error message
			await interaction.response.send_message(
				f"{ERROR_MESSAGE} That's a nope. Are you sure **{location}** even exists?!"
			)
			return

		# Parse the JSON response from the API
		data = response.json()

		# Extract the city name from the response data
		city = data['location']['name']
		# Extract the country name from the response data
		country = data['location']['country']
		# Extract the temperature based on the units_value
		temperature = data['current']['temp_c'] if units_value == "metric" else data['current']['temp_f']
		# Extract the "feels like" temperature based on the units_value
		feels_like = data['current']['feelslike_c'] if units_value == "metric" else data['current']['feelslike_f']
		# Extract the humidity percentage from the response data
		humidity = data['current']['humidity']
		# Extract the weather condition text and convert it to lowercase
		condition = data['current']['condition']['text'].lower()

		# Construct the output message with weather details
		output = (
			f"🌤️ The weather in **{city}**, **{country}** is currently {condition} with temperatures of `{temperature}{unit_symbol}` "
			f"(feels like `{feels_like}{unit_symbol}`). **Humidity** is at `{humidity}`%."
		)

		# Send the output message to the user
		await interaction.response.send_message(output)


# Define the setup function to add the WeatherCog to the bot
async def setup(bot: commands.Bot):
	"""
	A setup function to add the WeatherCog to the bot.

	Parameters:
	bot (commands.Bot): The bot instance to which this cog is added.
	"""
	# Add the WeatherCog to the bot
	await bot.add_cog(WeatherCog(bot))
