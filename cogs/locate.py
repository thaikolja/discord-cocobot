# Import the requests library for making HTTP requests
import requests

# Import the discord library for creating Discord bots
import discord

# Import commands from discord.ext for creating bot commands
from discord.ext import commands

# Import app_commands from discord for creating slash commands
from discord import app_commands

# Import ERROR_MESSAGE constant from the config module
from config.config import ERROR_MESSAGE

# Import GEOAPFIY_API_KEY constant from the config module
from config.config import GEOAPFIY_API_KEY

# Import sanitize_url function from utils.helpers for sanitizing URLs
from utils.helpers import sanitize_url


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
	@app_commands.describe(location='The address of the location you want to locate')
	# Define the asynchronous function that handles the "locate" command
	async def locate_command(self, interaction: discord.Interaction, location: str):
		"""
		A slash command to find the address of a location within Thailand.

		Parameters:
		interaction (discord.Interaction): The interaction object representing the command invocation.
		location (str): The address of the location to locate.
		"""
		# Sanitize the location URL
		locate_url = sanitize_url(location)

		# Construct the API URL with the sanitized location and API key
		url = f"https://api.geoapify.com/v1/geocode/search?name={locate_url}&country=Thailand&filter=countrycode:th&format=json&apiKey={GEOAPFIY_API_KEY}"

		# Make a GET request to the API
		response = requests.get(url)

		# Check if the response is not OK
		if not response.ok:
			# Return the error message if the request failed
			await interaction.response.send_message(ERROR_MESSAGE)

			return

		# Parse the JSON response
		data = response.json()

		# Get the first result from the response
		data = data['results'][0]

		# Get the name from the data, or use the location if name is not available
		name = data['name'] if 'name' in data else location

		# Get the latitude from the data
		lat = data['lat']

		# Get the longitude from the data
		lon = data['lon']

		# Get the formatted address from the data
		address = data['formatted']

		# Construct the output message with the location details and a Google Maps link
		output = (
			f"**{name}**, the location you've been looking for, is located at **{address}**. "
			f"Here's a link to a map: https://www.google.com/maps/search/?api=1&query={lat},{lon}"
		)

		# Send the output message as a response to the interaction
		await interaction.response.send_message(output)


# Define the asynchronous setup function to add the LocateCog to the bot
async def setup(bot: commands.Bot):
	"""
	A setup function to add the LocateCog to the bot.

	Parameters:
	bot (commands.Bot): The bot instance to which this cog is added.
	"""
	# Add an instance of LocateCog to the bot
	await bot.add_cog(LocateCog(bot))
