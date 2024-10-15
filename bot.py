# Import the os module for interacting with the operating system
import os  # This module provides a way to use operating system dependent functionality

# Import discord module for creating a Discord bot
import discord  # This module is used to create a Discord bot

# Import app_commands for creating application commands
from discord import app_commands  # This module is used to create application commands for the Discord bot

# Import Translator and LANGUAGES from googletrans for translation functionality
from googletrans import Translator, LANGUAGES  # This module is used for language translation

# Import load_dotenv to load environment variables from a .env file
from dotenv import load_dotenv  # This module is used to load environment variables from a .env file

# Import the requests library for making HTTP requests
import requests  # This library is used to make HTTP requests

# Import the sub function from the re module for regular expression substitution
from re import sub  # This function is used for regular expression substitution

# Load environment variables from a .env file
load_dotenv()  # Load environment variables from a .env file


# Define a custom client class that extends discord.Client
class Cocobot(discord.Client):
	"""
	A custom Discord client class that extends discord.Client.
	This client handles bot initialization, command tree setup, and translation functionality.
	"""

	def __init__(self):
		"""
		Initialize the MyClient instance with specific intents and a command tree.
		"""
		# Set up default intents for the bot
		intents = discord.Intents.default()  # Create a new Intents object with default values
		# Enable receiving message content
		intents.message_content = True  # Allow the bot to receive message content
		# Enable receiving presence updates
		intents.presences = True  # Allow the bot to receive presence updates
		# Enable receiving member events
		intents.members = True  # Allow the bot to receive member events
		# Initialize the superclass with the specified intents
		super().__init__(intents=intents)  # Initialize the superclass with the specified intents
		# Create a command tree for application commands
		self.tree = app_commands.CommandTree(self)  # Create a new CommandTree object
		# Initialize a translator for language translation
		self.translator = Translator()  # Create a new Translator object

	async def setup_hook(self):
		"""
		An asynchronous setup hook to synchronize the command tree with a specific guild.
		"""
		# Create a guild object with a specific ID (replace with your Guild ID)
		guild = discord.Object(id=os.getenv('GUILD_ID'))  # Create a new Guild object with the specified ID
		# Copy global commands to the specified guild
		self.tree.copy_global_to(guild=guild)  # Copy global commands to the specified guild
		# Synchronize the command tree with the guild
		await self.tree.sync(guild=guild)  # Synchronize the command tree with the guild


# Instantiate the custom client
client = Cocobot()  # Create a new instance of the Cocobot class


# Define an event handler for when the bot is ready
@client.event
async def on_ready():
	"""
	Event handler that is called when the bot is ready.
	Sets the bot's status and activity.
	"""
	# Print bot login information to the console
	print(f'Bot is ready. Logged in as {client.user} (ID: {client.user.id})')  # Print bot login information
	print('------')  # Print a separator
	# Set the bot's status to online and activity to a game
	await client.change_presence(  # Set the bot's presence
		status=discord.Status.online,  # Set the bot's status to online
		activity=discord.Game(name="whatever you want me to do")  # Set the bot's activity to a game
	)


# Define a command to translate text into a target language
@client.tree.command(name="translate", description="Translate text into a target language")
@app_commands.describe(
	text="The text in English to translate",
	language="Target language (e.g., 'es' or 'spanish' for Spanish)"
)
async def translate(interaction: discord.Interaction, text: str, language: str):
	"""
	Command to translate text into a specified target language.

	Parameters:
	interaction (discord.Interaction): The interaction object.
	text (str): The text to translate.
	language (str): The target language code (e.g., 'es' for Spanish).
	"""
	# Get the translator from the client
	translator = client.translator  # Get the translator object from the client
	# Convert the target language code to lowercase
	language = language.lower()  # Convert the language code to lowercase

	# Check if the target language code is valid
	if language not in LANGUAGES and language not in LANGUAGES.values():
		# Send an error message if the language code is invalid
		await interaction.response.send_message(
			"What kind of language is that supposed to be?! Did a coconut fall on your head or what? Run `/languages` to see what languages I can translate.")
		return  # Return from the function

	try:
		# Attempt to translate the text to the target language
		translation = translator.translate(text, dest=language)  # Translate the text
		# Send the translation result as a message
		await interaction.response.send_message(
			f'**Translation{translation.dest}:** {translation.text}')  # Send the translation result
	except Exception as e:
		# Print the error to the console
		print(f'Error: {str(e)}')  # Print the error
		# Send an error message if translation fails
		await interaction.response.send_message(
			"Seems like my coconut brain wasn't able to translate this. Try again, maybe?")  # Send an error message


