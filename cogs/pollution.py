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

# Import the discord library for creating Discord bots
import discord

# Import commands from discord.ext for creating bot commands
from discord.ext import commands

# Import app_commands from discord for creating slash commands
from discord import app_commands

# Import ERROR_MESSAGE and ACQIN_API_KEY from the config module
from config.config import ERROR_MESSAGE, ACQIN_API_KEY

# Import sanitize_url function from utils.helpers for sanitizing URLs
from utils.helpers import sanitize_url

# Import datetime for handling date and time
from datetime import datetime

# Import naturaltime from humanize for human-readable time differences
from humanize import naturaltime


# noinspection PyUnresolvedReferences
class PollutionCog(commands.Cog):
	"""
	A Discord Cog for showing up-to-date pollution data and AQI in the entered city.
	"""

	def __init__(self, bot: commands.Bot):
		"""
		Initializes the PollutionCog with the given bot instance.

		Parameters:
		bot (commands.Bot): The bot instance to which this cog is added.
		"""
		self.bot = bot  # Assign the bot instance to self.bot

	@app_commands.command(name="pollution", description='Shows up-to-date pollution data and AQI a specified city')
	@app_commands.describe(city='The city to check the pollution data for (Default: Bangkok)')
	async def pollution_command(self, interaction: discord.Interaction, city: str = 'Bangkok'):
		"""
		A slash command to show up-to-date pollution data and AQI in the entered city.

		Parameters:
		interaction (discord.Interaction): The interaction object representing the command invocation.
		city (str): The city to check the pollution data for (default is Bangkok).
		"""
		api_url = sanitize_url(f'https://api.waqi.info/feed/{city}/?token={ACQIN_API_KEY}')  # Sanitize the city name for use in the URL
		response = requests.get(api_url)  # Make a GET request to the API

		if not response.ok:  # Check if the response is not OK
			await interaction.response.send_message(
				f"{ERROR_MESSAGE} Looks like there's been some connection error. Give it another shot.")  # Send an error message if the request failed
			return  # Exit the function

		data = response.json()  # Parse the JSON response

		if data['status'] != 'ok':  # Check if the status in the response is not 'ok'
			await interaction.response.send_message(f"{ERROR_MESSAGE} Check your spelling of \"{city}\" and give it another shot.")  # Send an error message if the city name is
			# incorrect
			return  # Exit the function

		data = data['data']  # Extract the data from the response
		aqi = data['aqi']  # Get the AQI value from the data
		city = data['city']['name']  # Get the city name from the data
		updated_ago = naturaltime(datetime.fromisoformat(data['time']['iso']))  # Get the last updated time in a human-readable format

		pre_output = f"The PM2.5 level in **{city}** is at `{aqi}` **AQI**."  # Construct the pre-output message with the AQI value

		# Determine the emoji and message based on the AQI value
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

		output = f"{emoji} {pre_output} {message} (Last checked: {updated_ago})"  # Combine everything into the output
		await interaction.response.send_message(output)  # Send the output message as a response to the interaction


async def setup(bot: commands.Bot):
	"""
	A setup function to add the PollutionCog to the bot.

	Parameters:
	bot (commands.Bot): The bot instance to which this cog is added.
	"""
	await bot.add_cog(PollutionCog(bot))  # Add an instance of PollutionCog to the bot
