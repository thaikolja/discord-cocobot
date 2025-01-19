import requests
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from utils.helpers import sanitize_url
from config.config import WEATHERAPI_API_KEY


# noinspection PyUnresolvedReferences
class WeatherCog(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@app_commands.command(name="weather", description="Get the current weather for a location")
	@app_commands.describe(location='The location you want the weather for.', units='Choose the unit system: Metric (°C) or Imperial (°F). Defaults to Metric if not specified.')
	@app_commands.choices(units=[app_commands.Choice(name="Civilized Units (°C)", value="metric"), app_commands.Choice(name="Freedom Units (°F)", value="imperial")])
	async def weather_command(self, interaction: discord.Interaction, location: str, units: Optional[app_commands.Choice[str]] = None):
		units_value = "metric" if units is None else units.value
		unit_symbol = "°C" if units_value == "metric" else "°F"
		api_url = f"https://api.weatherapi.com/v1/current.json?key={WEATHERAPI_API_KEY}&q={sanitize_url(location)}"

		try:
			response = requests.get(api_url)
			response.raise_for_status()
		except requests.HTTPError as http_err:
			await interaction.response.send_message(f"HTTP error occurred: {http_err}", ephemeral=True)
			return
		except Exception as err:
			await interaction.response.send_message(f"An error occurred: {err}", ephemeral=True)
			return

		data = response.json()
		city = data['location']['name']
		country = data['location']['country']
		temperature = data['current']['temp_c'] if units_value == "metric" else data['current']['temp_f']
		feels_like = data['current']['feelslike_c'] if units_value == "metric" else data['current']['feelslike_f']
		humidity = data['current']['humidity']
		condition = data['current']['condition']['text'].lower()

		output = (f"🌤️ The weather in **{city}**, **{country}** is currently {condition} with temperatures of `{temperature}{unit_symbol}` "
							f"(feels like `{feels_like}{unit_symbol}`). **Humidity** is at `{humidity}%`.")

		await interaction.response.send_message(output, ephemeral=False)


async def setup(bot: commands.Bot):
	await bot.add_cog(WeatherCog(bot))
