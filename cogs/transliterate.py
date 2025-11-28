#  Copyright (C) 2025 by Kolja Nolte
#  kolja.nolte@gmail.com
#  https://gitlab.com/thailand-discord/bots/cocobot
#
#  This work is licensed under the MIT License. You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the condition that the above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  For more information, visit: https://opensource.org/licenses/MIT
#
#  Author:    Kolja Nolte
#  Email:     kolja.nolte@gmail.com
#  License:   MIT
#  Date:      2014-2025
#  Package:   cocobot Discord Bot

# Import the logging module for logging purposes
import logging

# Import discord from the discord library
import discord

# Import app_commands from the discord library
from discord import app_commands

# Import necessary components from the discord.ext.commands module
from discord.ext import commands

# Import ERROR_MESSAGE from the config module
from config.config import ERROR_MESSAGE

# Import UseAI from the utils.helpers module
from utils.helpers import UseAI

# Set up a logger for this module
logger = logging.getLogger(__name__)


# Define the Transliterate cog class
class Transliterate(commands.Cog):
    """
    A cog that attempts to transliterate Thai text into something resembling Latin script.
    Uses an AI due to the tedious nature of manually mapping Thai phonetics.
    Good luck.
    """

    def __init__(self, bot: commands.Bot):
        """
        Initializes the cog.
        Sets up the bot instance and AI provider.
        """
        self.bot = bot  # Assign the bot instance to a class variable
        self.ai_provider = 'google'  # Set the default AI provider

    # Define a command for transliterating Thai text
    @app_commands.command(
        name="transliterate",
        description='Transliterates Thai words and sentences into the English alphabet.',
    )
    @app_commands.describe(text='The Thai text to be butchered into Latin script.')
    async def transliterate_command(self, interaction: discord.Interaction, text: str):
        """
        The main command logic. Takes Thai text, throws it at an AI, and hopes for the best.

        Args:
                interaction (discord.Interaction): The context for the command invocation.
                text (str): The Thai input string, assuming it is indeed Thai.
        """
        # Notify the user that a response may take a while
        # noinspection PyUnresolvedReferences
        await interaction.response.defer()

        # Check if the input is just whitespace
        if not text or text.isspace():
            # Inform the user that the input cannot be just whitespace
            await interaction.followup.send(
                "✍️ How about adding some text in Thai, you coconut head!"
            )
            return

        try:
            # Initialize the AI helper for the requested task
            ai = UseAI(provider=self.ai_provider)

            # Construct a detailed prompt for the AI
            prompt = (
                "Transliterate the following Thai text into Latin characters using a "
                "phonetic system understandable to English speakers: "
                f"'{text}'.\n"
                "\n"
                "Instructions:\n"
                "1. Use diacritics (like ā, á, â, à, ǎ) on vowels to represent the five "
                "Thai tones (mid, high, falling, low, rising) accurately for each "
                "syllable.\n"
                "2. Separate syllables within a word using a hyphen (-).\n"
                "3. Separate distinct words with a single space.\n"
                "4. Use specific consonant mappings for initial sounds: 'ก' = 'g', "
                "'ป' = 'bp', 'ต' = 'dt'. For other consonants and vowels, use a "
                "consistent, common phonetic representation.\n"
                "5. Ensure the output contains only Latin characters, hyphens, "
                "spaces, and the necessary diacritics.\n"
                "Example: 'สวัสดี' might become 'sà-wàt-dii'.\n"
                "\n"
                "Provide only the transliterated text as the result."
            )

            # Send the constructed prompt to the AI and get a response
            answer = ai.prompt(prompt)

            # Check if the AI responded with content
            if not answer or answer.isspace():
                # Log a warning if the AI response is empty or whitespace
                logger.warning(
                    f"AI returned an empty or whitespace response for input: {text}"
                )
                # Inform the user the AI didn't provide a useful response
                await interaction.followup.send(
                    f"{ERROR_MESSAGE} @cocobot seems to be speechless. It didn't give anything useful. Poetic as always..."
                )
                return

            # Clean the AI response to remove extraneous characters
            transliteration = (
                answer.strip().replace(':', '').replace('"', '').replace("'", "")
            )

            # Further clean the transliteration by collapsing multiple spaces
            transliteration = ' '.join(transliteration.split())

            # Send the final transliterated text to the user
            await interaction.followup.send(f"✍️ **Transliteration:** {transliteration}")

        except ValueError as ve:
            # Log and handle ValueError exceptions
            logger.error(f"ValueError during transliteration for input '{text}': {ve}")
            # Inform the user about a value-related error
            await interaction.followup.send(
                f"{ERROR_MESSAGE} Looks like there was invalid data somewhere. Check your input, maybe?"
            )
        except Exception as e:
            # Log and handle unexpected exceptions
            logger.exception(
                f"An unexpected error occurred during transliteration for input '{text}': {e}"
            )
            # Inform the user that something went wrong, and blame the programmer
            await interaction.followup.send(
                f"{ERROR_MESSAGE} Blame @Kolja, the coconut head; he programmed me, after all!"
            )


# Function to add the Transliterate cog to the bot instance
async def setup(bot: commands.Bot):
    """
    Adds the Transliterate cog to the bot.
    Standard setup procedure for cogs.
    """
    await bot.add_cog(Transliterate(bot))
