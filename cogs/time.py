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


# Timeouts and async HTTP errors share this namespace
import asyncio

# Cache blobs are JSON strings, not pickled surprises
import json

# Log API failures instead of silently blaming the user
import logging

# Parse the vendor's date_time string into something strftime can dress up
from datetime import datetime

# Non-blocking HTTP so one slow timezone API doesn't freeze the bot
import aiohttp

# Interaction type for the slash command
import discord

# Slash command + describe decorators
from discord import app_commands

# Cog base
from discord.ext import commands

# Cache bypass flag, coconut error line, and the geolocation API key
from config.config import CACHE_BYPASS_PRIVILEGED, ERROR_MESSAGE, LOCALTIME_API_KEY

# SQLite cache so Bangkok time isn't a paid API call every 12 seconds
from utils.database import DatabaseManager

# INFO-level default; discord.py will still shout if it wants
logging.basicConfig(level=logging.INFO)

# Named logger so time-cog errors aren't anonymous
logger = logging.getLogger('discord')


# /time lives here: city in, clock out
# noinspection PyUnresolvedReferences
class TimeCog(commands.Cog):

    # Hold the bot and one shared aiohttp session
    def __init__(self, bot: commands.Bot):

        # Bot reference for cog lifecycle
        self.bot = bot

        # Reuse one ClientSession; opening a session per command is how you DDoS yourself
        self.session = aiohttp.ClientSession()

    # discord.py calls this when the cog is unloaded or the bot shuts down
    async def cog_unload(self):
        """Clean up the aiohttp session when the cog is unloaded."""

        # Close sockets so we don't leak connectors into the void
        await self.session.close()

    # Slash command metadata Discord shows in the picker
    @app_commands.command(
        name="time", description='Get the current time at a certain city or country'
    )
    # Parameter hint so people don't type "earth"
    @app_commands.describe(
        location='The city or country for which to get the current time (Default: Bangkok)',
    )
    # Default Bangkok because this is a Thailand discord, not a UN clock
    async def time_command(
        self, interaction: discord.Interaction, location: str = 'Bangkok'
    ):

        # ipgeolocation timezone endpoint — not Google, not a sundial
        api_url = 'https://api.ipgeolocation.io/timezone'

        # Query params; aiohttp will URL-encode so "New York" doesn't become soup
        params = {'apiKey': LOCALTIME_API_KEY, 'location': location}

        # Cache key is case-folded so Bangkok and bangkok share a slot
        cache_key = f"time:{location.lower()}"

        # Owners/admins/mods can skip stale cache when CACHE_BYPASS_PRIVILEGED is on
        user_is_privileged = (
            CACHE_BYPASS_PRIVILEGED
            and interaction.guild is not None
            and (
                interaction.user.id == interaction.guild.owner_id
                or interaction.user.guild_permissions.administrator
                or interaction.user.guild_permissions.manage_guild
            )
        )

        # Network, cache, and JSON can all fail; one try covers the happy path
        try:

            # Privileged users get a live fetch; everyone else may hit SQLite
            cached_data = None if user_is_privileged else await DatabaseManager.async_get_cache_entry(cache_key)

            # Cache hit: skip the vendor and their invoice
            if cached_data:

                # Deserialize what we stored 10 minutes ago
                data = json.loads(cached_data)

            # Cache miss or admin bypass
            else:

                # 10s timeout so a hung API doesn't hold the slash ack forever
                async with self.session.get(api_url, params=params, timeout=10) as response:

                    # 4xx/5xx become ClientResponseError, caught below
                    response.raise_for_status()

                    # Parse JSON body
                    data = await response.json()

                # Remember this location for 600 seconds; clocks aren't that urgent
                await DatabaseManager.async_set_cache_entry(cache_key, json.dumps(data), 600)

            # Country from the geo blob
            country = data['geo']['country']

            # City may be empty for country-only queries; fall back to what the user typed
            city = data['geo']['city'] or location

            # Vendor format is 'YYYY-MM-DD HH:MM:SS' — not ISO, not helpful, but ours now
            time = datetime.strptime(data['date_time'], '%Y-%m-%d %H:%M:%S')

            # Pretty line with weekday, month, day, 24h clock
            output = f"🕓 In **{city}**, **{country}**, it's currently `{time.strftime('%A, %b %d, %H:%M')}`"

            # First response must use interaction.response, not followup
            await interaction.response.send_message(output)

        # HTTP errors, timeouts, or a JSON shape that forgot 'geo'
        except (aiohttp.ClientError, asyncio.TimeoutError, KeyError) as e:

            # Log location + exception type; the user sees a joke, we see the crime
            logger.error(
                f"Time API failed for location={location!r}: {type(e).__name__}: {e}"
            )

            # August's sundial is the house joke; keep it
            await interaction.response.send_message(
                f"{ERROR_MESSAGE} `{location}` is not on August's sundial. Try a real place, not a hallucination."
            )


# Load TimeCog when the extension is added
async def setup(bot: commands.Bot):

    # Register the cog
    await bot.add_cog(TimeCog(bot))
