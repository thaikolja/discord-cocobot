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

# Import the discord library
import discord

# Import commands from discord.ext
from discord.ext import commands

# Import app_commands from discord
from discord import app_commands

# Import the datetime class from the datetime module for handling date and time
from datetime import datetime

# Import the naturaltime function from the humanize module for human-readable time
from humanize import naturaltime

# Import constants ERROR_MESSAGE and CURRENCYAPI_API_KEY from the config module
from config.config import ERROR_MESSAGE, CURRENCYAPI_API_KEY


# Define the ExchangerateCog class as a subclass of commands.Cog
# noinspection PyUnresolvedReferences
class ExchangerateCog(commands.Cog):
	"""
	A Discord Cog for fetching and displaying the current exchange rate between two currencies.
	"""

	# Initialize the ExchangerateCog with a bot instance
	def __init__(self, bot: commands.Bot):
		"""
		Initializes the ExchangerateCog with the given bot instance.

		Parameters:
		bot (commands.Bot): The bot instance to which this cog is added.
		"""
		self.bot = bot

	# Define a slash command named "exchangerate" with a description
	@app_commands.command(name="exchangerate", description='Get the current exchange rate between two currencies')
	# Describe the parameters for the slash command
	@app_commands.describe(
		from_currency='The currency to convert from (Default: USD)',
		to_currency='The currency to convert to (Default: THB)',
		amount='The amount of money to convert (Default: 1)')
	# Define the asynchronous function that handles the "exchangerate" command
	async def exchangerate_command(self, interaction: discord.Interaction, from_currency: str = 'USD', to_currency: str = 'THB', amount: int = 1):
		"""
		A slash command to get the current exchange rate between two currencies.

		Parameters:
		interaction (discord.Interaction): The interaction object representing the command invocation.
		from_currency (str): The currency to convert from. Defaults to 'USD'.
		to_currency (str): The currency to convert to. Defaults to 'THB'.
		amount (int): The amount of money to convert. Defaults to 1.
		"""
		# Strip and convert the currency codes to uppercase
		from_currency = from_currency.strip().upper()
		to_currency = to_currency.strip().upper()

		# Check if the currency codes are valid (3 letters)
		if len(to_currency) != 3 or len(from_currency) != 3:
			# Send an error message if the currency codes are invalid
			await interaction.response.send_message(f"{ERROR_MESSAGE} Invalid currency codes. Please use 3-letter currency codes like `USD`, `THB`, `EUR`, etc.")

		# Construct the API URL with the sanitized currency codes and API key
		api_url = f'https://api.currencyapi.com/v3/latest?apikey={CURRENCYAPI_API_KEY}&currencies={to_currency}&base_currency={from_currency}'

		# Make a GET request to the API URL
		response = requests.get(api_url)

		# Check if the response status is not OK (i.e., not in the 200-399 range)
		if not response.ok:
			# Construct an error message if the request was unsuccessful
			output = f"{ERROR_MESSAGE} Couldn't convert **{from_currency}** into **{to_currency}**. Are you sure they even exist? Coconut money doesn't count."
		else:
			# Parse the JSON data from the response
			data = response.json()

			# Convert the last updated time to a human-readable format
			updated_humanized = naturaltime(datetime.strptime(data['meta']['last_updated_at'], '%Y-%m-%dT%H:%M:%SZ'))

			# Calculate the converted value and round it to 2 decimal places
			value = round(data['data'][to_currency]['value'] * amount, 2)

			# Construct the output message with the exchange rate details
			output = f"💰 `{amount}` **{from_currency}** is currently `{value}` **{to_currency}** (Updated: {updated_humanized})"

		# Send the output message to the user
		await interaction.response.send_message(output)


# Define the asynchronous setup function to add the ExchangerateCog to the bot
async def setup(bot: commands.Bot):
	"""
	A setup function to add the ExchangerateCog to the bot.

	Parameters:
	bot (commands.Bot): The bot instance to which this cog is added.
	"""
	# Add an instance of ExchangerateCog to the bot
	await bot.add_cog(ExchangerateCog(bot))
