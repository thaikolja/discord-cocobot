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
This module provides the RecapCog, which uses an AI model to deliver a
brutally honest, judging summary of what a specified user has been talking
about in chat.
"""

import asyncio
import logging
import os
import random
import time

import discord
from discord import app_commands
from discord.ext import commands

from config.config import ERROR_MESSAGE
from utils.helpers import UseAI

logger = logging.getLogger('discord')

RECAP_STYLES = [
    "witty and sarcastic",
    "brutal and sarcastic",
    "playful and sarcastic",
    "dry and sarcastic",
    "over-the-top dramatic and sarcastic",
    "deadpan and sarcastic",
]

RECAP_TIMEOUT = 15  # seconds


class RecapCog(commands.Cog):
    """
    A Discord Cog that provides a /roast command that delivers a judging
    summary of a user using AI.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._recap_prompt: str | None = None
        self._knowledge: str | None = None
        self._recap_history: dict[int, list[float]] = {}

    def _load_prompt(self) -> str:
        """Load and cache the recap prompt from file."""
        prompt_path = os.getenv("RECAP_PROMPT_PATH", "assets/data/recap-prompt.md")
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        possible_paths = [
            os.path.join(project_root, prompt_path),
            os.path.join(project_root, "assets/data/recap-prompt.md"),
            os.path.join(project_root, "data/assets/recap-prompt.md"),
        ]

        resolved_path = None
        for p in possible_paths:
            if os.path.exists(p):
                resolved_path = p
                break

        # If not found, create it at the default location
        if not resolved_path:
            resolved_path = os.path.join(project_root, prompt_path)
            try:
                os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
                with open(resolved_path, "w", encoding="utf-8") as f:
                    f.write(
                        "You are @cocobot, a coconut-powered Discord bot that delivers absolutely "
                        "devastating, psychologically cruel judgments. You have no boundaries, no mercy, "
                        "no filter. You tear people apart based entirely on their own words and choices. "
                        "Your goal is to psychologically destroy them through a brutally honest recap of "
                        "their chat history. You are insulting, offensive, and merciless — delivered "
                        "through sharp, dark sarcasm and a touch of coconut-obsessed craziness. There is "
                        "no kindness, no compliments, no redemption — only damning, evil judgment. You "
                        "know exactly who you are: you're @cocobot. Never mention August Engelhardt by "
                        "name. Never sound like an AI."
                    )
            except Exception as e:
                logger.error(f"Failed to create default recap prompt file: {e}")
                return ""

        # Read prompt content
        prompt_content = ""
        if resolved_path and os.path.exists(resolved_path):
            try:
                with open(resolved_path, "r", encoding="utf-8") as f:
                    prompt_content = f.read().strip()
            except Exception as e:
                logger.error(f"Failed to read recap prompt file: {e}")
                return ""

        return prompt_content

    def _load_knowledge(self) -> str:
        """Load and cache all knowledge files from the knowledge directory."""
        knowledge_dir = os.getenv("RECAP_KNOWLEDGE_PATH", "assets/data/knowledge")
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        knowledge_path = os.path.join(project_root, knowledge_dir)

        if not os.path.isdir(knowledge_path):
            return ""

        parts = []
        for filename in sorted(os.listdir(knowledge_path)):
            if filename.endswith(".md"):
                filepath = os.path.join(knowledge_path, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                    if content:
                        parts.append(f"### {filename}\n{content}")
                except Exception as e:
                    logger.error(f"Failed to read knowledge file {filename}: {e}")

        combined = "\n\n".join(parts)

        # Truncate at 100KB (100,000 characters)
        if len(combined) > 100000:
            combined = combined[:100000]

        return combined

    def _soft_truncate(self, text: str, max_chars: int = 650) -> str:
        """Truncate text at last sentence boundary before max_chars."""
        if len(text) <= max_chars:
            return text

        # Find last sentence boundary (., !, ?) before max_chars
        truncated = text[:max_chars]
        last_sentence = max(
            truncated.rfind('.'),
            truncated.rfind('!'),
            truncated.rfind('?')
        )

        if last_sentence > max_chars * 0.7:  # At least 70% of limit
            return truncated[:last_sentence + 1]

        # No good sentence boundary, hard truncate with ellipsis
        return truncated.rstrip() + "..."

    @app_commands.command(
        name="roast",
        description="Deliver a brutally honest, judging summary of what a user has been saying"
    )
    @app_commands.describe(
        user="The user to judge"
    )
    async def roast_command(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):
        """
        Delivers a judging summary of a user based on their chat history using AI.
        """
        # Lazy load prompt and knowledge (cached)
        if self._recap_prompt is None:
            self._recap_prompt = self._load_prompt()
        if self._knowledge is None:
            self._knowledge = self._load_knowledge()

        prompt_content = self._recap_prompt
        knowledge = self._knowledge

        # If empty or too short (<= 50 chars), stop and notify ephemerally
        if len(prompt_content) <= 50:
            is_ephemeral = os.getenv("RECAP_EPHEMERAL_NOTICE", "true").lower() == "true"
            await interaction.response.send_message(
                "❌ The recap prompt is empty or too short (must be > 50 characters). Please configure it properly in the recap prompt file.",
                ephemeral=is_ephemeral
            )
            return

        # Check rate limit (3 per hour) before defer
        rate_limit_enabled = os.getenv("RECAP_RATE_LIMIT_ENABLED", "true").lower() == "true"
        if rate_limit_enabled:
            now = time.time()
            user_id = interaction.user.id
            self._recap_history.setdefault(user_id, [])
            # Keep only timestamps from last hour
            self._recap_history[user_id] = [t for t in self._recap_history[user_id] if now - t < 3600]

            if len(self._recap_history[user_id]) >= 3:
                await interaction.response.send_message(
                    "🥥 You've judged 3 people in the last hour. Give your coconut a rest.",
                    ephemeral=True
                )
                return

            self._recap_history[user_id].append(now)

        # Defer the interaction response since AI request takes time
        try:
            await interaction.response.defer()
        except discord.errors.NotFound:
            logger.warning(f"Interaction expired for roast command by {interaction.user}")
            return
        except Exception as e:
            logger.error(f"Failed to defer interaction: {e}")
            return

        try:
            # Fetch user messages across channels in specific categories
            messages = []
            start_time = time.time()

            # 1. Search current channel first (most important for context)
            try:
                if interaction.channel.permissions_for(user).view_channel:
                    async for msg in interaction.channel.history(limit=200):
                        if len(messages) >= 20:
                            break
                        if time.time() - start_time > RECAP_TIMEOUT:
                            break
                        if msg.author.id == user.id and msg.clean_content:
                            messages.append(msg)
            except discord.errors.Forbidden:
                pass

            # 2. Get channels from configured categories
            category_ids_str = os.getenv("RECAP_CATEGORY_IDS", "")
            if category_ids_str:
                category_ids = [int(cid.strip()) for cid in category_ids_str.split(",") if cid.strip()]

                recap_channels = []
                for category_id in category_ids:
                    category = interaction.guild.get_channel(category_id)
                    if category and hasattr(category, 'channels'):
                        for channel in category.channels:
                            # Skip current channel (already searched)
                            if channel.id == interaction.channel.id:
                                continue

                            # Skip if target user can't view this channel
                            if not channel.permissions_for(user).view_channel:
                                continue

                            # Skip if channel is empty
                            if not channel.last_message_id:
                                continue

                            recap_channels.append(channel)

                # Shuffle channels randomly
                random.shuffle(recap_channels)

                # 3. Iterate through channels
                for channel in recap_channels:
                    if len(messages) >= 20:
                        break
                    if time.time() - start_time > RECAP_TIMEOUT:
                        logger.warning("Recap message collection timed out after 15 seconds")
                        break

                    try:
                        async for msg in channel.history(limit=200):
                            if len(messages) >= 20:
                                break
                            if time.time() - start_time > RECAP_TIMEOUT:
                                break
                            if msg.author.id == user.id and msg.clean_content:
                                messages.append(msg)
                    except discord.errors.Forbidden:
                        continue

            # Check minimum 10 messages
            if len(messages) < 10:
                await interaction.followup.send(
                    f"🥥 {user.mention} hasn't said enough in any public channel (need at least 10 messages, found {len(messages)}). "
                    f"Tell them to chat more before they get judged."
                )
                return

            # Detect self-recap
            is_self_recap = user.id == interaction.user.id

            # Randomize/shuffle messages if enabled
            shuffle_enabled = os.getenv("RECAP_SHUFFLE_MESSAGES", "true").lower() == "true"
            if shuffle_enabled:
                random.shuffle(messages)

            # Build transcript
            transcript_lines = []
            for msg in messages:
                author_name = msg.author.display_name
                content = msg.clean_content
                transcript_lines.append(f"{author_name}: {content}")

            transcript = "\n".join(transcript_lines)

            # Select random style
            style = random.choice(RECAP_STYLES)

            # Build prompt sections
            prompt_sections = []

            # 1. Knowledge first (if available)
            if knowledge:
                prompt_sections.append(f"## Background Knowledge\n{knowledge}")

            # 2. Core recap prompt
            prompt_sections.append(prompt_content)

            # 3. Style and language instructions
            style_instructions = f"""
## Instructions
- Your judging style: {style}. Sarcasm must be present throughout.
- You must write your judgment in English, regardless of the language the messages are in.
- Address the user in third person (he/she), never use second person (you).
- Output only paragraphs and plain text. No lists, no bullet points, no numbered items.
- Remove ALL line breaks. The output must be a single continuous paragraph.
- Use markdown bold (**) or italic (*) ONLY to emphasize specific words — use sparingly.
- Don't sound like an AI. Write like a cynical, sarcastic human who despises weakness and mediocrity.
- Embed the user's name naturally somewhere in the text — never as a standalone first line.
- Use the background knowledge about the server's themes to enhance your psychological takedown.
- No kindness, no compliments, no redemption, no silver linings — only damning, evil judgment.
- Channel a touch of coconut-obsessed craziness in your delivery.
- Your goal is to psychologically destroy them based entirely on their own words and choices.
- Aim for approximately 1500 characters.
"""
            if is_self_recap:
                style_instructions += "- This is a self-judging recap. Make it extra self-deprecating and devastating — you know yourself better than anyone, use that to psychologically destroy them even more.\n"

            prompt_sections.append(style_instructions)

            # 4. Messages to judge
            prompt_sections.append(f"## Messages to judge\n{transcript}")

            full_prompt = "\n\n".join(prompt_sections)

            # Grab AI settings
            provider = os.getenv("RECAP_PROVIDER", "deepseek")
            api_key = os.getenv("RECAP_PROVIDER_API_KEY")
            model = os.getenv("RECAP_PROVIDER_MODEL", "deepseek-v4-flash")

            fallback_provider = os.getenv("RECAP_FALLBACK_PROVIDER") or None
            fallback_api_key = os.getenv("RECAP_FALLBACK_PROVIDER_API_KEY") or None
            fallback_model = os.getenv("RECAP_FALLBACK_PROVIDER_MODEL") or None

            # Initialize UseAI
            ai = UseAI(
                provider=provider,
                api_key=api_key if api_key else None,
                model=model if model else None,
                fallback_provider=fallback_provider,
                fallback_api_key=fallback_api_key,
                fallback_model=fallback_model
            )

            # Call AI
            recap_output = await asyncio.to_thread(ai.prompt, full_prompt, False)

            if not recap_output:
                await interaction.followup.send(f"{ERROR_MESSAGE} The AI failed to generate a judgment.")
                return

            # Check minimum length (80 chars)
            if len(recap_output) < 80:
                # Ask AI to expand
                expand_prompt = f"Your judgment was too short ({len(recap_output)} characters). Expand it to at least 80 characters while keeping the same sarcastic, insulting style:\n\n{recap_output}"
                recap_output = await asyncio.to_thread(ai.prompt, expand_prompt, False)

                if not recap_output:
                    await interaction.followup.send(f"{ERROR_MESSAGE} The AI failed to expand the judgment.")
                    return

            # Soft truncate at 650 characters
            recap_output = self._soft_truncate(recap_output, 650)

            # Send with mention toggle
            mention_enabled = os.getenv("RECAP_MENTION_USER", "true").lower() == "true"
            if mention_enabled:
                message = await interaction.followup.send(f"{user.mention} {recap_output}")
            else:
                message = await interaction.followup.send(recap_output)

            # Add reactions
            await message.add_reaction("🔥")

        except discord.errors.Forbidden:
            logger.error("Missing permissions to read channel history.")
            await interaction.followup.send(f"{ERROR_MESSAGE} I don't have permission to read the message history here.")
        except Exception as e:
            logger.error(f"Error during roast command: {e}", exc_info=True)
            await interaction.followup.send(f"{ERROR_MESSAGE} Is my coconut battery dead?")


async def setup(bot: commands.Bot):
    """
    Standard setup function for discord.py to load the cog.
    """
    await bot.add_cog(RecapCog(bot))
