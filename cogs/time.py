import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime


class TimeCog(commands.Cog):
	"""
	A cog for time-related commands.
	"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@app_commands.command(name="time", description="Get the current server time")
	async def time_command(self, interaction: discord.Interaction):
		"""
		Slash command to get the current server time.
		"""
		now = datetime.now()
		current_time = now.strftime("%H:%M:%S")  # Format as HH:MM:SS
		await interaction.response.send_message(f"The current time is {current_time}", ephemeral=False)

# If you have other time-related commands, you can add them here


async def setup(bot: commands.Bot):
	"""
	Asynchronous setup function to add the TimeCog to the bot.
	"""
	await bot.add_cog(TimeCog(bot))
