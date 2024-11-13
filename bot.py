# Import the os library for interacting with the operating system
import os

# Import the discord library for creating a Discord bot
import discord

# Import the requests library for making HTTP requests
import requests

# Use an alias for the time module to avoid conflicts
import time as std_time

# Import the app_commands library for creating Discord bot commands
from discord import app_commands

# Import the Translator library for translating text
# noinspection PyProtectedMember
from googletrans import Translator, LANGUAGES

# Import the load_dotenv function for loading environment variables from a .env file
from dotenv import load_dotenv

# Import the sub function for regular expression substitution
import re

# Import the humanize library for human-readable date and time
import humanize

# Import the datetime class for working with dates and times
from datetime import datetime

# Load environment variables from a .env file
load_dotenv()

# Define a constant for the host name
# HOST will be used to check if the current host is the server
HOST: str = 'host.yanawa.io'

# Define a constant for the Discord bot token
# BOT_ACCESS_TOKEN will be used to authenticate the Discord bot
BOT_ACCESS_TOKEN: str = os.getenv('BOT_ACCESS_TOKEN')

# Define a constant for the Discord guild ID
# SERVER_ID will be used to identify the Discord guild
SERVER_ID: str = os.getenv('SERVER_ID')

# Define a constant for the LocalTime API key
# LOCALTIME_API_KEY will be used to make requests to the LocalTime API
LOCALTIME_API_KEY: str = os.getenv('LOCALTIME_API_KEY')

# Define a constant for the Weather API key
# WEATHERAPI_API_KEY will be used to make requests to the Weather API
WEATHERAPI_API_KEY: str = os.getenv('WEATHERAPI_API_KEY')

# Define a constant for the Currency API key
# CURRENCYAPI_API_KEY will be used to make requests to the Currency API
CURRENCYAPI_API_KEY: str = os.getenv('CURRENCYAPI_API_KEY')


# Define a custom Discord client class
class Cocobot(discord.Client):
	"""
	A custom Discord client class for the Cocobot.
	"""

	version: str = '1.2.2'

	# Initialize the client with default intents
	def __init__(self):
		# Create a new instance of the discord.Intents class
		intents: discord.Intents = discord.Intents.default()
		# noinspection PyDunderSlots,PyUnresolvedReferences
		intents.message_content = True

		# Call the superclass constructor
		super().__init__(intents=intents)

		# Create a new instance of the app_commands.CommandTree class
		self.tree: app_commands.CommandTree = app_commands.CommandTree(self)

		# Create a new instance of the Translator class
		self.translator: Translator = Translator()

	# Define a setup hook for the client
	async def setup_hook(self) -> None:
		"""
		A setup hook for the client.
		"""
		# Create a new instance of the discord.Object class for the guild
		guild: discord.Object = discord.Object(id=SERVER_ID)
		# Copy global commands to the guild
		self.tree.copy_global_to(guild=guild)
		# Sync the command tree for the guild
		await self.tree.sync(guild=guild)


# Create a new instance of the Cocobot class
client: Cocobot = Cocobot()


# This is the keyword you're listening for

@client.event
async def on_ready():
	"""
	An event handler that is called when the bot is ready.
	"""
	print(f'Logged in as {client.user}!')


last_triggered = {}


@client.event
async def on_message(message):
	"""
	An event handler that is called when a message is received.
	"""
	if message.author == client.user:
		return

	# Regex to match 'tate' with optional spaces before or after, case-insensitive
	pattern = r"(?<!\w)tate(?!\w)(?=\s|[.!?,;]|\b)"

	# Check if the message contains the exact word 'tate' (case-insensitive)
	if re.search(pattern, message.content.strip(), re.IGNORECASE):
		current_time = std_time.time()  # Use std_time to call the correct time function

		# Check if the user has triggered the command before and if the cooldown has passed
		if message.author.id in last_triggered:
			last_time = last_triggered[message.author.id]
			if current_time - last_time < 1800:
				await message.channel.send(
					"🕺 The Bottom G is exhausted from all the Bottom-G'ing, give him half 'n hour or so!"
				)
				return

		# Send the GIF
		await message.channel.send('https://media1.tenor.com/m/fyrqnSBR4gcAAAAd/bottom-g-andrew-tate.gif')

		# Update the last triggered time for this user
		last_triggered[message.author.id] = current_time


