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

# Import the logging module for error tracking and logging purposes
import logging  # Import logging module for error tracking

# Import the discord module for interacting with the Discord API
import discord  # For interacting with the Discord API

# Import the openai module for interacting with OpenAI's API
import openai  # For interacting with OpenAI's API

# Import the app_commands module from discord for defining slash commands
from discord import app_commands  # For defining slash commands

# Import the commands module from discord.ext for creating bot commands
from discord.ext import commands  # For creating bot commands

# Import the ERROR_MESSAGE from the config module
from config.config import (  # Import custom error message from configuration
    ERROR_MESSAGE,
)

# Import the UseAI helper utility from the utils.helpers module
from utils.helpers import UseAI  # Import AI helper utility

# Configure the logger for this module to track activities and errors
logger = logging.getLogger(__name__)


# noinspection PyUnresolvedReferences
# Define a new Cog class for translation functionality
class TranslateCog(commands.Cog):
    """
    A Discord Cog for translating text from one language to another.
    """

    # Constructor to initialize the TranslateCog class with the given bot instance
    def __init__(self, bot: commands.Bot):
        """
        Initializes the TranslateCog class with the given bot instance.

        Parameters:
        bot (commands.Bot): The bot instance to which this cog is added
        """
        # Store the bot instance for later use
        self.bot = bot

    # Define a new slash command for translation
    @app_commands.command(
        name="translate", description='Translate text from one language to another'
    )
    # Provide descriptions for command parameters
    @app_commands.describe(
        text='The text to translate',
        from_language='The language code of the source language (Default: Thai)',
        to_language='The language code of the target language (Default: English)',
    )
    # Main function to handle the translation command
    async def translate_command(
        self,
        interaction: discord.Interaction,
        text: str,
        from_language: str = 'Thai',
        to_language: str = 'English',
    ):
        """
        Handles the /translate command to translate text from one language to another.

        Parameters:
        interaction (discord.Interaction): The interaction object representing the command invocation
        text (str): The text to translate
        from_language (str): The language code of the source language (Default: Thai)
        to_language (str): The language code of the target language (Default: English)
        """

        try:
            # Defer the response immediately to avoid timeout
            await interaction.response.defer()
        except discord.errors.NotFound:
            # Interaction has already expired, log and return
            logger.warning(f"Interaction expired for translate command by {interaction.user}")
            return
        except Exception as e:
            # Log other defer errors but continue
            logger.error(f"Failed to defer interaction: {e}")
            return

        try:
            # Initialize the AI helper with the preferred provider
            ai = UseAI(provider='google')
            # Set AI response parameters
            ai.temperature = 0.3
            ai.top_p = 0.3
            # Construct the prompt for the AI to process
            prompt = (
                f'Translate the text "{text}" from {from_language} to {to_language}. '
                'Keep the tone and meaning of the original text. Stay accurate.'
            )

            # Get the response from the AI
            output = ai.prompt(prompt)

            # Check if the response is valid
            if not output:
                # Send error message if response is empty
                await interaction.followup.send(ERROR_MESSAGE)
                return

            # Send the translated text back to the user
            await interaction.followup.send(f"📚️ **Translation:** {output}")
        except openai.APITimeoutError:
            # Handle API timeout errors
            await interaction.followup.send("⏰ Request timed out after 10 seconds")
        except Exception as e:
            # Handle other exceptions
            logger.error(f"Translation error: {e}", exc_info=True)
            await interaction.followup.send(f"❌ Error: {str(e)}")


# Define the asynchronous setup function to add the TranslateCog to the bot
async def setup(bot: commands.Bot):
    """
    A setup function to add the TranslateCog to the bot.

    Parameters:
    bot (commands.Bot): The bot instance to which this cog is added
    """
    # Add an instance of TranslateCog to the bot
    await bot.add_cog(TranslateCog(bot))
