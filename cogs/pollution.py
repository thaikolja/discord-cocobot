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

# Import the Discord API library for interacting with the Discord API
import discord

# Import the commands module from discord.ext to create bot commands
from discord.ext import commands

# Import the app_commands module from discord to create slash commands
from discord import app_commands

# Import configuration constants and API key from the config module
from config.config import ERROR_MESSAGE, ACQIN_API_KEY

# Import the sanitize_url function from utils.helpers to sanitize URLs
from utils.helpers import sanitize_url

# Import the datetime class from the datetime module for handling dates and times
from datetime import datetime

# Import the naturaltime function from the humanize module to format time in a human-readable way
from humanize import naturaltime


# Define a new Discord cog for handling pollution data
# noinspection PyUnresolvedReferences
class PollutionCog(commands.Cog):
	"""
	A Discord Cog for showing up-to-date pollution data and AQI in the entered city.
	"""

	# Initialize the cog with the bot instance
	def __init__(self, bot: commands.Bot):
		"""
		Initializes the PollutionCog with the given bot instance.

		Parameters:
		bot (commands.Bot): The bot instance to which this cog is added.
		"""
		# Assign the bot instance to the self.bot attribute
		self.bot = bot

	# Define a slash command for fetching pollution data
	@app_commands.command(name="pollution", description='Shows up-to-date pollution data and AQI in the specified city')
	@app_commands.describe(city='The city to check the pollution data for (Default: Bangkok)')
	async def pollution_command(self, interaction: discord.Interaction, city: str = 'Bangkok'):
		"""
		A slash command to show up-to-date pollution data and AQI in the entered city.

		Parameters:
		interaction (discord.Interaction): The interaction object representing the command invocation.
		city (str): The city to check the pollution data for (default is Bangkok).
		"""
		# Sanitize the city name for use in the URL and construct the API request URL
		api_url = sanitize_url(f'https://api.waqi.info/feed/{city}/?token={ACQIN_API_KEY}')

		# Make a GET request to the pollution API
		response = requests.get(api_url)

		# Check if the response was successful
		if not response.ok:
			# Send an error message if the request failed
			await interaction.response.send_message(f"{ERROR_MESSAGE} Looks like there's been some connection error. Give it another shot.")
			return

		# Parse the JSON response from the API
		data = response.json()

		# Check if the API returned a successful status
		if data['status'] != 'ok':
			# Send an error message if the city name is incorrect
			await interaction.response.send_message(f"{ERROR_MESSAGE} Check your spelling of \"{city}\" and give it another shot.")
			return

		# Extract the main data from the response
		data = data['data']

		# Get the AQI value from the data
		aqi = data['aqi']

		# Get the city name from the data
		city = data['city']['name']

		# Calculate how long ago the data was updated
		updated_ago = naturaltime(datetime.fromisoformat(data['time']['iso']))

		# Construct the base output message with AQI value
		pre_output = f"The PM2.5 level in **{city}** is at `{aqi}` **AQI**."

		# Determine the appropriate emoji and message based on AQI level
		if aqi <= 50:
			emoji, message = "🟢", "The air is so clean, it’s like a vacuum sealed coconut fresh off the tree. August Engelhardt would be proud (and probably try to worship it, too)."
		elif aqi <= 100:
			emoji, message = "🟡", "Decent air. Like a coconut: refreshing, but not life-changing."
		elif aqi <= 150:
			emoji, message = "🟠", "Not great, not terrible. Stay in, unless you fancy a diet of delusions. Wear a mask."
		elif aqi <= 200:
			emoji, message = "🔴", "Unhealthy. Breathing's like Engelhardt's coconut-only dreams. Wear a mask - and, no, it's not \"infringing on your freedom.\""
		else:
			emoji, message = "⚫️", "Apocalypse air! Even Engelhardt's coconuts couldn't save this. Mask up, or you'll be seeing coconuts soon."

		# Combine all elements into the final output message
		output = f"{emoji} {pre_output} {message} (Last checked: {updated_ago})"

		# Send the final message as a response to the interaction
		await interaction.response.send_message(output)


# Define the setup function to register the cog with the bot
async def setup(bot: commands.Bot):
	"""
	A setup function to add the PollutionCog to the bot.

	Parameters:
	bot (commands.Bot): The bot instance to which this cog is added.
	"""
	# Add the PollutionCog instance to the bot
	await bot.add_cog(PollutionCog(bot))