# Define an event handler that is called when the bot is ready
@client.event
async def on_ready() -> None:
	"""
	An event handler that is called when the bot is ready.
	"""
	# Print a message to the console to indicate that the bot is ready
	print(f'Bot is ready. Logged in as {client.user} (ID: {client.user.id})')
	# Print a separator line
	print('------')
	# Change the bot's presence to online
	await client.change_presence(
		status=discord.Status.online,
		activity=discord.Game(name=" with my 🥥")
	)


# Define a command to show the current exchange rate
# noinspection PyUnresolvedReferences
@client.tree.command(
	name="exchangerate",
	description="Show the current exchange rate"
)
@app_commands.describe(
	from_currency="The currency to convert from (Default: USD)",
	to_currency="The currency to convert to (Default: THB)",
	amount="The amount to convert (Default: 1)")
async def exchangerate(
	interaction: discord.Interaction,
	from_currency: str = 'USD',
	to_currency: str = 'THB',
	amount: float = 1.00) -> None:
	"""
	A command to show the current exchange rate.
	"""
	output: str = ''
	try:
		# Convert the from_currency and to_currency to uppercase
		from_currency: str = from_currency.upper()
		to_currency: str = to_currency.upper()

		# Remove non-numeric characters from the amount
		amount = float(re.sub('[^0-9.]', '', str(amount)))

		# Remove non-alphanumeric characters from the from_currency and to_currency
		from_currency: str = re.sub('[^A-Z]', '', from_currency)[:3]
		to_currency: str = re.sub('[^A-Z]', '', to_currency)[:3]

		# Construct the API URL for the exchange rate API
		api_url: str = f'https://api.currencyapi.com/v3/latest?apikey={CURRENCYAPI_API_KEY}&currencies={to_currency}&base_currency={from_currency}'

		# Make a GET request to the API
		response = requests.get(api_url)
		response.raise_for_status()
		response = response.json()

		# Check if the response contains an error
		if 'errors' in response:
			# Check if the error is related to the base currency
			if 'base_currency' in response['errors']:
				# Set the output to an error message
				output = f"🥥 Something's cracked, and it's **not** the coconut! Are you sure **{from_currency}** is a real currency and not just coconut money?"
			# Check if the error is related to the currencies
			elif 'currencies' in response['errors']:
				# Set the output to an error message
				output = f"🥥 Something's cracked, and it's **not** the coconut! Are you sure **{to_currency}** is a real currency and not just coconut money?"
		else:
			# Extract the value and last updated time from the response
			value = response['data'][to_currency]['value']
			last_updated = humanize.naturaltime(datetime.fromisoformat(response['meta']['last_updated_at']))

			# Calculate the converted value
			calculated_value = float(value) * float(amount)

			# Set the output to the converted value and last updated time
			output = f'💰 **{amount:.2f} {from_currency}** is currently worth **{calculated_value:.3f} {to_currency}** (last updated {last_updated})'
	except requests.RequestException:
		output = f"🥥 Something's cracked, and it's **not** the coconut! ¯\\_(ツ)_/¯"

	# Send the output to the interaction
	await interaction.response.send_message(output)


# Define a command to show the current weather in a city or country
# noinspection PyUnresolvedReferences
@client.tree.command(name="weather", description="Show the current weather in a city or country")
@app_commands.describe(location="The city or country to show the current weather (Default: Bangkok)")
async def weather(interaction: discord.Interaction, location: str = 'Bangkok') -> None:
	"""
	A command to show the current weather in a city or country.
	"""
	try:
		# Remove non-alphanumeric characters from the location
		location = re.sub(r'[^-\w\s]', '', location).replace(' ', '%20')
		# Check if the location is not empty
		if not location:
			output = "🥥 Something's cracked, and it's **not** the coconut! That doesn't look like a valid location. Try again!"
		else:
			# Construct the API URL for the weather API
			api_url = f'https://api.weatherapi.com/v1/current.json?key={WEATHERAPI_API_KEY}&q={location}'
			# Make a GET request to the API
			response = requests.get(api_url)
			response.raise_for_status()
			response = response.json()

			# Extract the current weather time, city, temperature, condition, feels like, and humidity from the response
			current_weather_time = response['location']['localtime']
			city = response['location']['name']
			temperature_c = response['current']['temp_c']
			condition = str(response['current']['condition']['text'])
			feels_like = response['current']['feelslike_c']
			humidity = response['current']['humidity']
			# Set the output to the current weather information
			output = (
				f"🌤️ It's currently ({current_weather_time}) **{temperature_c}°C** in **{city}** which feels more like *"
				f"*{feels_like}°C**. Weather condition: **{condition}**. Humidity: **{humidity}%**"
			)
	except requests.RequestException:
		output = f"🥥 Something's cracked, and it's **not** the coconut! ¯\\_(ツ)_/¯"

	# Send the output to the interaction
	await interaction.response.send_message(output)


