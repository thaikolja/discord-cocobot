# Import the requests library for making HTTP requests
import requests

# Import the discord library
import discord

# Import commands from discord.ext
from discord.ext import commands

# Import app_commands from discord
from discord import app_commands

# Import Optional from typing for optional type hints
from typing import Optional

# Import sanitize_url function from utils.helpers
from utils.helpers import sanitize_url

# Import WEATHERAPI_API_KEY from config
from config.config import WEATHERAPI_API_KEY

# Import ERROR_MESSAGE from config
from config.config import ERROR_MESSAGE


# Define the WeatherCog class as a subclass of commands.Cog
# noinspection PyUnresolvedReferences
class WeatherCog(commands.Cog):
	# Initialize the WeatherCog with a bot instance
	def __init__(self, bot: commands.Bot):
		# Assign the bot instance to self.bot
		self.bot = bot

	# Define a slash command named "weather" with a description
	@app_commands.command(name="weather", description="Get the current weather for a location")
	# Describe the location and units parameters
	@app_commands.describe(
		location='The location you want the weather for.',
		units='Choose the unit system: Metric (°C) or Imperial (°F). Defaults to Metric if not specified.'
	)
	# Define choices for the units parameter
	@app_commands.choices(
		units=[
			app_commands.Choice(name="Civilized Units (°C)", value="metric"),
			app_commands.Choice(name="Freedom Units (°F)", value="imperial")
		]
	)
	# Define the weather_command function with interaction, location, and optional units parameters
	async def weather_command(
		self,
		interaction: discord.Interaction,
		location: str,
		units: Optional[app_commands.Choice[str]] = None
	):
		# Set units_value to "metric" if units is None, else set to units.value
		units_value = "metric" if units is None else units.value
		# Set unit_symbol based on units_value
		unit_symbol = "°C" if units_value == "metric" else "°F"
		# Construct the API URL with sanitized location
		api_url = f"https://api.weatherapi.com/v1/current.json?key={WEATHERAPI_API_KEY}&q={sanitize_url(location)}"

		# Try to make a GET request to the API URL
		try:
			# Make the GET request to the API URL
			response = requests.get(api_url)
			# Raise an exception for HTTP error responses
			response.raise_for_status()
		# Catch HTTP errors
		except requests.HTTPError as http_error:
			# Send an ephemeral error message to the user with details
			await interaction.response.send_message(
				f"{ERROR_MESSAGE} Looks like the connection to the weather API couldn't be established. {http_error}",
				ephemeral=True
			)
			# Exit the function
			return
		# Catch any other exceptions
		except ConnectionError:
			# Send a generic ephemeral error message to the user
			await interaction.response.send_message(
				f"{ERROR_MESSAGE} Give it another try.",
				ephemeral=True
			)
			# Exit the function
			return

		# Parse the JSON response from the API
		data = response.json()

		# Extract city name from the response data
		city = data['location']['name']

		# Extract country name from the response data
		country = data['location']['country']

		# Extract temperature based on units_value
		temperature = data['current']['temp_c'] if units_value == "metric" else data['current']['temp_f']

		# Extract feels_like temperature based on units_value
		feels_like = data['current']['feelslike_c'] if units_value == "metric" else data['current']['feelslike_f']

		# Extract humidity from the response data
		humidity = data['current']['humidity']

		# Extract weather condition text and convert to lowercase
		condition = data['current']['condition']['text'].lower()

		# Construct the output message with weather details
		output = (
			f"🌤️ The weather in **{city}**, **{country}** is currently {condition} with temperatures of `{temperature}{unit_symbol}` "
			f"(feels like `{feels_like}{unit_symbol}`). **Humidity** is at `{humidity}%`."
		)

		# Send the output message to the user
		await interaction.response.send_message(output, ephemeral=False)


# Define the setup function to add the WeatherCog to the bot
async def setup(bot: commands.Bot):
	# Add the WeatherCog to the bot
	await bot.add_cog(WeatherCog(bot))
