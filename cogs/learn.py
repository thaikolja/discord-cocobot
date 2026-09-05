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


# JSON for the Thai word list that is definitely not a spreadsheet
import json

# os.path.isfile so we fail before opening a ghost file
import os

# Random word of the day, without claiming pedagogical rigor
import random

# Discord types for the slash interaction
import discord

# Slash command decorator lives here
from discord import app_commands

# Cog base class
from discord.ext import commands

# Shared coconut error line for when the vocab file ghosts us
from config.config import ERROR_MESSAGE


# Flash-card cog: one random Thai word, zero curriculum
# noinspection PyUnresolvedReferences
class LearnCog(commands.Cog):

    # discord.py hands us the bot; we just keep it
    def __init__(self, bot: commands.Bot):

        # Stash for later; this cog barely uses it, but the pattern is the pattern
        self.bot = bot

    # Slash name "learn" — not "random_thai_noun", unfortunately
    @app_commands.command(
        name="learn",
        description='Displays one of 250 core Thai words and its translation',
    )
    # One interaction, no options: keep it one-tap
    async def learn_command(self, interaction: discord.Interaction):

        # Relative path from process CWD; deploy with the assets folder or cry
        word_list_path = './assets/data/thai-words.json'

        # Missing file: don't pretend we have 250 words in our head
        if not os.path.isfile(word_list_path):

            # Tell the user the coconut is empty
            await interaction.response.send_message(
                f"{ERROR_MESSAGE}: No vocabulary found."
            )

            # Stop before json.load invents a traceback
            return

        # JSON can be truncated mid-deploy; catch that
        try:

            # UTF-8 because Thai is not Latin-1, despite what Windows thinks
            with open(word_list_path, 'r', encoding='utf-8') as file:

                # Parse the whole list into memory; 250 words is not Big Data
                data = json.load(file)

        # File exists but isn't JSON anymore
        except json.JSONDecodeError:

            # Blame the file, not the user
            await interaction.response.send_message(
                f"{ERROR_MESSAGE}: Failed to read vocabulary data. The file may be "
                f"corrupted."
            )

            # Don't fall through with a half-parsed list
            return

        # Permissions, encoding surprises, the usual
        except Exception as e:

            # Surface the exception text; admins will paste it in #dev anyway
            await interaction.response.send_message(
                f"{ERROR_MESSAGE}: An unexpected error occurred: {str(e)}"
            )

            # Abort the flash card
            return

        # Empty list is valid JSON and still useless
        if not data:

            # File was there, just hollow
            await interaction.response.send_message(
                f"{ERROR_MESSAGE}: I found the vocabulary file, but it contains no "
                f"words. Weird."
            )

            # random.choice on [] is a ValueError party
            return

        # Pick one entry; fairness is not a requirement
        word = random.choice(data)

        # Need english, thai, and how to say it — missing any one is junk data
        if (
            not word.get('english')
            or not word.get('thai')
            or not word.get('transliteration')
        ):

            # Don't send "None means None" into Discord
            await interaction.response.send_message(
                f"{ERROR_MESSAGE}: Something's wrong with this word entry. Missing "
                f"key data."
            )

            # Skip this broken row
            return

        # The actual lesson, wrapped in markdown like a gift
        await interaction.response.send_message(
            f'💡 **"{word["english"]}"** means **"{word["thai"]}"** in Thai and is '
            f'spoken like `{word["transliteration"]}`'
        )


# Extension entrypoint discord.py expects
async def setup(bot: commands.Bot):

    # Register LearnCog on the bot
    await bot.add_cog(LearnCog(bot))
