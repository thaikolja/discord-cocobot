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

# Import the logging library for logging purposes
import logging

# Import the aiohttp library for making asynchronous HTTP requests
import aiohttp

# Import the discord library for interacting with the Discord API
import discord

# Import the commands module from discord.ext for command handling
from discord.ext import commands

# Import the app_commands module from discord for slash command support
from discord import app_commands

# Import the sanitize_url function from the utils.helpers module
from utils.helpers import sanitize_url

# Import the WEATHERAPI_API_KEY and ERROR_MESSAGE constants from the config.config module
from config.config import WEATHERAPI_API_KEY, ERROR_MESSAGE

# Set up the logger for this file
logger = logging.getLogger(__name__)


# Define a View for the weather message to handle button interactions
class WeatherView(discord.ui.View):
	"""
	A View with a button to toggle weather units between Celsius and Fahrenheit.
	"""

	def __init__(self, location: str, initial_units: str, weather_cog):
		"""
		Initializes the WeatherView.

		Args:
				location (str): The location the weather is for.
				initial_units (str): The units currently displayed ('metric' or 'imperial').
				weather_cog (WeatherCog): Reference to the WeatherCog instance for API calls.
		"""
		super().__init__(timeout=300)  # 5 minutes
		self._last_interaction = None
		self.location = location
		self.current_units = initial_units
		self.weather_cog = weather_cog

		# Build the toggle button
		label_next = "Freedom Units (°F)" if self.current_units == "metric" else "Civilized Units (°C)"
		# noinspection PyTypeChecker
		self.toggle_button = discord.ui.Button(
			label=f"Show in {label_next}",
			style=discord.ButtonStyle.primary,
			custom_id="toggle_weather_units"
		)
		self.toggle_button.callback = self.on_toggle_units
		self.add_item(self.toggle_button)

	async def interaction_check(self, interaction: discord.Interaction) -> bool:
		"""
		Store the last interaction for timeout editing.
		"""
		self._last_interaction = interaction
		return True

	async def on_toggle_units(self, interaction: discord.Interaction):
		"""
		Callback for the toggle units button.
		Fetches weather data in the opposite unit system and updates the message.
		"""
		# ACK the button click (no visible update yet)
		# noinspection PyUnresolvedReferences
		await interaction.response.defer()

		# flip units
		target_units = "imperial" if self.current_units == "metric" else "metric"
		unit_symbol = "°F" if target_units == "imperial" else "°C"
		temp_key = "temp_f" if target_units == "imperial" else "temp_c"
		feels_key = "feelslike_f" if target_units == "imperial" else "feelslike_c"

		sanitized = sanitize_url(self.location)
		url = f"https://api.weatherapi.com/v1/current.json?key={WEATHERAPI_API_KEY}&q={sanitized}"

		try:
			async with self.weather_cog.session.get(url, timeout=10) as resp:
				resp.raise_for_status()
				data = await resp.json()

			# guard
			if not data.get("location") or not data.get("current"):
				logger.error("Incomplete weather data on toggle: %r", data)
				return await interaction.followup.send(
					f"{ERROR_MESSAGE} Incomplete data while toggling.",
					ephemeral=True
				)

			loc = data["location"]
			cur = data["current"]
			cond = cur.get("condition", {})

			city = loc.get("name", "Unknown")
			country = loc.get("country", "Unknown")
			temp = cur.get(temp_key)
			feels = cur.get(feels_key)
			humidity = cur.get("humidity")
			cond_text = cond.get("text", "unknown").lower()
			icon = cond.get("icon")
			icon_url = f"https:{icon}" if icon else None

			if temp is None or feels is None or humidity is None:
				logger.error("Missing metrics on toggle: %r", cur)
				return await interaction.followup.send(
					f"{ERROR_MESSAGE} Failed to parse key metrics while toggling.",
					ephemeral=True
				)

			# build embed
			embed = discord.Embed(
				title=f"Weather in {city}, {country}",
				description=f"Currently **{cond_text}**.",
				color=discord.Color.blue()
			)
			if icon_url:
				embed.set_thumbnail(url=icon_url)

			embed.add_field(name="Temperature", value=f"`{temp}{unit_symbol}`", inline=True)
			embed.add_field(name="Feels Like", value=f"`{feels}{unit_symbol}`", inline=True)
			embed.add_field(name="Humidity", value=f"`{humidity}%`", inline=True)
			embed.set_footer(text=f"Units: {target_units.capitalize()}")
			embed.timestamp = discord.utils.utcnow()

			# update state & label
			self.current_units = target_units
			next_label = "Freedom Units (°F)" if self.current_units == "metric" else "Civilized Units (°C)"
			self.toggle_button.label = f"Show in {next_label}"

			# finally edit the actual message the button sits on
			await interaction.message.edit(embed=embed, view=self)

			return None

		except aiohttp.ClientResponseError as e:
			logger.error("HTTP error %s on toggle: %s", e.status, e)
			msg = f"{ERROR_MESSAGE} Weather API error ({e.status}) while toggling."
			if e.status == 400:
				msg = f"{ERROR_MESSAGE} Invalid location '{self.location}'."
			return await interaction.followup.send(msg, ephemeral=True)

		except Exception as e:
			logger.exception("Unexpected error toggling weather units for %s: {e}", self.location)
			return await interaction.followup.send(
				f"{ERROR_MESSAGE} {e}",
				ephemeral=True
			)

	async def on_timeout(self):
		"""
		Called when the view times out. Disables the button.
		"""
		for item in self.children:
			item.disabled = True

		# Try to cleanly edit the message one last time
		try:
			if hasattr(self, "_last_interaction"):
				await self._last_interaction.message.edit(view=self)
		except Exception as e:
			logger.warning("Could not disable button on timeout: %s", e)


