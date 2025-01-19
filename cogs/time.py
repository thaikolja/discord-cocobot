import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from config.config import TIMEZONEDB_API_KEY
import requests


# noinspection PyUnresolvedReferences
class TimeCog(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@app_commands.command(name="time", description="Get the current server time")
	@app_commands.describe(location="The location you want the time for (Default: \"Thailand\").")
	async def time_command(self, interaction: discord.Interaction, location: str = 'Thailand'):
		now = datetime.now()
		tz = now.astimezone().tzinfo
		current_time = now.strftime("%H:%M") + f" ({tz})"

		await interaction.response.send_message(f"🕰️ The current time in **{location}** is {current_time}", ephemeral=False)


async def setup(bot: commands.Bot):
	await bot.add_cog(TimeCog(bot))