# Define a command to show the current time in a city or country
@client.tree.command(name="time", description="Show the current time a city or country")
@app_commands.describe(location="The city or country to show the current time")
async def time(interaction: discord.Interaction, location: str):
	"""
	Command to show the current time in a specified city or country.

	Parameters:
	interaction (discord.Interaction): The interaction object.
	location (str): The city or country to show the current time.
	"""
	# Clean the location string by removing special characters and replacing spaces with URL-encoded spaces
	location_cleaned = sub(r'[^-\w\s]', '', location).replace(' ', '%20')  # Clean the location string
	# Get the LOCALTIME_API_KEY environment variable
	localtime_api_key = os.getenv('LOCALTIME_API_KEY')  # Get the API key
	# Initialize variables to store the city, country, and current time
	city = None  # Initialize the city variable
	country = None  # Initialize the country variable
	current_time = None  # Initialize the current time variable

	try:
		# Construct the API URL for the time zone API
		api_url = f'https://api.ipgeolocation.io/timezone?apiKey={localtime_api_key}&location={location_cleaned}'  # Construct the API URL
		# Send a GET request to the API
		response = requests.get(api_url)  # Send a GET request
		# Raise an exception if the response was an error
		response.raise_for_status()  # Raise an exception if the response was an error

		# Check if the response was in JSON format
		if response.headers['Content-Type'].startswith('application/json'):
			# Parse the JSON response
			data = response.json()  # Parse the JSON response

			# Check if the response contains the required data
			if 'is_dst' in data and data['is_dst']:
				# Extract the city, country, and current time from the response
				city = data['geo']['city']  # Extract the city
				country = data['geo']['country']  # Extract the country
				current_time = data.get('date_time_txt')  # Extract the current time
	except requests.RequestException:
		# Set the current time to None if an exception occurred
		current_time = None  # Set the current time to None

	# Check if the current time was successfully retrieved
	if type(current_time) == str:
		# Construct the output message
		output = f'The current time in **{city}**, **{country}** is **{current_time}**'  # Construct the output message
	else:
		# Construct an error message if the current time was not retrieved
		output = "That doesn't look like a real location. Are you making things up?!"  # Construct an error message

	# Send the output message
	await interaction.response.send_message(output)  # Send the output message


# Define a command to list all supported language codes
@client.tree.command(name="languages", description="List supported language codes")
async def languages(interaction: discord.Interaction):
	"""
	Command to list all supported language codes.

	Parameters:
	interaction (discord.Interaction): The interaction object.
	"""
	# Create a list of supported language codes and their names
	languages_list = [f"• `{language}`/`{code}`" for code, language in
					  LANGUAGES.items()]  # Create a list of language codes
	# Join the list into a single message
	message = "\n".join(languages_list)  # Join the list into a single message
	# Split the message into chunks if it's too long
	chunks = [message[i:i + 1990] for i in range(0, len(message), 1990)]  # Split the message into chunks

	# Send each chunk as a separate message
	for i, chunk in enumerate(chunks):
		if i == 0:
			# Send the first chunk as a response to the interaction
			await interaction.response.send_message(chunk)  # Send the first chunk
		else:
			# Send subsequent chunks as follow-up messages
			await interaction.followup.send(chunk)  # Send subsequent chunks


# Run the client using the retrieved token
client.run(os.getenv('BOT_TOKEN'))  # Run the client with the retrieved token
