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
#  Date:      2014-2026
#  Package:   cocobot Discord Bot

"""
This module provides the SummarizeCog, which uses an AI model to summarize
recent chat messages in a Discord channel.
"""

# Standard library imports for async and logging stuff
import asyncio
import logging

# Discord.py  bits we use for commands and interactions
import discord
from discord import app_commands
from discord.ext import commands

# Local config + AI helper for summarization
from config.config import ERROR_MESSAGE
from utils.helpers import UseAI

# Grab the shared discord logger so we stay consistent
logger = logging.getLogger('discord')


class SummarizeCog(commands.Cog):
    """
    A Discord Cog that provides message summarization using AI.
    It's basically a shorthand for "what did I miss while I was getting a coffee?".
    """

    def __init__(self, bot: commands.Bot):
        """
        Initialize the cog with the bot instance and the AI helper.
        """
        # Keep a handle to the bot so we can interact with Discord
        self.bot = bot
        # Set up the AI helper using the configured model for summarization
        import os
        summarize_model = os.getenv("MODEL_SUMMARIZE", "deepseek")
        self.ai = UseAI(summarize_model)
        logger.info(f"Summarize cog using model: {summarize_model}")

    # Register the slash command with Discord
    @app_commands.command(
        name="summarize",
        description="Summarize recent messages in the current channel."
    )
    # Add a helpful description for the limit option
    @app_commands.describe(
        limit="Number of recent messages to summarize (Default: 15, Max: 25)"
    )
    async def summarize_command(self, interaction: discord.Interaction, limit: app_commands.Range[int, 1, 25] = 15):
        """
        Summarize recent messages in the current channel based on the specified limit of messages. The summary aims to
        capture key topics, agreements, or comedic points while maintaining a slightly humorous tone.

        Parameters:
            interaction (discord.Interaction): The interaction object representing the user's command input.
            limit (app_commands.Range[int, 1, 25]): The number of recent messages to summarize. Defaults to 15, with a maximum of 25.

        Raises:
            discord.errors.Forbidden: Raised when the bot lacks permissions to read the message history of the channel.
            Exception: Raised when an unexpected error occurs during message fetching or summarization.

        """
        # Acknowledge the interaction immediately since LLM processing takes time
        try:
            if not interaction.response.is_done():
                await interaction.response.defer()
        except discord.NotFound:
            # Interaction expired - try to notify the channel
            try:
                await interaction.channel.send(
                    f"🥥 {interaction.user.mention} The command took too long to process. Please try again!"
                )
            except Exception:
                pass
            return
        except Exception:
            return

        try:
            # Pull recent messages from the channel
            messages = [msg async for msg in interaction.channel.history(limit=limit)]

            # If the channel is empty, short-circuit with a friendly reply
            if not messages:
                await interaction.followup.send("Nothing to summarize here. Is the channel as deserted as August's Kabakon?")

                return

            # channel.history returns messages newest to oldest, so let's flip it
            messages.reverse()

            # Build a simple text transcript for the AI
            transcript_lines = []
            for msg in messages:
                # We'll grab the author's name and what they said, skipping empty stuff
                author_name = msg.author.display_name
                content = msg.clean_content
                if content:
                    transcript_lines.append(f"{author_name}: {content}")

            # If we end up with nothing to summarize after cleaning, let the user know
            if not transcript_lines:
                await interaction.followup.send("Could not find any text content to summarize.")

                return

            # Combine everything into one big string for the AI
            transcript = "\n".join(transcript_lines)

            # This is where we tell the AI how to behave - keep it short and a bit cheeky
            prompt = (
                "Provide a concise summary of the following chat transcript with **no more than 600 characters**. "
                "Capture the **main topics**, agreements, or funny remarks without listing every detail. ",
                "Write as paragraph. Keep the tone slightly sarcastic and humorous, but not too much. Avoid being too formal.",
                "Return only the summary and nothing else. The summary must be **useful**. The content to summarize: \n\n",
                f"{transcript}"
            )

            # We're running this in a separate thread so we don't freeze the whole bot
            summary = await asyncio.to_thread(self.ai.prompt, str(prompt), False)

            # If the AI flakes out, show an error
            if not summary:
                await interaction.followup.send(f"{ERROR_MESSAGE} The AI failed to generate a summary.")

                return

            # Let's not create a wall of text, please
            if len(summary) > 2000:
                summary = summary[:1997] + "..."

            # Send the final summary back to the channel
            await interaction.followup.send(summary)

        # Handling cases where the bot isn't allowed to see history
        except discord.errors.Forbidden:
            logger.error("Error: Missing permissions to read message history.")

            await interaction.followup.send(f"{ERROR_MESSAGE} I don't have permission to read the message history here.")
        # Catch-all for when things go south
        except Exception as e:
            logger.error(f"Error fetching/summarizing messages: {e}", exc_info=True)

            await interaction.followup.send(f"{ERROR_MESSAGE} Couldn't summarize the chat. Is my coconut battery dead?")


async def setup(bot: commands.Bot):
    """
    Standard discord.py setup function to add the cog to the bot.
    """
    # Hook the cog into the bot at startup
    await bot.add_cog(SummarizeCog(bot))
