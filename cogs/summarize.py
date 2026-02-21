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

import asyncio
import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from config.config import ERROR_MESSAGE
from utils.helpers import UseAI

logger = logging.getLogger('discord')


class SummarizeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ai = UseAI('google')

    @app_commands.command(
        name="summarize",
        description="Summarize recent messages in the current channel."
    )
    @app_commands.describe(
        limit="Number of recent messages to summarize (Default: 25, Max: 25)"
    )
    async def summarize_command(self, interaction: discord.Interaction, limit: app_commands.Range[int, 1, 25] = 25):
        """
        Summarize recent messages in the current channel based on the specified limit of messages. The summary aims to
        capture key topics, agreements, or comedic points while maintaining a slightly humorous tone.

        Parameters:
            interaction (discord.Interaction): The interaction object representing the user's command input.
            limit (app_commands.Range[int, 1, 25]): The number of recent messages to summarize. Defaults to 25, with a maximum of 25.

        Raises:
            discord.errors.Forbidden: Raised when the bot lacks permissions to read the message history of the channel.
            Exception: Raised when an unexpected error occurs during message fetching or summarization.

        """
        # Acknowledge the interaction immediately since LLM processing takes time
        await interaction.response.defer()

        try:
            messages = [msg async for msg in interaction.channel.history(limit=limit)]

            # If there are no messages, notify the user.
            if not messages:
                await interaction.followup.send("Nothing to summarize here. Is the channel as deserted as August's Kabakon?")

                return

            # Note: channel.history returns messages from newest to oldest. Reverse them to maintain chronological order.
            messages.reverse()

            transcript_lines = []
            for msg in messages:
                # Avoid passing bot messages if they clutter, but here we summarize everything.
                author_name = msg.author.display_name
                content = msg.clean_content
                if content:
                    transcript_lines.append(f"{author_name}: {content}")

            if not transcript_lines:
                await interaction.followup.send("Could not find any text content to summarize.")

                return

            transcript = "\\n".join(transcript_lines)
            prompt = (
                f"Provide a concise summary of the following chat transcript with no more than **maximum 600 characters**. "
                f"Capture the **main topics**, agreements, or funny remarks without listing every detail. ",
                f"Write as paragraph. Keep the tone slightly sarcastic and humorous, but not too much. Avoid being too formal.",
                f"Return only the summary and nothing else. The content to summarize: \\n\\n",
                f"{transcript}"
            )

            # Run the LLM prompt in an executor to avoid blocking the asyncio event loop
            summary = await asyncio.to_thread(self.ai.prompt, str(prompt), False)

            if not summary:
                await interaction.followup.send(f"{ERROR_MESSAGE} The AI failed to generate a summary.")

                return

            # Let's not create a wall of text, please
            if len(summary) > 2000:
                summary = summary[:1997] + "..."

            await interaction.followup.send(summary)

        except discord.errors.Forbidden:
            logger.error("Error: Missing permissions to read message history.")

            await interaction.followup.send(f"{ERROR_MESSAGE} I don't have permission to read the message history here.")
        except Exception as e:
            logger.error(f"Error fetching/summarizing messages: {e}", exc_info=True)

            await interaction.followup.send(f"{ERROR_MESSAGE} Couldn't summarize the chat. Is my coconut battery dead?")


async def setup(bot: commands.Bot):
    await bot.add_cog(SummarizeCog(bot))
