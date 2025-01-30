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

import requests

# Import Discord API library for bot functionality
import discord

# Import command handling from Discord extensions
from discord.ext import commands

# Import slash command functionality from Discord API
from discord import app_commands

# Import configuration constants and API key
from config.config import ERROR_MESSAGE, ACQIN_API_KEY

# Import URL sanitization utility function
from utils.helpers import sanitize_url

# Import datetime handling for time-related operations
from datetime import datetime

# Import human-readable time formatting
from humanize import naturaltime


# Define a new Discord cog for pollution data
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
		self.bot = bot  # Assign the bot instance to self.bot

	# Define a slash command for pollution data
	@app_commands.command(name="pollution", description='Shows up-to-date pollution data and AQI a specified city')
	@app_commands.describe(city='The city to check the pollution data for (Default: Bangkok)')
	async def pollution_command(self, interaction: discord.Interaction, city: str = 'Bangkok'):
		"""
		A slash command to show up-to-date pollution data and AQI in the entered city.

		Parameters:
		interaction (discord.Interaction): The interaction object representing the command invocation.
		city (str): The city to check the pollution data for (default is Bangkok).
		"""
		# Sanitize and construct the API URL with the city and API key
		api_url = sanitize_url(f'https://api.waqi.info/feed/{city}/?token={ACQIN_API_KEY}')  # Sanitize the city name for use in the URL

		# Make a GET request to the pollution API
		response = requests.get(api_url)  # Make a GET request to the API

		# Check if the response was successful
		if not response.ok:  # Check if the response is not OK
			# Send an error message if the request failed
			await interaction.response.send_message(
				f"{ERROR_MESSAGE} Looks like there's been some connection error. Give it another shot.")
			return  # Exit the function

		# Parse the JSON response from the API
		data = response.json()  # Parse the JSON response

		# Check if the API returned a successful status
		if data['status'] != 'ok':  # Check if the status in the response is not 'ok'
			# Send an error message if the city name is incorrect
			await interaction.response.send_message(f"{ERROR_MESSAGE} Check your spelling of \"{city}\" and give it another shot.")
			# Exit the function
			return

		# Extract the main data from the response
		data = data['data']  # Extract the data from the response

		# Get the AQI value from the data
		aqi = data['aqi']  # Get the AQI value from the data

		# Get the city name from the data
		city = data['city']['name']  # Get the city name from the data

		# Calculate how long ago the data was updated
		updated_ago = naturaltime(datetime.fromisoformat(data['time']['iso']))  # Get the last updated time in a human-readable format

		# Construct the base output message with AQI value
		pre_output = f"The PM2.5 level in **{city}** is at `{aqi}` **AQI**."  # Construct the pre-output message with the AQI value

		# Determine the appropriate emoji and message based on AQI level
		if aqi <= 50:
			emoji, message = "🟢", "The air is so clean, it’s like a vacuum sealed coconut fresh off the tree. August Engelhardt would be proud (and probably try to worship it, too)."
		elif aqi <= 100:
			emoji, message = "🟡", "Decent air. Like a coconut: refreshing, but not life-changing."
		elif aqi <= 150:
			emoji, message = "🟠", "Not great, not terrible. Stay in, unless you fancy a diet of delusions. Wear a mask."
		elif aqi <= 200:
			emoji, message = "🔴", "Unhealthy. Breathing's like Engelhardt's coconut-only dreams. Wear a mask - and, no, it's not \"infringing on your freedom.\""
		elif aqi <= 300:
			emoji, message = "🟣", "Very unhealthy. The air is a cult—suffocating your sanity, one breath at a time. A mask is no longer optional."
		else:
			emoji, message = "⚫️", "Apocalypse air! Even Engelhardt's coconuts couldn't save this. Mask up, or you'll be seeing coconuts soon."

		# Combine all elements into the final output message
		output = f"{emoji} {pre_output} {message} (Last checked: {updated_ago})"  # Combine everything into the output

		# Send the final message as a response to the interaction
		await interaction.response.send_message(output)  # Send the output message as a response to the interaction


# Setup function to register the cog with the bot
async def setup(bot: commands.Bot):
	"""
	A setup function to add the PollutionCog to the bot.

	Parameters:
	bot (commands.Bot): The bot instance to which this cog is added.
	"""
	# Add the PollutionCog instance to the bot
	await bot.add_cog(PollutionCog(bot))  # Add an instance of PollutionCog to the bot
