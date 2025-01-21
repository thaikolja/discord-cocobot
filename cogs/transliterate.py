#  Copyright (C) 2025 by Kolja Nolte
#  kolja.nolte@gmail.com
#  https://gitlab.com/thaikolja/discord-cocobot
#
#  This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
#  You are free to use, share, and adapt this work for non-commercial purposes, provided that you:
#  - Give appropriate credit to the original author.
#  - Provide a link to the license.
#  - Distribute your contributions under the same license.
#
#  For more information, visit: https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#  Author:    Kolja Nolte
#  Email:     kolja.nolte@gmail.com
#  License:   CC BY-NC-SA 4.0
#  Date:      2014-2025
#  Package:   Thailand Discord

import discord
from discord.ext import commands
from discord import app_commands
from utils.helpers import UseAI


# noinspection PyUnresolvedReferences
class Transliterate(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@app_commands.command(name="transliterate", description='Transliterate Thai text to Latin script')
	@app_commands.describe(text='The text to transliterate')
	async def transliterate_command(self, interaction: discord.Interaction, text: str):
		prompt = (f"Transliterate the Thai text '{text}' into Latin characters only. Use diacritics to display the tone markers for every consonant and vowel. Make it readable for "
							f"English "
							f"readers. ")

		ai = UseAI(provider='google')

		answer = ai.prompt(prompt)

		await interaction.response.send_message(answer)


async def setup(bot: commands.Bot):
	await bot.add_cog(Transliterate(bot))
