# cogs/time.py
import requests
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from config.config import ERROR_MESSAGE, LOCALTIME_API_KEY
from utils.helpers import sanitize_url

class TimeCog(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@app_commands.command(name="time", description='Get the current time at a certain city or country')
	@app_commands.describe(location='The city or country for which to get the current time (Default: Bangkok)')
	async def time_command(self, interaction: discord.Interaction, location: str = 'Bangkok'):
		try:
			api_url = sanitize_url(f'https://api.ipgeolocation.io/timezone?apiKey={LOCALTIME_API_KEY}&location={location}')
			response = requests.get(api_url)

			if not response.ok:
				raise requests.exceptions.RequestException()

			data = response.json()
			country = data['geo']['country']
			city = data['geo']['city'] or location
			time = datetime.strptime(data['date_time'], '%Y-%m-%d %H:%M:%S')

			output = f"🕓 In **{city}**, **{country}**, it's currently `{time.strftime('%A, %b %d, %H:%M')}`"
			await interaction.response.send_message(output)

		except (requests.exceptions.RequestException, KeyError):
			await interaction.response.send_message(
				f"{ERROR_MESSAGE} Couldn't find time for `{location}`. Maybe it's in a coconut timezone?"
			)

async def setup(bot: commands.Bot):
	await bot.add_cog(TimeCog(bot))