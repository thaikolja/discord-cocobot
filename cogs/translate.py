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
from config.config import ERROR_MESSAGE
from utils.helpers import UseAI


class TranslateCog(commands.Cog):
	"""
	A Discord Cog for translating text from one language to another.
	"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@app_commands.command(name="translate", description='Translate text from one language to another')
	@app_commands.describe(
		text='The text to translate',
		from_language='The language code of the source language (Default: Thai)',
		to_language='The language code of the target language (Default: English)'
	)
	async def translate_command(self, interaction: discord.Interaction, text: str, from_language: str = 'Thai', to_language: str = 'English'):
		"""
		A slash command to translate text from one language to another.
		"""
		ai = UseAI(provider='groq')
		output = ai.prompt(f'Translate the text "{text}" from {from_language} to {to_language}. Keep the tone and meaning of the original text.')

		if not output:
			await interaction.response.send_message(ERROR_MESSAGE)
		else:
			await interaction.response.send_message(f"🇹🇭 {output}")


async def setup(bot: commands.Bot):
	await bot.add_cog(TranslateCog(bot))
