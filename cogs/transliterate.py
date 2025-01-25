# Import the discord library for creating Discord bots
import discord

# Import commands from discord.ext for creating bot commands
from discord.ext import commands

# Import app_commands from discord for creating slash commands
from discord import app_commands

# Import UseAI class from utils.helpers for AI-based transliterations
from utils.helpers import UseAI


# Define the Transliterate class as a subclass of commands.Cog
# noinspection PyUnresolvedReferences
class Transliterate(commands.Cog):
	"""
	A Discord Cog for transliterating Thai text to Latin script.
	"""

	def __init__(self, bot: commands.Bot):
		"""
		Initializes the Transliterate class with the given bot instance.

		Parameters:
		bot (commands.Bot): The bot instance to which this cog is added.
		"""
		self.bot = bot

	@app_commands.command(name="transliterate", description='Transliterate Thai text to Latin script')
	@app_commands.describe(text='The text to transliterate')
	async def transliterate_command(self, interaction: discord.Interaction, text: str):
		"""
		A slash command to transliterate Thai text to Latin script.

		Parameters:
		interaction (discord.Interaction): The interaction object representing the command invocation.
		text (str): The text to transliterate.
		"""
		# Create a prompt for the AI to transliterate the text
		prompt = (
			f"Transliterate the Thai text '{text}' into Latin characters only. Use diacritics to display the tone markers for every consonant and vowel. Make it readable for English "
			f"readers."
		)

		# Create an instance of UseAI with 'google' as the provider
		ai = UseAI(provider='gpt')

		# Generate the transliteration using the AI instance
		answer = ai.prompt(prompt)

		# Send the transliterated text as a response to the interaction
		await interaction.response.send_message(answer)


# Define the asynchronous setup function to add the Transliterate cog to the bot
async def setup(bot: commands.Bot):
	"""
	A setup function to add the Transliterate cog to the bot.

	Parameters:
	bot (commands.Bot): The bot instance to which this cog is added.
	"""
	await bot.add_cog(Transliterate(bot))
