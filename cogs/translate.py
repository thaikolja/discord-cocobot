#  Copyright (C) 2026 by Kolja Nolte
#  kolja.nolte@gmail.com
#  https://gitlab.com/thailand-discord/bots/cocobot
#
#  This work is licensed under the MIT License. You are free to use, copy, modify,
#  merge, publish, distribute, sublicense, and/or sell copies of the Software,
#  and to permit persons to whom the Software is furnished to do so, subject to the
#  condition that the above copyright notice and this permission notice shall be
#  included in all
#  copies or substantial portions of the Software.
#
#  For more information, visit: https://opensource.org/licenses/MIT
#
#  Author:    Kolja Nolte
#  Email:     kolja.nolte@gmail.com
#  License:   MIT
#  Date:      2024-2026
#  Package:   cocobot Discord Bot

# Import the logging module for error tracking and logging purposes
import asyncio
import logging  # Import logging module for error tracking

# Import the discord module for interacting with the Discord API
import discord  # For interacting with the Discord API

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

DISCORD_MESSAGE_LIMIT = 2000


def _normalize_language(language: str | None) -> str | None:
    """Normalize a user-provided language name for comparisons and prompts."""
    if language is None:
        return None

    normalized = language.strip()
    if not normalized:
        return None

    return normalized.title()


def _detect_source_language(text: str) -> str:
    """Guess the source language using a minimal heuristic.

    If any character falls within the Thai Unicode block, treat the text as Thai.
    Latin letters are treated as English; input without either script is unknown.
    """
    if any("\u0e00" <= character <= "\u0e7f" for character in text):
        return "Thai"
    if any(("a" <= character.casefold() <= "z") for character in text):
        return "English"
    return "Unknown"


def _default_target_language(source_language: str) -> str:
    """Infer the default target language from the resolved source language."""
    return "English" if source_language.casefold() != "english" else "Thai"


def _escape_response_text(text: str) -> str:
    """Escape user- or AI-provided text before placing it in a Discord message."""
    return discord.utils.escape_markdown(discord.utils.escape_mentions(text))


def _utf16_length(text: str) -> int:
    """Return the number of UTF-16 code units Discord counts for a message."""
    return sum(2 if ord(character) > 0xFFFF else 1 for character in text)


def _truncate(text: str, limit: int) -> str:
    """Truncate text to a UTF-16 unit limit while making the omission visible."""
    if _utf16_length(text) <= limit:
        return text
    if limit <= 1:
        return "…"[:limit]

    truncated = []
    used_units = 0
    content_limit = limit - 1
    for character in text:
        character_units = 2 if ord(character) > 0xFFFF else 1
        if used_units + character_units > content_limit:
            break
        truncated.append(character)
        used_units += character_units
    return f"{''.join(truncated)}…"


def _format_translation_response(
    text: str,
    output: str,
    source_language: str,
    target_language: str,
) -> str:
    """Build a safe translation response within Discord's message limit."""
    escaped_input = _escape_response_text(text)
    escaped_output = _escape_response_text(output)
    source_label = _truncate(_escape_response_text(source_language), 64)
    target_label = _truncate(_escape_response_text(target_language), 64)
    input_label = f"📚️ **Input ({source_label}):** "
    output_label = f"\n**Output ({target_label}):** "
    content_budget = (
        DISCORD_MESSAGE_LIMIT - _utf16_length(input_label) - _utf16_length(output_label)
    )

    # Give each field half of the available space, then let the other field use
    # any capacity the shorter field leaves behind.
    input_length = _utf16_length(escaped_input)
    output_length = _utf16_length(escaped_output)
    input_budget = min(input_length, content_budget // 2)
    output_budget = min(output_length, content_budget - input_budget)
    remaining = content_budget - input_budget - output_budget
    output_budget += min(remaining, output_length - output_budget)
    remaining = content_budget - input_budget - output_budget
    input_budget += min(remaining, input_length - input_budget)

    return (
        f"{input_label}{_truncate(escaped_input, input_budget)}"
        f"{output_label}{_truncate(escaped_output, output_budget)}"
    )


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
        name="translate", description="Translate text from one language to another"
    )
    # Provide descriptions for command parameters
    @app_commands.describe(
        text="The text to translate",
        from_language="Source language name (Default: Thai/English)",
        to_language="Target language name (Default: Opposite of `from_language`)",
    )
    # Main function to handle the translation command
    async def translate_command(
        self,
        interaction: discord.Interaction,
        text: str,
        from_language: str | None = None,
        to_language: str | None = None,
    ):
        """
        Handles the /translate command to translate text from one language to another.

        Parameters:
        interaction (discord.Interaction): The interaction object representing the command invocation
        text (str): The text to translate
        from_language (str | None): Source language name; guessed from Thai text when omitted
        to_language (str | None): Target language name; inferred from the resolved source when omitted
        """

        from_language = _normalize_language(from_language)
        to_language = _normalize_language(to_language)

        displayed_source_language = from_language

        if from_language is None or to_language is None:
            detected_language = _detect_source_language(text)

            if from_language is None:
                displayed_source_language = detected_language
                # Preserve the existing non-Thai fallback for translation routing,
                # but do not present unknown input as detected English.
                from_language = (
                    detected_language if detected_language != "Unknown" else "English"
                )
            if to_language is None:
                to_language = _default_target_language(from_language)

        if displayed_source_language is None:
            displayed_source_language = from_language

        if from_language.casefold() == to_language.casefold():
            await interaction.response.send_message(
                "❌ Source and target languages must be different.",
                ephemeral=True,
            )
            return

        try:
            # Defer the response immediately to avoid timeout
            await interaction.response.defer()
        except discord.errors.NotFound:
            # Interaction has already expired, log and return
            logger.warning(
                f"Interaction expired for translate command by {interaction.user}"
            )
            return
        except Exception as e:
            # Log other defer errors but continue
            logger.error(f"Failed to defer interaction: {e}")
            return

        try:
            # Initialize the AI helper with the preferred provider
            ai = UseAI(provider="gemini")
            # Set AI response parameters
            ai.temperature = 0.3
            # Well, top_p, I guess
            ai.top_p = 0.3
            # Construct the prompt for the AI to process
            prompt = (
                f'Translate the text "{text}" from {from_language} to {to_language}. '
                "Keep the tone and meaning of the original text. Stay accurate."
            )

            # Get the response from the AI off the event loop
            output = await asyncio.to_thread(ai.prompt, prompt)

            # Check if the response is valid
            if not output:
                # Send error message if response is empty
                await interaction.followup.send(ERROR_MESSAGE)
                return

            # Include the source text and resolved languages without allowing
            # user or model output to create mentions or break the labels.
            response = _format_translation_response(
                text,
                str(output),
                displayed_source_language,
                to_language,
            )
            await interaction.followup.send(
                response,
                allowed_mentions=discord.AllowedMentions.none(),
            )
        except TimeoutError:
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
