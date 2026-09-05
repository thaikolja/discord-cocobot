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

# Blocking Gemini again; thread it or the gateway sulks
import asyncio

# Translation failures deserve logs, not just coconut poetry
import logging

# Interaction, NotFound, send_message
import discord

# Slash commands
from discord import app_commands

# Cog base
from discord.ext import commands

# Shared error banner
from config.config import (  # Import custom error message from configuration
    ERROR_MESSAGE
)

# Gemini wrapper
from utils.helpers import UseAI

# Language prompt templates
from utils.prompts import render_language_prompt

# Module-level logger
logger = logging.getLogger(__name__)


def _normalize_language(language: str | None) -> str | None:
    """Normalize a user-provided language name for comparisons and prompts."""
    # None stays None; we infer later
    if language is None:
        # Caller will detect Thai vs English
        return None

    # Users type " thai " with feelings
    normalized = language.strip()

    # Empty after strip is the same as omitted
    if not normalized:
        # Treat as missing, not as language ""
        return None

    # Title case so "english" and "English" compare the same-ish
    return normalized.title()


def _detect_source_language(text: str) -> str:
    """Guess the source language using a minimal heuristic.

    If any character falls within the Thai Unicode block, treat the text as Thai.
    Otherwise default to English.
    """
    # One Thai letter is enough; this is a bot, not a language ID paper
    return 'Thai' if any('\u0e00' <= character <= '\u0e7f' for character in text) else 'English'


def _default_target_language(source_language: str) -> str:
    """Infer the default target language from the resolved source language."""
    # Thai in → English out, everything else → Thai; that's the house rule
    return 'English' if source_language.casefold() != 'english' else 'Thai'


# discord.py type checker vs runtime; ignore the red squiggles
# noinspection PyUnresolvedReferences
# Thai↔English by default, any named language if the user bothers
class TranslateCog(commands.Cog):
    """
    A Discord Cog for translating text from one language to another.
    """

    def __init__(self, bot: commands.Bot):
        """
        Initializes the TranslateCog class with the given bot instance.

        Parameters:
        bot (commands.Bot): The bot instance to which this cog is added
        """
        # Bot reference, same as every other cog
        self.bot = bot

        # Gemini for translation; not the summarize provider
        self.ai = UseAI(provider='gemini')

    # /translate in the Discord UI
    @app_commands.command(
        name="translate", description='Translate text from one language to another'
    )
    # Optional from/to; we guess if they skip both
    @app_commands.describe(
        text='The text to translate',
        from_language='Source language name (Default: Thai/English)',
        to_language='Target language name (Default: Opposite of `from_language`)'
    )
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

        # Normalize source name (or keep None)
        from_language = _normalize_language(from_language)

        # Same for target
        to_language = _normalize_language(to_language)

        # Fill whatever they left blank
        if from_language is None or to_language is None:
            # Heuristic: Thai block vs "probably English"
            detected_language = _detect_source_language(text)

            # Source missing → use detection
            if from_language is None:
                # Detected string is already Title Case
                from_language = detected_language

            # Target missing → opposite of source
            if to_language is None:
                # English source → Thai, else English
                to_language = _default_target_language(from_language)

        # Same language both ways: August banned that industry
        if from_language.casefold() == to_language.casefold():
            # Ephemeral so the channel doesn't mock them publicly
            await interaction.response.send_message(
                '❌ Translating a language into itself is the kind of industry August banned on Kabakon. Pick a different shore.',
                ephemeral=True,
            )

            # No defer, no model
            return

        # Defer before the slow prompt
        try:
            # Acknowledge so Discord doesn't time us out
            await interaction.response.defer()

        # Interaction already expired
        except discord.errors.NotFound:
            # Log user id; we can't reply anymore
            logger.warning(
                "Translate defer failed: interaction expired "
                f"(user_id={interaction.user.id})."
            )

            # Stop
            return

        # Other defer failures
        except Exception as e:
            # Error log, then leave
            logger.error(
                f"Translate defer failed for user_id={interaction.user.id}: {e}"
            )

            # No followup without a defer
            return

        # Render, call, send
        try:
            # Inject text and language names into the template
            prompt = render_language_prompt(
                'translate',
                text=text,
                from_language=from_language,
                to_language=to_language,
            )

            # Missing template
            if not prompt:
                # Generic error
                await interaction.followup.send(ERROR_MESSAGE)

                # Don't call Gemini with None
                return

            # Off-thread model call
            output = await asyncio.to_thread(self.ai.prompt, prompt)

            # Empty translation is a failure
            if not output:
                # Same banner as other empty-model paths
                await interaction.followup.send(ERROR_MESSAGE)

                # Don't send a blank book emoji
                return

            # Success: prefix and ship
            await interaction.followup.send(f"📚️ **Translation:** {output}")

        # Explicit timeout from the helper
        except TimeoutError:
            # Copra boats joke, keep the original string
            await interaction.followup.send(
                f"{ERROR_MESSAGE} The steamer to the other language timed out. Even copra boats are faster today."
            )

        # Provider or unexpected errors
        except Exception as e:
            # Length helps; don't dump the whole source text
            logger.error(
                f"Translate provider call failed (text_length={len(text)}): {e}",
                exc_info=True,
            )

            # Dictionary slammed shut
            await interaction.followup.send(
                f"{ERROR_MESSAGE} The dictionary of Kabakon slammed shut. Try again after the next coconut falls."
            )


# Extension setup
async def setup(bot: commands.Bot):
    """
    A setup function to add the TranslateCog to the bot.

    Parameters:
    bot (commands.Bot): The bot instance to which this cog is added
    """
    # Register TranslateCog
    await bot.add_cog(TranslateCog(bot))
