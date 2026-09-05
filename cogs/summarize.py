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

"""
This module provides the SummarizeCog, which uses an AI model to summarize
recent chat messages in a Discord channel.
"""

# Thread off the LLM so the event loop doesn't nap through a 50-message recap
import asyncio

# Errors here are "who said what" plus model flakes; log them
import logging

# Channel history, followups, Forbidden — the usual Discord weather
import discord

# Slash command + Range so users can't ask for 10,000 messages "just to see"
from discord import app_commands

# Cog base class; still the least painful extension story
from discord.ext import commands

# Shared error string when the model or prompt file ghosts us
from config.config import ERROR_MESSAGE

# Provider wrapper; summarize may not use the same model as translate
from utils.helpers import UseAI

# Prompt renderer: keep the "be funny but useful" instructions out of this file
from utils.prompts import render_language_prompt

# Use the discord logger so recap errors sit next to gateway noise
logger = logging.getLogger('discord')


# "What did I miss" as a slash command, with coconut editorializing
class SummarizeCog(commands.Cog):
    """
    A Discord Cog that provides message summarization using AI.
    It's basically a shorthand for "what did I miss while I was getting a coffee?".
    """

    def __init__(self, bot: commands.Bot):
        """
        Initialize the cog with the bot instance and the AI helper.
        """
        # Bot handle for future use (and because every cog does this)
        self.bot = bot

        # Late import so tests can stub os.getenv without loading this at module import
        import os

        # Deepseek by default; override if you like living on Gemini quotas
        summary_provider = os.getenv("SUMMARY_PROVIDER", "deepseek")

        # One helper instance per cog; no per-command construction tax
        self.ai = UseAI(summary_provider)

    # Register /summarize with Discord's command catalog
    @app_commands.command(
        name="summarize",
        description="Summarize recent messages in the current channel"
    )
    # Cap is 50; this is a recap, not a deposition
    @app_commands.describe(
        limit="Number of recent messages to summarize (Default: 20, Max: 50)"
    )
    async def summarize_command(self, interaction: discord.Interaction, limit: app_commands.Range[int, 1, 50] = 20):
        """
        Summarize recent messages in the current channel based on the specified limit of messages. The summary aims to
        capture key topics, agreements, or comedic points while maintaining a slightly humorous tone.

        Parameters:
            interaction (discord.Interaction): The interaction object representing the user's command input.
            limit (app_commands.Range[int, 1, 50]): The number of recent messages to summarize. Defaults to 20, with a maximum of 50.

        Raises:
            discord.errors.Forbidden: Raised when the bot lacks permissions to read the message history of the channel.
            Exception: Raised when an unexpected error occurs during message fetching or summarization.

        """
        # Defer unless someone already acknowledged this interaction
        try:
            # Double-defer is a Discord crime; check first
            if not interaction.response.is_done():
                # Buy time; history + LLM is not a 3-second job
                await interaction.response.defer()

        # Token already dead; try a channel ping as a consolation prize
        except discord.NotFound:
            # Best-effort shout into the channel
            try:
                # Mention the user so they know it wasn't silently eaten
                await interaction.channel.send(
                    f"🥥 {interaction.user.mention} The command took too long to process. Please try again!"
                )

            # Channel send can fail too; swallow it, we're already in a hole
            except Exception:
                # Nothing left to do except leave
                pass

            # Don't continue into followup land
            return

        # Mystery defer failure: abort without a speech
        except Exception:
            # Silent return matches original behavior
            return

        # Fetch, transcript, prompt, send — or explain why not
        try:
            # Newest-first from Discord; we'll reverse in a minute
            messages = [msg async for msg in interaction.channel.history(limit=limit)]

            # Empty channel: rare, but don't call an LLM about the void
            if not messages:
                # Kabakon-empty, not just "no messages"
                await interaction.followup.send(
                    "Nothing to recap. This channel is as empty as Kabakon after the copra ran out."
                )

                # Early exit; no reverse, no prompt
                return

            # Chronological order so the summary isn't a time-travel documentary
            messages.reverse()

            # Collect "Name: text" lines; skip the empty husks
            transcript_lines = []

            # Walk every fetched message
            for msg in messages:
                # Display name beats username for recaps
                author_name = msg.author.display_name

                # Mentions resolved; less "@123" soup for the model
                content = msg.clean_content

                # Stickers and blank pings don't summarize well
                if content:
                    # One line per utterance
                    transcript_lines.append(f"{author_name}: {content}")

            # All attachments, no words: still nothing to preach
            if not transcript_lines:
                # Ask for sentences, not husks
                await interaction.followup.send(
                    "Only husks, no pulp. I need actual sentences before I preach the gospel of the coconut."
                )

                # Don't spend tokens on emptiness
                return

            # One blob for the prompt template
            transcript = "\n".join(transcript_lines)

            # Fill the summarize prompt; False later means "don't extra-think"
            prompt = render_language_prompt('summarize', transcript=transcript)

            # Missing prompt file: generic error, not a stack dump
            if not prompt:
                # Same ERROR_MESSAGE as the rest of the bot
                await interaction.followup.send(ERROR_MESSAGE)

                # No prompt, no summary
                return

            # Thread pool: keep gateway heartbeats alive during the model call
            summary = await asyncio.to_thread(self.ai.prompt, str(prompt), False)

            # Model returned nothing useful
            if not summary:
                # August declined; user still needs a message
                await interaction.followup.send(
                    f"{ERROR_MESSAGE} August stared at the transcript and declined to waste sunlight on it."
                )

                # Don't send an empty followup
                return

            # Discord isn't a novel; clip the sermon
            if len(summary) > 1000:
                # 800 plus ellipsis is the house style
                summary = summary[:800] + "..."

            # Ship the recap
            await interaction.followup.send(summary)

        # Can't read history: permissions, not the model
        except discord.errors.Forbidden:
            # Log for whoever forgot Read Message History
            logger.error("Error: Missing permissions to read message history.")

            # User-facing: even a sun-king needs the keys
            await interaction.followup.send(
                f"{ERROR_MESSAGE} I am not allowed to read this channel. Even a sun-king needs the keys to the hut."
            )

        # Anything else: log with traceback, joke in channel
        except Exception as e:
            # Keep the exception; humidity is not a stack frame
            logger.error(f"Error fetching/summarizing messages: {e}", exc_info=True)

            # Blame Kolja; it's tradition
            await interaction.followup.send(
                f"{ERROR_MESSAGE} The recap press seized. Blame the humidity, or Kolja. Mostly Kolja."
            )


# Extension loader
async def setup(bot: commands.Bot):
    """
    Standard discord.py setup function to add the cog to the bot.
    """
    # Attach SummarizeCog at boot
    await bot.add_cog(SummarizeCog(bot))
