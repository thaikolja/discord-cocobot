# Import the necessary libraries for parsing command-line arguments
import argparse

# Import the os library for interacting with the operating system
import os

# Import the discord library for creating a Discord bot
import discord

# Import the socket library for checking the current host
import socket

# Import the requests library for making HTTP requests
import requests

# Import the app_commands library for creating Discord bot commands
from discord import app_commands

# Import the Translator library for translating text
from googletrans import Translator, LANGUAGES

# Import the load_dotenv function for loading environment variables from a .env file
from dotenv import load_dotenv

# Import the sub function for regular expression substitution
from re import sub

from datetime import datetime

# Load environment variables from a .env file
load_dotenv()

# Define a constant for the host name
# HOST will be used to check if the current host is the server
HOST = 'host.yanawa.io'

# Define a constant for the Discord guild ID
# GUILD_ID will be used to identify the Discord guild
GUILD_ID = os.getenv('GUILD_ID')

# Define a constant for the LocalTime API key
# LOCALTIME_API_KEY will be used to make requests to the LocalTime API
LOCALTIME_API_KEY = os.getenv('LOCALTIME_API_KEY')

# Define a constant for the Discord bot token
# BOT_TOKEN will be used to authenticate the Discord bot
BOT_TOKEN = os.getenv('BOT_TOKEN')

WEATHERAPI_API_KEY = os.getenv('WEATHERAPI_API_KEY')

# Load environment variables from a .env file
load_dotenv()


# Define a custom Discord client class
class Cocobot(discord.Client):
	# Initialize the client with default intents
	def __init__(self):
		# Create a new instance of the discord.Intents class
		intents = discord.Intents.default()
		# Enable message content intent
		intents.message_content = True
		# Enable presence intent
		intents.presences = True
		# Enable member intent
		intents.members = True
		# Call the superclass constructor
		super().__init__(intents=intents)
		# Create a new instance of the app_commands.CommandTree class
		self.tree = app_commands.CommandTree(self)
		# Create a new instance of the Translator class
		self.translator = Translator()

	# Define a setup hook for the client
	async def setup_hook(self):
		# Create a new instance of the discord.Object class for the guild
		guild = discord.Object(id=GUILD_ID)
		# Copy global commands to the guild
		self.tree.copy_global_to(guild=guild)
		# Sync the command tree for the guild
		await self.tree.sync(guild=guild)


# Create a new instance of the Cocobot class
client = Cocobot()


# Define an event handler that is called when the bot is ready
@client.event
async def on_ready():
	# Print a message to the console to indicate that the bot is ready
	print(f'Bot is ready. Logged in as {client.user} (ID: {client.user.id})')
	# Print a separator line
	print('------')
	# Change the bot's presence to online
	await client.change_presence(
		status=discord.Status.online,
		activity=discord.Game(name="whatever you want me to do")
	)


@client.tree.command(name="weather", description="Show the current weather in a city or country")
@app_commands.describe(location="The city or country to show the current weather (Default: Bangkok)")
async def weather(interaction: discord.Interaction, location: str = 'Bangkok'):
	location = sub(r'[^-\w\s]', '', location).replace(' ', '%20')
	api_url = f'https://api.weatherapi.com/v1/current.json?key={WEATHERAPI_API_KEY}&q={location}'
	response = {}

	try:
		response = requests.get(api_url).json()
		current_weather_time = response['location']['localtime']
		city = response['location']['name']
		temperature_c = response['current']['temp_c']
		condition = str(response['current']['condition']['text'])
		feels_like = response['current']['feelslike_c']
		output = (
			f"🌤️ It's currently ({current_weather_time}) **{temperature_c}°C** in {city} which feels more like *"
			f"*{feels_like}°C**. "
			f"Weather "
			f"condition: **{condition}**. "
		)
	except requests.RequestException:
		output = f"\"{location}\" doesn\'t look like a real location. Did a coconut fall on your head?!"

	if 'error' in response:
		print('Error:', response['error']['message'])

	await interaction.response.send_message(output)


# Define a command to translate text into a target language
@client.tree.command(name="translate", description="Translate text into a target language")
@app_commands.describe(
	# Describe the text argument
	text="The text in English to translate",
	# Describe the language argument
	language="Target language (e.g., 'es' or 'spanish' for Spanish)"
)
async def translate(interaction: discord.Interaction, text: str, language: str):
	try:
		# Create a new instance of the Translator class
		translator = client.translator
		# Convert the language to lowercase
		language = language.lower()

		# Check if the language is valid
		if language not in LANGUAGES and language not in LANGUAGES.values():
			# Send an error message to the interaction
			await interaction.response.send_message(
				"What kind of language is that supposed to be?! Did a coconut fall on your head or what? Run `/languages` to see what languages I can translate.")
			# Return from the function
			return

		# Translate the text
		translation = translator.translate(text, dest=language)
		# Send the translation to the interaction
		await interaction.response.send_message(
			f'**Translation:** {translation.text}')
	except Exception as e:
		# Print the error message to the console
		print(f'Error: {str(e)}')
		# Send an error message to the interaction
		await interaction.response.send_message(
			"Seems like my coconut brain wasn't able to translate this. Try again, maybe?")


# Define a command to show the current time in a city or country
@client.tree.command(name="time", description="Show the current time a city or country")
@app_commands.describe(location="The city or country to show the current time")
async def time(interaction: discord.Interaction, location: str):
	current_time = None
	city = None
	country = None

	try:
		# Remove non-alphanumeric characters from the location
		location = sub(r'[^-\w\s]', '', location).replace(' ', '%20')
		# Construct the API URL for the LocalTime API
		api_url = f'https://api.ipgeolocation.io/timezone?apiKey={LOCALTIME_API_KEY}&location={location}'
		# Make a GET request to the API
		response = requests.get(api_url)
		# Raise an exception if the response was not successful
		response.raise_for_status()

		# Check if the response is in JSON format
		if response.headers['Content-Type'].startswith('application/json'):
			# Parse the JSON response
			data = response.json()

			# Check if the response contains the expected data
			if 'geo' in data:
				# Extract the city and country from the response
				city = data['geo']['city']
				country = data['geo']['country']
				# Extract the current time from the response
				current_time = data.get('date_time_txt')
	except requests.RequestException:
		# If the request failed, set the current time to None
		current_time = None

	# Check if the current time is a string
	if type(current_time) == str:
		# If the city is not empty, include it in the output
		if len(city) >= 3:
			output = f'The current time in **{city}**, **{country}** is **{current_time}**'
		# Otherwise, only include the country in the output
		else:
			output = f'The current time in **{country}** is **{current_time}**'
	else:
		# If the current time is not a string, send an error message
		output = "That doesn't look like a real location. Are you making things up?!"

	# Send the output to the interaction
	await interaction.response.send_message(output)


# Define a command to list supported language codes
@client.tree.command(name="languages", description="List supported language codes")
async def languages(interaction: discord.Interaction):
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
client.run(BOT_TOKEN)