# Define a command to translate text into a target language
# noinspection PyUnresolvedReferences
@client.tree.command(name="translate", description="Translate text into a target language")
@app_commands.describe(
	# Describe the text argument
	text="The text in English to translate",
	# Describe the language argument
	language="Target language (e.g., 'es' or 'spanish' for Spanish)"
)
async def translate(interaction: discord.Interaction, text: str, language: str) -> None:
	"""
	A command to translate text into a target language.
	"""
	try:
		# Create a new instance of the Translator class
		translator = client.translator
		# Convert the language to lowercase
		language = language.lower()

		# Check if the language is valid
		if language not in LANGUAGES and language not in LANGUAGES.values():
			# Send an error message to the interaction
			await interaction.response.send_message(
				"🛑 What kind of language is that supposed to be?! Did a coconut fall on your head or what? Run "
				"`/languages` to see what languages I can translate.")
			# Return from the function
			return

		# Translate the text
		translation = translator.translate(text, dest=language)
		# Send the translation to the interaction
		await interaction.response.send_message(
			f'🌏 **Translation:** {translation.text}')
	except TypeError as error:
		# Send an error message to the interaction
		await interaction.response.send_message(
			f"🥥 Something's cracked, and it's **not** the coconut! ¯\\_(ツ)_/¯ ({error})")


# Define a command to show the current time in a city or country
# noinspection PyUnresolvedReferences
@client.tree.command(name="time", description="Show the current time a city or country")
@app_commands.describe(location="The city or country to show the current time")
async def time(interaction: discord.Interaction, location: str = 'Bangkok') -> None:
	"""
	A command to show the current time in a city or country.
	"""
	try:
		# Remove non-alphanumeric characters from the location
		location = re.sub(r'[^-\w\s]', '', location).replace(' ', '%20')

		# Check if the location is not empty
		if not location:
			output = "🥥 Something's cracked, and it's **not** the coconut! Please enter a valid location."
		else:
			# Construct the API URL for the LocalTime API
			api_url = f'https://api.ipgeolocation.io/timezone?apiKey={LOCALTIME_API_KEY}&location={location}'

			# Make a GET request to the API
			response = requests.get(api_url)
			response.raise_for_status()
			response = response.json()

			# Check if the response contains the expected data
			if 'geo' in response:
				# Extract the city and country from the response
				city = response['geo']['city']
				country = response['geo']['country']

				# Extract the current time from the response
				current_time = response.get('date_time_txt')

				# Check if the current time is a string
				if type(current_time) == str:
					# If the city is not empty, include it in the output
					if len(city) >= 3:
						output = f'🕐 The current time in **{city}**, **{country}** is **{current_time}**'

					# Otherwise, only include the country in the output
					else:
						output = f'🕓 The current time in **{country}** is **{current_time}**'
				else:
					# If the current time is not a string, send an error message
					output = "🥥 Something's cracked, and it's **not** the coconut! That doesn't look like a real location. Are you making things up?!"
			else:
				output = "🥥 Something's cracked, and it's **not** the coconut! That doesn't look like a real location. Are you making things up?!"
	except requests.RequestException:
		output = f"🥥 Something's cracked, and it's **not** the coconut! ¯\\_(ツ)_/¯"

	# Send the output to the interaction
	await interaction.response.send_message(output)


# Define a command to list supported language codes
# noinspection PyUnresolvedReferences
@client.tree.command(name="languages", description="List supported language codes")
async def languages(interaction: discord.Interaction) -> None:
	"""
	A command to list supported language codes.
	"""
	# Create a list of language codes and names
	languages_list = [f"• `{language}`/`{code}`" for code, language in LANGUAGES.items()]

	# Join the list into a single string
	message = "\n".join(languages_list)

	# Split the message into chunks of 1990 characters or less
	chunks = [message[i:i + 1990] for i in range(0, len(message), 1990)]

	# Send each chunk as a separate message
	for i, chunk in enumerate(chunks):
		# If this is the first chunk, send it as the initial response
		if i == 0:
			await interaction.response.send_message(chunk)
		# Otherwise, send it as a follow-up message
		else:
			await interaction.followup.send(chunk)


# Run the client with the retrieved token
client.run(BOT_ACCESS_TOKEN)