# Define a class WeatherCog that inherits from commands.Cog
class WeatherCog(commands.Cog):
	"""
	A Cog representing weather-related commands for a Discord bot.
	"""

	def __init__(self, bot: commands.Bot):
		"""
		Initializes the WeatherCog with a bot instance and sets up an aiohttp session.
		"""
		self.bot = bot
		self.session = aiohttp.ClientSession()

	async def cog_unload(self):
		"""
		Closes the aiohttp session when the cog is unloaded.
		"""
		await self.session.close()

	@app_commands.command(name="weather", description="Get the current weather for a location")
	@app_commands.describe(
		location="The location you want the weather for (Default: Bangkok)",
		units="Unit system: Metric (°C) or Imperial (°F)."
	)
	@app_commands.choices(
		units=[
			app_commands.Choice(name="Civilized Units (°C)", value="metric"),
			app_commands.Choice(name="Freedom Units (°F)", value="imperial")
		]
	)
	async def weather_command(
		self,
		interaction: discord.Interaction,
		location: str = "Bangkok",
		units: app_commands.Choice[str] = None
	):
		# defer so we can send a followup with view
		# noinspection PyUnresolvedReferences
		await interaction.response.defer(ephemeral=False)

		units_val = units.value if units else "metric"
		symbol = "°C" if units_val == "metric" else "°F"
		temp_k = "temp_c" if units_val == "metric" else "temp_f"
		feels_k = "feelslike_c" if units_val == "metric" else "feelslike_f"

		sanitized = sanitize_url(location)
		url = f"https://api.weatherapi.com/v1/current.json?key={WEATHERAPI_API_KEY}&q={sanitized}"

		try:
			async with self.session.get(url, timeout=10) as resp:
				resp.raise_for_status()
				data = await resp.json()

			if not data.get("location") or not data.get("current"):
				logger.error("Incomplete data for %s: %r", location, data)
				return await interaction.followup.send(
					f"{ERROR_MESSAGE} Incomplete data received."
				)

			loc = data["location"]
			cur = data["current"]
			cond = cur.get("condition", {})

			city = loc.get("name", "Unknown City")
			country = loc.get("country", "Unknown Country")
			temp = cur.get(temp_k)
			feels = cur.get(feels_k)
			humidity = cur.get("humidity")
			cond_text = cond.get("text", "unknown").lower()
			icon = cond.get("icon")
			icon_url = f"https:{icon}" if icon else None

			if temp is None or feels is None or humidity is None:
				logger.error("Missing metrics for %s: %r", location, cur)
				return await interaction.followup.send(
					f"{ERROR_MESSAGE} Failed to parse essential weather details."
				)

			embed = discord.Embed(
				title=f"Weather in {city}, {country}",
				description=f"Currently **{cond_text}**.",
				color=discord.Color.blue()
			)
			if icon_url:
				embed.set_thumbnail(url=icon_url)

			embed.add_field(name="Temperature", value=f"`{temp}{symbol}`", inline=True)
			embed.add_field(name="Feels Like", value=f"`{feels}{symbol}`", inline=True)
			embed.add_field(name="Humidity", value=f"`{humidity}%`", inline=True)
			embed.set_footer(text=f"Units: {units_val.capitalize()}")
			embed.timestamp = discord.utils.utcnow()

			# send the embed with our toggle view
			view = WeatherView(location, units_val, self)
			await interaction.followup.send(embed=embed, view=view)

			return None

		except aiohttp.ContentTypeError as e:
			logger.error("JSON decode error for %s: %s", location, e)
			return await interaction.followup.send(
				f"{ERROR_MESSAGE} Received invalid data from the weather service."
			)
		except aiohttp.ClientResponseError as e:
			logger.error("HTTP error %s for %s: %s", e.status, location, e)
			msg = f"{ERROR_MESSAGE} Weather API error ({e.status})."
			if e.status == 401:
				msg = f"{ERROR_MESSAGE} Invalid API key."
			elif e.status == 400:
				msg = f"{ERROR_MESSAGE} Invalid location '{location}'."
			return await interaction.followup.send(msg)

		except aiohttp.ClientError as e:
			logger.error("AIOHTTP error for %s: %s", location, e)
			return await interaction.followup.send(
				f"{ERROR_MESSAGE} Network issue contacting weather service."
			)

		except TimeoutError:
			logger.error("Timeout for %s", location)
			return await interaction.followup.send(
				f"{ERROR_MESSAGE} The weather service timed out."
			)

		except Exception as e:
			logger.exception("Unexpected error for %s: {e}", location)
			return await interaction.followup.send(
				f"{ERROR_MESSAGE} {e}"
			)


async def setup(bot: commands.Bot):
	"""
	A setup function to add the WeatherCog to the bot.
	"""
	await bot.add_cog(WeatherCog(bot))
