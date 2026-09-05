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


# Cache payloads ride as JSON strings; we pack and unpack them here
import json

# Named logger so weather failures don't hide in the root logger
import logging

# Unique button IDs; Discord will not share custom_ids like a commune
import uuid

# Socket timeout alias used when WeatherAPI ghosts us
from socket import timeout as timeout_error

# Async HTTP; requests would block the event loop and the coconut
import aiohttp

# Discord types for embeds, views, and interactions
import discord

# Slash commands and their describe/choice decorators
from discord import app_commands

# Cog base class
from discord.ext import commands

# API key, error copy, and who gets to skip the cache
from config.config import CACHE_BYPASS_PRIVILEGED, ERROR_MESSAGE, WEATHERAPI_API_KEY

# Cache get/set so we don't hammer WeatherAPI every humidity check
from utils.database import DatabaseManager

# Channel city fallback plus URL-safe location strings
from utils.helpers import resolve_channel_location, sanitize_url

# Module logger: weather.py, not "root"
logger = logging.getLogger(__name__)


# Persistent view: one button to flip °C / °F
class WeatherView(discord.ui.View):
    """
    Represents a custom Discord UI view for toggling weather temperature units.

    This class provides a Discord interactive user interface allowing users to
    toggle between temperature units, either metric or imperial, directly via
    a button. It fetches weather data based on the user's specified location
    and updates the Discord embed with relevant weather information.

    Attributes:
        location (str): The user's location, which is used for making API requests
            to retrieve weather data.
        current_units (str): The current temperature unit system, either "metric"
            or "imperial".
        weather_cog: The reference to the weather cog instance that is used
            to handle API requests and related logic.
        button_custom_id (str): A unique ID for the toggle button, ensuring
            functionality is specific to this view instance.
        toggle_button (discord.ui.Button): The interactive button used for toggling
            temperature units.
    """

    # Build the toggle button and stash location + units
    def __init__(self, location: str, initial_units: str, weather_cog: "WeatherCog") -> None:
        """
        Initializes a view containing a button for toggling weather temperature units.

        This class represents a custom Discord UI view featuring a button that allows
        users to toggle between temperature units (e.g., metric and imperial). It holds
        additional attributes to manage the user's selected location, the current
        temperature unit system, and a reference to the weather cog which provides
        logic for retrieving weather data.

        Args:
            location (str): The user's location used for API requests.
            initial_units (str): Initial temperature unit system; can be either "metric"
                or "imperial".
            weather_cog: The weather cog instance, used for interacting with weather
                APIs.
        """
        # timeout=None: the button outlives the original interaction
        super().__init__(timeout=None)

        # Last interaction, in case we need it later
        self._last_interaction = None

        # Location string we will hit WeatherAPI with
        self.location = location

        # metric or imperial, currently showing
        self.current_units = initial_units

        # Cog holds the shared ClientSession
        self.weather_cog = weather_cog

        # Label for the *next* unit system; Freedom vs Civilized is the joke
        label_next = (
            "Freedom Units (°F)"
            if self.current_units == "metric"
            else "Civilized Units (°C)"
        )

        # UUID so two weather cards don't share a custom_id
        self.button_custom_id = f"toggle_weather_units_{uuid.uuid4()}"

        # Primary button; PyTypeChecker doesn't love ui.Button assignment
        # noinspection PyTypeChecker
        self.toggle_button = discord.ui.Button(
            label=f"Show in {label_next}",
            style=discord.ButtonStyle.primary,
            custom_id=self.button_custom_id,
        )

        # Wire clicks to the toggle handler
        self.toggle_button.callback = self.on_toggle_units

        # Attach the button to this view
        self.add_item(self.toggle_button)

    # Discord asks; we store the interaction and always allow
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Checks the validity of a given interaction and stores it for later use.

        This function evaluates the provided Discord interaction and determines
        whether it is valid for the current context. If valid, it stores the
        interaction for future reference and allows it to proceed.

        Args:
            interaction (discord.Interaction): The interaction object that
                represents the user's action within the Discord server.

        Returns:
            bool: Returns True if the interaction is allowed to proceed; otherwise,
                False.
        """
        # Remember who clicked
        self._last_interaction = interaction

        # Always proceed; privilege checks happen on fetch
        return True

    # Flip units, refetch or cache, rewrite the embed
    async def on_toggle_units(self, interaction: discord.Interaction) -> None:
        """
        Handles the user interaction to toggle between metric and imperial weather units
        and updates the weather information display accordingly.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's
                action in Discord, used to trigger this handler.
        """
        # Defer so Discord doesn't time out while we talk to WeatherAPI
        # noinspection PyUnresolvedReferences
        await interaction.response.defer()

        # Flip the unit system
        target_units = "imperial" if self.current_units == "metric" else "metric"

        # Degree symbol matching the target
        unit_symbol = "°F" if target_units == "imperial" else "°C"

        # WeatherAPI field names: temp_f vs temp_c
        temp_key = "temp_f" if target_units == "imperial" else "temp_c"

        # Same split for feels-like
        feels_key = "feelslike_f" if target_units == "imperial" else "feelslike_c"

        # Sanitize so "Bangkok?" doesn't become a broken query
        sanitized = sanitize_url(self.location)

        # Current-conditions endpoint with the bot's key
        url = f"https://api.weatherapi.com/v1/current.json?key={WEATHERAPI_API_KEY}&q={sanitized}"

        # Cache keyed by place + units so °C and °F don't collide
        cache_key = f"weather:{sanitized}:{target_units}"

        # Admins/owners/mods skip cache when the flag is on
        user_is_privileged = (
            CACHE_BYPASS_PRIVILEGED
            and interaction.guild is not None
            and (
                interaction.user.id == interaction.guild.owner_id
                or interaction.user.guild_permissions.administrator
                or interaction.user.guild_permissions.manage_guild
            )
        )

        # Network + parse + embed update
        try:
            # Privileged users always miss cache on purpose
            cached_data = None if user_is_privileged else await DatabaseManager.async_get_cache_entry(cache_key)

            # Hit: decode JSON
            if cached_data:
                # Cached string back to dict
                data = json.loads(cached_data)

            # Miss: actually call WeatherAPI
            else:
                # 10s timeout; Thailand humidity isn't worth hanging
                async with self.weather_cog.session.get(url, timeout=10) as resp:
                    # 4xx/5xx become exceptions
                    resp.raise_for_status()

                    # Parse body
                    data = await resp.json()

                # Ten minutes; weather doesn't change that fast in Bangkok
                await DatabaseManager.async_set_cache_entry(cache_key, json.dumps(data), 600)

            # Need both location and current blobs
            if not data.get("location") or not data.get("current"):
                # Log the truncated payload
                logger.error("Incomplete weather data on toggle: %r", data)

                # Ephemeral error; don't wreck the original embed
                return await interaction.followup.send(
                    f"{ERROR_MESSAGE} Incomplete data while toggling.", ephemeral=True
                )

            # Place metadata
            loc = data["location"]

            # Current observation
            cur = data["current"]

            # Condition object, or empty if WeatherAPI got lazy
            cond = cur.get("condition", {})

            # City name
            city = loc.get("name", "Unknown")

            # Country name
            country = loc.get("country", "Unknown")

            # Temperature in the requested unit
            temp = cur.get(temp_key)

            # Feels-like in the same unit
            feels = cur.get(feels_key)

            # Humidity percent
            humidity = cur.get("humidity")

            # Condition text, lowercased for the sentence
            cond_text = cond.get("text", "unknown").lower()

            # Icon path from the API
            icon = cond.get("icon")

            # Protocol-relative URLs need https:
            icon_url = f"https:{icon}" if icon else None

            # All three metrics required or we refuse to lie
            if temp is None or feels is None or humidity is None:
                # Log the current blob
                logger.error("Missing metrics on toggle: %r", cur)

                # Ephemeral parse failure
                return await interaction.followup.send(
                    f"{ERROR_MESSAGE} Failed to parse key metrics while toggling.",
                    ephemeral=True,
                )

            # Rebuild the blue weather embed
            embed = discord.Embed(
                title=f"Weather in {city}, {country}",
                description=f"Currently **{cond_text}**.",
                color=discord.Color.blue(),
            )

            # Thumbnail if we have an icon
            if icon_url:
                # Discord will fetch it
                embed.set_thumbnail(url=icon_url)

            # Temperature field
            embed.add_field(
                name="Temperature", value=f"`{temp}{unit_symbol}`", inline=True
            )

            # Feels-like field
            embed.add_field(
                name="Feels Like", value=f"`{feels}{unit_symbol}`", inline=True
            )

            # Humidity field
            embed.add_field(name="Humidity", value=f"`{humidity}%`", inline=True)

            # Footer says which unit system won
            embed.set_footer(text=f"Units: {target_units.capitalize()}")

            # Fresh timestamp
            embed.timestamp = discord.utils.utcnow()

            # Remember the new unit system
            self.current_units = target_units

            # Next click should offer the other system
            next_label = (
                "Freedom Units (°F)"
                if self.current_units == "metric"
                else "Civilized Units (°C)"
            )

            # Update button copy
            self.toggle_button.label = f"Show in {next_label}"

            # Edit the original message in place
            await interaction.message.edit(embed=embed, view=self)

            # Success sentinel
            return None

        # HTTP errors from WeatherAPI
        except aiohttp.ClientResponseError as e:
            # Status + exception text
            logger.error("HTTP error %s on toggle: %s", e.status, e)

            # Generic API error copy
            msg = f"{ERROR_MESSAGE} Weather API error ({e.status}) while toggling."

            # 400 usually means "that isn't a place"
            if e.status == 400:
                # Name the bad location
                msg = f"{ERROR_MESSAGE} Invalid location '{self.location}'."

            # Ephemeral so the channel stays clean
            return await interaction.followup.send(msg, ephemeral=True)

        # Anything else: log stack, show the exception
        except Exception as e:
            # exception() includes traceback
            logger.exception(
                "Unexpected error toggling weather units for %s: {e}", self.location, e
            )

            # Surface the error string
            return await interaction.followup.send(
                f"{ERROR_MESSAGE} {e}", ephemeral=True
            )


# Cog: /weather plus a shared aiohttp session
class WeatherCog(commands.Cog):
    """
    A Discord bot cog for retrieving and displaying weather information using the WeatherAPI.

    WeatherCog is designed to integrate with a Discord bot and provide weather reports for
    specific locations using a command-based interface. It establishes and manages an HTTP
    session for making requests to the WeatherAPI, processes the received data, and formats
    it into a user-friendly Discord embed. Additionally, it supports persistent interactive
    views for user interaction.

    Attributes:
        bot (commands.Bot): Reference to the bot instance the cog is attached to.
        session (aiohttp.ClientSession): An aiohttp session for making API requests.
        persistent_views (list): A list used to retain persistent views registered with
            the bot.
    """

    # Bind bot, open session, empty view list
    def __init__(self, bot: commands.Bot):
        """
        Initializes the WeatherCog with a bot instance and sets up an aiohttp session.

        Args:
                        bot: The Discord bot instance.
        """
        # Keep the bot for add_view
        self.bot = bot

        # One session for the cog lifetime
        self.session = aiohttp.ClientSession()

        # Strong refs so persistent views aren't GC'd
        self.persistent_views = []

    # Hook after load; views register in the command instead
    async def cog_load(self):
        """
        Registers persistent views after the cog is loaded.
        """

    # Views will be registered via bot.add_view in the command handler

    # Close HTTP when the cog is yanked
    async def cog_unload(self):
        """
        Closes the aiohttp session when the cog is unloaded.
        """
        # Don't leak connectors
        await self.session.close()

    # Slash command metadata: name + description
    @app_commands.command(
        name="weather", description="Get the current weather for a location"
    )
    # Argument help text
    @app_commands.describe(
        location="The location you want the weather for (defaults to the channel's city, or Bangkok)",
        units="Unit system: Metric (°C) or Imperial (°F).",
    )
    # Two choices: Civilized vs Freedom, as the server demanded
    @app_commands.choices(
        units=[
            app_commands.Choice(name="Civilized Units (°C)", value="metric"),
            app_commands.Choice(name="Freedom Units (°F)", value="imperial"),
        ]
    )
    # The actual /weather handler
    async def weather_command(
        self,
        interaction: discord.Interaction,
        location: str | None = None,
        units: app_commands.Choice[str] = None,
    ):
        """
        Handles the `weather` command which retrieves current weather information for a
        specified location using the WeatherAPI and displays it to the user as a Discord embed
        with relevant weather details.

        Args:
            interaction (discord.Interaction): The interaction object for the Discord command
                invocation.
            location (str, optional): The location to retrieve weather data for. Defaults
                to "Bangkok".
            units (app_commands.Choice[str], optional): Unit system to use for weather data.
                Choices are "metric" (°C) or "imperial" (°F). If not provided, defaults to "metric".

        Raises:
            aiohttp.ContentTypeError: Raised if the JSON parsing of the API response fails.
            aiohttp.ClientResponseError: Raised for HTTP response errors from the WeatherAPI.
            aiohttp.ClientError: Raised for general network or client errors during the API
                request.
            timeout_error: Raised if the request to the WeatherAPI server times out.
            Exception: Raised for any unexpected errors encountered.

        Returns:
            None: The function sends an embed or error message directly to the user on successful
                execution or on failure.
        """
        # Defer publicly; weather takes longer than Discord's 3s
        # noinspection PyUnresolvedReferences
        await interaction.response.defer(ephemeral=False)

        # No location: channel city or Bangkok
        if location is None:
            # Helper knows the channel map
            location = resolve_channel_location(interaction)

        # Default metric if they skipped the choice
        units_val = units.value if units else "metric"

        # Symbol for the embed
        symbol = "°C" if units_val == "metric" else "°F"

        # API temp field
        temp_k = "temp_c" if units_val == "metric" else "temp_f"

        # API feels-like field
        feels_k = "feelslike_c" if units_val == "metric" else "feelslike_f"

        # URL-safe query
        sanitized = sanitize_url(location)

        # Current weather endpoint
        url = f"https://api.weatherapi.com/v1/current.json?key={WEATHERAPI_API_KEY}&q={sanitized}"

        # Cache key includes units
        cache_key = f"weather:{sanitized}:{units_val}"

        # Same privilege bypass as the toggle
        user_is_privileged = (
            CACHE_BYPASS_PRIVILEGED
            and interaction.guild is not None
            and (
                interaction.user.id == interaction.guild.owner_id
                or interaction.user.guild_permissions.administrator
                or interaction.user.guild_permissions.manage_guild
            )
        )

        # Fetch, parse, embed, register view
        try:
            # Skip cache for privileged users
            cached_data = None if user_is_privileged else await DatabaseManager.async_get_cache_entry(cache_key)

            # Use cache
            if cached_data:
                # JSON string to dict
                data = json.loads(cached_data)

            # Live request
            else:
                # 10 second timeout
                async with self.session.get(url, timeout=10) as resp:

                    # Fail on HTTP errors
                    resp.raise_for_status()

                    # Parse JSON
                    data = await resp.json()

                # Cache 10 minutes
                await DatabaseManager.async_set_cache_entry(cache_key, json.dumps(data), 600)

            # Need location + current
            if not data.get("location") or not data.get("current"):
                # Log incomplete payload
                logger.error("Incomplete data for %s: %r", location, data)

                # Follow-up error
                return await interaction.followup.send(
                    f"{ERROR_MESSAGE} Incomplete data received."
                )

            # Location blob
            loc = data["location"]

            # Current blob
            cur = data["current"]

            # Condition with fallback
            cond = cur.get("condition", {})

            # City
            city = loc.get("name", "Unknown City")

            # Country
            country = loc.get("country", "Unknown Country")

            # Temperature
            temp = cur.get(temp_k)

            # Feels-like
            feels = cur.get(feels_k)

            # Humidity
            humidity = cur.get("humidity")

            # Condition sentence
            cond_text = cond.get("text", "unknown").lower()

            # Icon path
            icon = cond.get("icon")

            # Full icon URL
            icon_url = f"https:{icon}" if icon else None

            # Require all three metrics
            if temp is None or feels is None or humidity is None:
                # Log missing fields
                logger.error("Missing metrics for %s: %r", location, cur)

                # User-facing parse error
                return await interaction.followup.send(
                    f"{ERROR_MESSAGE} Failed to parse essential weather details."
                )

            # Build embed
            embed = discord.Embed(
                title=f"Weather in {city}, {country}",
                description=f"Currently **{cond_text}**.",
                color=discord.Color.blue(),
            )

            # Icon thumbnail
            if icon_url:
                # Set it
                embed.set_thumbnail(url=icon_url)

            # Temperature
            embed.add_field(name="Temperature", value=f"`{temp}{symbol}`", inline=True)

            # Feels like
            embed.add_field(name="Feels Like", value=f"`{feels}{symbol}`", inline=True)

            # Humidity
            embed.add_field(name="Humidity", value=f"`{humidity}%`", inline=True)

            # Footer with unit system
            embed.set_footer(text=f"Units: {units_val.capitalize()}")

            # Timestamp now
            embed.timestamp = discord.utils.utcnow()

            # Toggle view bound to this location
            view = WeatherView(location, units_val, self)

            # Keep a reference
            self.persistent_views.append(view)

            # Register for persistent custom_id handling
            self.bot.add_view(view)

            # Send embed + button
            await interaction.followup.send(embed=embed, view=view)

            # Success
            return None

        # Body wasn't JSON
        except aiohttp.ContentTypeError as e:
            # Log decode failure
            logger.error("JSON decode error for %s: %s", location, e)

            # Tell the user the service sent garbage
            return await interaction.followup.send(
                f"{ERROR_MESSAGE} Received invalid data from the weather service."
            )

        # HTTP status errors
        except aiohttp.ClientResponseError as e:
            # Log status
            logger.error("HTTP error %s for %s: %s", e.status, location, e)

            # Default message
            msg = f"{ERROR_MESSAGE} Weather API error ({e.status})."

            # Bad API key
            if e.status == 401:
                # Don't leak the key, just say it's wrong
                msg = f"{ERROR_MESSAGE} Invalid API key."

            # Bad location
            elif e.status == 400:
                # Quote the query
                msg = f"{ERROR_MESSAGE} Invalid location '{location}'."

            # Send whatever we picked
            return await interaction.followup.send(msg)

        # Network-level aiohttp errors
        except aiohttp.ClientError as e:
            # Log
            logger.error("AIOHTTP error for %s: %s", location, e)

            # Network copy
            return await interaction.followup.send(
                f"{ERROR_MESSAGE} Network issue contacting weather service."
            )

        # Socket timeout
        except timeout_error:
            # Log location
            logger.error("Timeout for %s", location)

            # Timeout copy
            return await interaction.followup.send(
                f"{ERROR_MESSAGE} The weather service timed out."
            )

        # Catch-all with the Kabakon line
        except Exception:
            # Full traceback; exception is attached by logger.exception
            logger.exception("Unexpected weather error for %s", location)

            # User-facing monsoon of incompetence
            return await interaction.followup.send(
                f"{ERROR_MESSAGE} The sky over Kabakon refused to report. Try again after the next monsoon of incompetence."
            )


# discord.py entry: add this cog
async def setup(bot: commands.Bot):
    """
    Registers the WeatherCog with the given bot instance.

    The method sets up the WeatherCog as a component of the provided bot,
    allowing the bot to utilize all functionalities defined in the WeatherCog.

    Args:
        bot (commands.Bot): The bot instance to which the WeatherCog will be
            registered.

    """
    # Attach WeatherCog to the bot
    await bot.add_cog(WeatherCog(bot))
