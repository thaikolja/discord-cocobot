# Import the os module for interacting with the operating system
import os
# Import discord module for creating a Discord bot
import discord
# Import commands from discord.ext for creating bot commands
from discord.ext import commands
# Import app_commands for creating application commands
from discord import app_commands
# Import Translator and LANGUAGES from googletrans for translation functionality
from googletrans import Translator, LANGUAGES
# Import load_dotenv to load environment variables from a .env file
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Retrieve the bot token from environment variables
TOKEN = os.getenv('BOT_TOKEN')


# Define a custom client class that extends discord.Client
class MyClient(discord.Client):
	"""
	A custom Discord client class that extends discord.Client.
	This client handles bot initialization, command tree setup, and translation functionality.
	"""

	def __init__(self):
		"""
		Initialize the MyClient instance with specific intents and a command tree.
		"""
		# Set up default intents for the bot
		intents = discord.Intents.default()
		# Enable receiving message content
		intents.message_content = True
		# Enable receiving presence updates
		intents.presences = True
		# Enable receiving member events
		intents.members = True
		# Initialize the superclass with the specified intents
		super().__init__(intents=intents)
		# Create a command tree for application commands
		self.tree = app_commands.CommandTree(self)
		# Initialize a translator for language translation
		self.translator = Translator()

	async def setup_hook(self):
		"""
		An asynchronous setup hook to synchronize the command tree with a specific guild.
		"""
		# Create a guild object with a specific ID (replace with your Guild ID)
		guild = discord.Object(id=1148760268353061077)
		# Copy global commands to the specified guild
		self.tree.copy_global_to(guild=guild)
		# Synchronize the command tree with the guild
		await self.tree.sync(guild=guild)


# Instantiate the custom client
client = MyClient()


# Define an event handler for when the bot is ready
@client.event
async def on_ready():
	"""
	Event handler that is called when the bot is ready.
	Sets the bot's status and activity.
	"""
	# Print bot login information to the console
	print(f'Bot is ready. Logged in as {client.user} (ID: {client.user.id})')
	print('------')
	# Set the bot's status to online and activity to a game
	await client.change_presence(
		status=discord.Status.online,
		activity=discord.Game(name="Translating languages")
	)


# Define a command to translate text into a target language
@client.tree.command(name="translate", description="Translate text into a target language")
@app_commands.describe(text="The text to translate", target_language="Target language code (e.g., 'es' for Spanish)")
async def translate(interaction: discord.Interaction, text: str, target_language: str):
	"""
	Command to translate text into a specified target language.

	Parameters:
	interaction (discord.Interaction): The interaction object.
	text (str): The text to translate.
	target_language (str): The target language code (e.g., 'es' for Spanish).
	"""
	# Get the translator from the client
	translator = client.translator
	# Convert the target language code to lowercase
	target_language = target_language.lower()

	# Check if the target language code is valid
	if target_language not in LANGUAGES and target_language not in LANGUAGES.values():
		# Send an error message if the language code is invalid
		await interaction.response.send_message(
			'Invalid target language code. Use `/languages` to see supported codes.')
		return

	try:
		# Attempt to translate the text to the target language
		translation = translator.translate(text, dest=target_language)
		# Send the translation result as a message
		await interaction.response.send_message(
			f'**Translation ({translation.src} → {translation.dest}):** {translation.text}')
	except Exception as e:
		# Print the error to the console
		print(f'Error: {str(e)}')
		# Send an error message if translation fails
		await interaction.response.send_message('An error occurred during translation.')


# Define a command to list all supported language codes
@client.tree.command(name="languages", description="List supported language codes")
async def languages(interaction: discord.Interaction):
	"""
	Command to list all supported language codes.

	Parameters:
	interaction (discord.Interaction): The interaction object.
	"""
	# Create a list of supported language codes and their names
	languages_list = [f"• `{code}`: {language}" for code, language in LANGUAGES.items()]
	# Join the list into a single message
	message = "\n".join(languages_list)
	# Split the message into chunks if it's too long
	chunks = [message[i:i + 1990] for i in range(0, len(message), 1990)]
	# Send each chunk as a separate message
	for i, chunk in enumerate(chunks):
		if i == 0:
			await interaction.response.send_message(chunk)
		else:
			await interaction.followup.send(chunk)


# Run the client using the retrieved token
client.run(TOKEN)
