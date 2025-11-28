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

# Import the logging library
import logging

# Import the uuid module to generate unique IDs
import uuid

# Import the timeout error exception from the socket module
from socket import timeout as timeout_error

# Import the aiohttp library for async HTTP requests
import aiohttp

# Import the main discord module
import discord

# Import app_commands for slash command functionality
from discord import app_commands

# Import commands extension from discord.ext
from discord.ext import commands

# Import required configuration constants
from config.config import ERROR_MESSAGE, WEATHERAPI_API_KEY

# Import the URL sanitization helper function
from utils.helpers import sanitize_url

# Configure the logger for this module
logger = logging.getLogger(__name__)


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
        # Initialize with no timeout for persistent button functionality
        super().__init__(timeout=None)

        # Store the last interaction object for reference
        self._last_interaction = None

        # Store the location string for API requests
        self.location = location

        # Store the current units system (metric/imperial)
        self.current_units = initial_units

        # Store reference to the weather cog for API access
        self.weather_cog = weather_cog

        # Determine the appropriate label for the toggle button
        label_next = (
            "Freedom Units (°F)"
            if self.current_units == "metric"
            else "Civilized Units (°C)"
        )

        # Create a unique custom_id for the button for this specific view instance
        self.button_custom_id = f"toggle_weather_units_{uuid.uuid4()}"

        # Create a button for toggling temperature units
        # noinspection PyTypeChecker
        self.toggle_button = discord.ui.Button(
            label=f"Show in {label_next}",
            style=discord.ButtonStyle.primary,
            custom_id=self.button_custom_id,
        )

        # Assign the callback function for button clicks
        self.toggle_button.callback = self.on_toggle_units

        # Add the button to the view
        self.add_item(self.toggle_button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Store the last interaction for timeout editing.

        Args:
                        interaction: The Discord interaction object.

        Returns:
                        bool: Always returns True to allow the interaction.
        """
        # Store the interaction object for later reference
        self._last_interaction = interaction

        # Allow the interaction to proceed
        return True

    async def on_toggle_units(self, interaction: discord.Interaction):
        """
        Callback for the toggle units button.
        Fetches weather data in the opposite unit system and updates the message.

        Args:
                        interaction: The Discord interaction object.
        """
        # Acknowledge the interaction without immediate visible response
        # noinspection PyUnresolvedReferences
        await interaction.response.defer()

        # Switch between metric and imperial units
        target_units = "imperial" if self.current_units == "metric" else "metric"

        # Set the appropriate temperature unit symbol
        unit_symbol = "°F" if target_units == "imperial" else "°C"

        # Determine which API keys to use based on units
        temp_key = "temp_f" if target_units == "imperial" else "temp_c"

        # Determine which feels-like key to use based on units
        feels_key = "feelslike_f" if target_units == "imperial" else "feelslike_c"

        # Sanitize the location string for the API request
        sanitized = sanitize_url(self.location)

        # Construct the API URL with the API key and location
        url = f"https://api.weatherapi.com/v1/current.json?key={WEATHERAPI_API_KEY}&q={sanitized}"

        try:
            # Make the API request with a timeout
            async with self.weather_cog.session.get(url, timeout=10) as resp:

                # Raise an exception for HTTP errors
                resp.raise_for_status()

                # Parse the JSON response data
                data = await resp.json()

            # Check for required data sections
            if not data.get("location") or not data.get("current"):
                # Log error for debugging purposes
                logger.error("Incomplete weather data on toggle: %r", data)

                # Send error message to the user
                return await interaction.followup.send(
                    f"{ERROR_MESSAGE} Incomplete data while toggling.", ephemeral=True
                )

            # Extract location data from response
            loc = data["location"]

            # Extract current weather data from response
            cur = data["current"]

            # Extract condition data with empty fallback
            cond = cur.get("condition", {})

            # Extract city name with fallback
            city = loc.get("name", "Unknown")

            # Extract country name with fallback
            country = loc.get("country", "Unknown")

            # Extract temperature value
            temp = cur.get(temp_key)

            # Extract feels-like temperature value
            feels = cur.get(feels_key)

            # Extract humidity value
            humidity = cur.get("humidity")

            # Extract weather condition text with fallback
            cond_text = cond.get("text", "unknown").lower()

            # Extract weather icon URL
            icon = cond.get("icon")

            # Format the full icon URL if available
            icon_url = f"https:{icon}" if icon else None

            # Ensure all required weather metrics are present
            if temp is None or feels is None or humidity is None:
                # Log the error for debugging
                logger.error("Missing metrics on toggle: %r", cur)

                # Send error message to the user
                return await interaction.followup.send(
                    f"{ERROR_MESSAGE} Failed to parse key metrics while toggling.",
                    ephemeral=True,
                )

            # Create a new Discord embed for weather information
            embed = discord.Embed(
                title=f"Weather in {city}, {country}",
                description=f"Currently **{cond_text}**.",
                color=discord.Color.blue(),
            )

            # Add the weather icon if available
            if icon_url:
                embed.set_thumbnail(url=icon_url)

            # Add temperature field to the embed
            embed.add_field(
                name="Temperature", value=f"`{temp}{unit_symbol}`", inline=True
            )

            # Add feels-like temperature field
            embed.add_field(
                name="Feels Like", value=f"`{feels}{unit_symbol}`", inline=True
            )

            # Add humidity percentage field
            embed.add_field(name="Humidity", value=f"`{humidity}%`", inline=True)

            # Add units information to embed footer
            embed.set_footer(text=f"Units: {target_units.capitalize()}")

            # Add current timestamp to the embed
            embed.timestamp = discord.utils.utcnow()

            # Update the current units state
            self.current_units = target_units

            # Update button label for next toggle
            next_label = (
                "Freedom Units (°F)"
                if self.current_units == "metric"
                else "Civilized Units (°C)"
            )

            # Change the button text to reflect new toggle option
            self.toggle_button.label = f"Show in {next_label}"

            # Update the original message with new embed and view
            await interaction.message.edit(embed=embed, view=self)

            # Return None to indicate success
            return None

        except aiohttp.ClientResponseError as e:
            # Log HTTP errors from the API
            logger.error("HTTP error %s on toggle: %s", e.status, e)

            # Create default error message
            msg = f"{ERROR_MESSAGE} Weather API error ({e.status}) while toggling."

            # Override with more specific message for common errors
            if e.status == 400:
                msg = f"{ERROR_MESSAGE} Invalid location '{self.location}'."

            # Send error message to the user
            return await interaction.followup.send(msg, ephemeral=True)

        except Exception as e:
            # Log unexpected errors
            logger.exception(
                "Unexpected error toggling weather units for %s: {e}", self.location, e
            )

            # Send generic error message to the user
            return await interaction.followup.send(
                f"{ERROR_MESSAGE} {e}", ephemeral=True
            )


class WeatherCog(commands.Cog):
    """
    A Cog representing weather-related commands for a Discord bot.
    """

    def __init__(self, bot: commands.Bot):
        """
        Initializes the WeatherCog with a bot instance and sets up an aiohttp session.

        Args:
                        bot: The Discord bot instance.
        """
        # Store reference to the bot
        self.bot = bot

        # Create HTTP session for API requests
        self.session = aiohttp.ClientSession()

        # Initialize list to track persistent views
        self.persistent_views = []

    async def cog_load(self):
        """
        Registers persistent views after the cog is loaded.
        """

    # Views will be registered via bot.add_view in the command handler

    async def cog_unload(self):
        """
        Closes the aiohttp session when the cog is unloaded.
        """
        # Clean up HTTP session when cog is removed
        await self.session.close()

    @app_commands.command(
        name="weather", description="Get the current weather for a location"
    )
    @app_commands.describe(
        location="The location you want the weather for (Default: Bangkok)",
        units="Unit system: Metric (°C) or Imperial (°F).",
    )
    @app_commands.choices(
        units=[
            app_commands.Choice(name="Civilized Units (°C)", value="metric"),
            app_commands.Choice(name="Freedom Units (°F)", value="imperial"),
        ]
    )
    async def weather_command(
        self,
        interaction: discord.Interaction,
        location: str = "Bangkok",
        units: app_commands.Choice[str] = None,
    ):
        """
        Slash the command handler for /weather that displays weather for a location.

        Args:
                        interaction: The Discord interaction object.
                        location: The location to get weather for.
                        units: Choice of units (metric or imperial).
        """
        # Defer response to allow time for API call
        # noinspection PyUnresolvedReferences
        await interaction.response.defer(ephemeral=False)

        # Use metric units by default if not specified
        units_val = units.value if units else "metric"

        # Select temperature symbol based on units
        symbol = "°C" if units_val == "metric" else "°F"

        # Select temperature key based on units
        temp_k = "temp_c" if units_val == "metric" else "temp_f"

        # Select feels-like key based on units
        feels_k = "feelslike_c" if units_val == "metric" else "feelslike_f"

        # Sanitize location for API request
        sanitized = sanitize_url(location)

        # Construct the API URL
        url = f"https://api.weatherapi.com/v1/current.json?key={WEATHERAPI_API_KEY}&q={sanitized}"

        try:
            # Make the API request with a timeout
            async with self.session.get(url, timeout=10) as resp:

                # Raise exception for HTTP errors
                resp.raise_for_status()

                # Parse the JSON response
                data = await resp.json()

            # Check for required data sections
            if not data.get("location") or not data.get("current"):
                # Log error for debugging
                logger.error("Incomplete data for %s: %r", location, data)

                # Send error message to user
                return await interaction.followup.send(
                    f"{ERROR_MESSAGE} Incomplete data received."
                )

            # Extract location data
            loc = data["location"]

            # Extract current weather data
            cur = data["current"]

            # Extract condition data with empty fallback
            cond = cur.get("condition", {})

            # Extract city name with fallback
            city = loc.get("name", "Unknown City")

            # Extract country name with fallback
            country = loc.get("country", "Unknown Country")

            # Extract temperature value
            temp = cur.get(temp_k)

            # Extract feels-like temperature value
            feels = cur.get(feels_k)

            # Extract humidity value
            humidity = cur.get("humidity")

            # Extract weather condition text with fallback
            cond_text = cond.get("text", "unknown").lower()

            # Extract weather icon URL
            icon = cond.get("icon")

            # Format the full icon URL if available
            icon_url = f"https:{icon}" if icon else None

            # Ensure all required weather metrics are present
            if temp is None or feels is None or humidity is None:
                # Log the error for debugging
                logger.error("Missing metrics for %s: %r", location, cur)

                # Send error message to user
                return await interaction.followup.send(
                    f"{ERROR_MESSAGE} Failed to parse essential weather details."
                )

            # Create a new Discord embed for weather information
            embed = discord.Embed(
                title=f"Weather in {city}, {country}",
                description=f"Currently **{cond_text}**.",
                color=discord.Color.blue(),
            )

            # Add the weather icon if available
            if icon_url:
                embed.set_thumbnail(url=icon_url)

            # Add temperature field to the embed
            embed.add_field(name="Temperature", value=f"`{temp}{symbol}`", inline=True)

            # Add feels-like temperature field
            embed.add_field(name="Feels Like", value=f"`{feels}{symbol}`", inline=True)

            # Add humidity percentage field
            embed.add_field(name="Humidity", value=f"`{humidity}%`", inline=True)

            # Add units information to embed footer
            embed.set_footer(text=f"Units: {units_val.capitalize()}")

            # Add current timestamp to the embed
            embed.timestamp = discord.utils.utcnow()

            # Create the weather view with toggle button
            view = WeatherView(location, units_val, self)

            # Store the view for persistence
            self.persistent_views.append(view)

            # Register view with the bot for persistent functionality
            self.bot.add_view(view)

            # Send the response with embed and view
            await interaction.followup.send(embed=embed, view=view)

            # Return None to indicate success
            return None

        except aiohttp.ContentTypeError as e:
            # Log JSON parsing errors
            logger.error("JSON decode error for %s: %s", location, e)

            # Send error message to user
            return await interaction.followup.send(
                f"{ERROR_MESSAGE} Received invalid data from the weather service."
            )

        except aiohttp.ClientResponseError as e:
            # Log HTTP errors
            logger.error("HTTP error %s for %s: %s", e.status, location, e)

            # Create default error message
            msg = f"{ERROR_MESSAGE} Weather API error ({e.status})."

            # Override with more specific messages for common errors
            if e.status == 401:
                msg = f"{ERROR_MESSAGE} Invalid API key."
            elif e.status == 400:
                msg = f"{ERROR_MESSAGE} Invalid location '{location}'."

            # Send error message to user
            return await interaction.followup.send(msg)

        except aiohttp.ClientError as e:
            # Log network/client errors
            logger.error("AIOHTTP error for %s: %s", location, e)

            # Send network error message to user
            return await interaction.followup.send(
                f"{ERROR_MESSAGE} Network issue contacting weather service."
            )

        except timeout_error:
            # Log timeout errors
            logger.error("Timeout for %s", location)

            # Send timeout error message to user
            return await interaction.followup.send(
                f"{ERROR_MESSAGE} The weather service timed out."
            )

        except Exception as e:
            # Log unexpected errors
            logger.exception("Unexpected error for %s: {e}", location)

            # Send generic error message to user
            return await interaction.followup.send(f"{ERROR_MESSAGE} {e}")


async def setup(bot: commands.Bot):
    """
    A setup function to add the WeatherCog to the bot.

    Args:
                    bot: The Discord bot instance.
    """
    # Register the WeatherCog with the bot
    await bot.add_cog(WeatherCog(bot))
