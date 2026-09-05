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


# Gemini is blocking; asyncio lets us hide that from Discord's event loop
import asyncio

# When transliteration goes sideways, logs beat vibes
import logging

# Yes, this is still a Discord bot, not a linguistics thesis
import discord

# Slash commands live here, because prefix commands are so 2018
from discord import app_commands

# Cog plumbing: the official way to bolt features onto the coconut
from discord.ext import commands

# Shared "oops" copy so we don't invent a new apology each time
from config.config import ERROR_MESSAGE

# Thin wrapper around whoever is currently pretending to know Thai phonetics
from utils.helpers import UseAI

# Prompt templates, because raw f-strings of instructions age like milk
from utils.prompts import render_language_prompt

# Module logger; name matches the file so grep actually works
logger = logging.getLogger(__name__)


# Thai-to-Latin via AI, because a lookup table would be a second career
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
        # Hold the bot so setup() doesn't have to smuggle it later
        self.bot = bot

        # Gemini is the default; swap it only if you enjoy debugging encodings
        self.ai_provider = 'gemini'

        # Temperature 0: we want romanization, not creative spelling
        self.ai = UseAI(
            provider=self.ai_provider,
            temperature=0.0,
            disable_thinking=True,
        )

    # Discord needs a name and a sales pitch for the slash command
    @app_commands.command(
        name="transliterate",
        description='Transliterates Thai words and sentences into the English alphabet'
    )
    # Parameter hint so users don't paste English and wonder why nothing happens
    @app_commands.describe(text='The Thai text to be butchered into Latin script.')
    async def transliterate_command(self, interaction: discord.Interaction, text: str):
        """
        The main command logic. Takes Thai text, throws it at an AI, and hopes for the best.

        Args:
                interaction (discord.Interaction): The context for the command invocation.
                text (str): The Thai input string, assuming it is indeed Thai.
        """
        # Discord times out fast; defer before Gemini even wakes up
        try:
            # Inspector: discord.py types vs runtime, classic
            # noinspection PyUnresolvedReferences
            await interaction.response.defer()

        # Token expired while we were still saying hello
        except discord.errors.NotFound:
            # Log the ghost ping so we know it wasn't a model failure
            logger.warning(
                "Transliterate defer failed: interaction expired before acknowledgement "
                f"(user_id={interaction.user.id})."
            )

            # Nothing left to follow up on
            return

        # Any other Discord hiccup: log and bail, don't pretend we deferred
        except Exception as e:
            # Keep the user id; future-you will thank present-you
            logger.error(
                f"Transliterate defer failed for user_id={interaction.user.id}: {e}",
                extra={'cause': 'discord_interaction_defer'},
            )

            # Stop here; followup would just 404
            return

        # Whitespace-only "Thai" is not a tribute, it's a shrug
        if not text or text.isspace():
            # Kabakon flavor, still a hard no
            await interaction.followup.send(
                "✍️ Empty tribute? Kabakon is not impressed. Offer actual Thai, not a blank copra husk."
            )

            # No model call for an empty string, we're not that bored
            return

        # Prompt, call, clean, send — the happy path, theoretically
        try:
            # Bake the user text into the canned transliterate prompt
            prompt = render_language_prompt('transliterate', text=text)

            # Missing template is a deploy bug, not a user typo
            if not prompt:
                # Generic error; don't leak that the prompt file vanished
                await interaction.followup.send(ERROR_MESSAGE)

                # No prompt, no party
                return

            # Off-thread so the rest of the bot can still serve weather memes
            answer = await asyncio.to_thread(self.ai.prompt, prompt)

            # Empty model output is a warning, not a "success with vibes"
            if not answer or answer.isspace():
                # Length helps when reproducing filter nonsense
                logger.warning(
                    "Transliterate Gemini returned empty text; check model output filters "
                    f"and prompt render for input_length={len(text)}."
                )

                # User-facing: the sun-king chose silence. Rarely a compliment.
                await interaction.followup.send(
                    f"{ERROR_MESSAGE} The sun-king of Kabakon considered your syllables and chose silence. Rarely a compliment."
                )

                # Don't send quotes around nothing
                return

            # Strip quotes and colons the model loves to sprinkle on
            transliteration = (
                answer.strip().replace(':', '').replace('"', '').replace("'", "")
            )

            # Collapse the model's "poetic spacing" into one space
            transliteration = ' '.join(transliteration.split())

            # Finally: Latin-ish letters, Discord-ready
            await interaction.followup.send(f"✍️ **Transliteration:** {transliteration}")

        # ValueError usually means the helper hated the input
        except ValueError as ve:
            # Length + exception; enough to debug without dumping Thai into logs forever
            logger.warning(
                f"Transliterate rejected input as ValueError (length={len(text)}): {ve}"
            )

            # Tell them to send actual Thai, not keyboard soup
            await interaction.followup.send(
                f"{ERROR_MESSAGE} That offering would not even ferment into copra. Send proper Thai, not whatever that was."
            )

        # Provider down, network, surprise AttributeError — all land here
        except Exception as e:
            # Stack traces for Kolja; jokes for the channel
            logger.error(
                f"Transliterate failed during Gemini/provider call (length={len(text)}): {e}",
                exc_info=True,
            )

            # Copra press jammed: technically accurate if you squint
            await interaction.followup.send(
                f"{ERROR_MESSAGE} The copra press jammed. Sit in the sun with August until Kolja oils the gears."
            )


# discord.py entry point: load this cog or the command never exists
async def setup(bot: commands.Bot):
    """
    Adds the Transliterate cog to the bot.
    Standard setup procedure for cogs.
    """
    # Instantiate and attach; no extra options, keep it boring
    await bot.add_cog(Transliterate(bot))
