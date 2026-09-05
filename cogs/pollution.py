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

"""
Registers the PollutionCog with the given bot instance.

Parameters:
bot (commands.Bot): The bot instance to which the cog will be added.
"""

# Cache stores JSON blobs; we unpack them later
import json

# Parse the station's ISO timestamp
from datetime import datetime

# Bangkok time so "ago" isn't UTC-lying to Thai users
from zoneinfo import ZoneInfo

# Async HTTP for WAQI
import aiohttp

# Discord interaction types
import discord

# Slash commands
from discord import app_commands

# Cog base
from discord.ext import commands

# Human-readable "3 minutes ago"
from humanize import naturaltime

# Token, cache bypass, error banner
from config.config import ACQIN_API_KEY, CACHE_BYPASS_PRIVILEGED, ERROR_MESSAGE

# Cache get/set
from utils.database import DatabaseManager

# City from channel name + URL hygiene
from utils.helpers import resolve_channel_location, sanitize_url


# AQI with coconut health advice; Bangkok if you omit the city
# noinspection PyUnresolvedReferences
class PollutionCog(commands.Cog):
    """
    A Discord Cog for showing up-to-date pollution data and AQI in the entered city.
    """

    def __init__(self, bot: commands.Bot):
        """
        Initializes the PollutionCog with the given bot instance.

        Parameters:
        bot (commands.Bot): The bot instance to which this cog is added.
        """
        # Keep the bot around
        self.bot = bot

    # /pollution
    @app_commands.command(
        name="pollution",
        description='Shows up-to-date pollution data and AQI in the specified city',
    )
    # Optional city; channel name is the fallback
    @app_commands.describe(
        city='The city to check the pollution data for (defaults to the channel\'s city, or Bangkok)'
    )
    async def pollution_command(
        self, interaction: discord.Interaction, city: str | None = None
    ):
        """
        A slash command to show up-to-date pollution data and AQI in the entered city.

        Parameters:
        interaction (discord.Interaction): The interaction object representing the command invocation.
        city (str | None): The city to check. If omitted, inferred from the channel name.
        """
        # No city typed → guess from the channel, else Bangkok
        if city is None:
            # Helper owns the mapping; don't duplicate it here
            city = resolve_channel_location(interaction)

        # Token in the URL; sanitize so city names don't break the path
        api_url = sanitize_url(
            f'https://api.waqi.info/feed/{city}/?token={ACQIN_API_KEY}'
        )

        # Lowercase city so "Bangkok" and "bangkok" share a cache slot
        cache_key = f"pollution:{city.lower()}"

        # Same privilege bypass as exchangerate
        user_is_privileged = (
            CACHE_BYPASS_PRIVILEGED
            and interaction.guild is not None
            and (
                interaction.user.id == interaction.guild.owner_id
                or interaction.user.guild_permissions.administrator
                or interaction.user.guild_permissions.manage_guild
            )
        )

        # Cache or live fetch, then sermonize the AQI
        try:
            # Privileged: skip cache
            cached_data = None if user_is_privileged else await DatabaseManager.async_get_cache_entry(cache_key)

            # Cache hit
            if cached_data:
                # Parse what we stored
                data = json.loads(cached_data)

            # Cache miss: hit WAQI
            else:
                # Session + GET
                async with aiohttp.ClientSession() as session:
                    # Fetch the feed
                    async with session.get(api_url) as response:
                        # HTTP failure
                        if response.status != 200:
                            # Connection error copy, original string
                            await interaction.response.send_message(
                                f"{ERROR_MESSAGE} Looks like there's been some connection error. Give it another shot."
                            )

                            # Don't parse a sad body
                            return

                        # JSON body
                        data = await response.json()

                # WAQI uses status "ok" even when HTTP is 200
                if data['status'] != 'ok':
                    # Usually a typo in the city name
                    await interaction.response.send_message(
                        f"{ERROR_MESSAGE} Check your spelling of \"{city}\" and give it another shot."
                    )

                    # Don't cache failures
                    return

                # Ten-minute cache of a good payload
                await DatabaseManager.async_set_cache_entry(cache_key, json.dumps(data), 600)

            # Unwrap the inner data object
            data = data['data']

            # The number people actually want
            aqi = data['aqi']

            # Official station name may differ from what they typed
            city = data['city']['name']

            # Station clock
            parsed_time = datetime.fromisoformat(data['time']['iso'])

            # Compare in Bangkok, not UTC
            bangkok_now = datetime.now(ZoneInfo('Asia/Bangkok'))

            # Timedelta for humanize
            time_diff = bangkok_now - parsed_time

            # Stations in the future: take abs so we still say "ago"
            updated_ago = naturaltime(abs(time_diff.total_seconds()))

            # Base sentence with AQI
            pre_output = f"The PM2.5 level in **{city}** is at `{aqi}` **AQI**."

            # Color-coded coconut commentary
            if aqi <= 50:
                # Green: Engelhardt would worship this air
                emoji, message = (
                    "🟢",
                    "The air is so clean, it's like a vacuum sealed coconut fresh off the tree. August Engelhardt would be proud (and probably try to worship it, too).",
                )

            # Moderate
            elif aqi <= 100:
                # Yellow: fine, not a lifestyle
                emoji, message = (
                    "🟡",
                    "Decent air. Like a coconut: refreshing, but not life-changing.",
                )

            # Unhealthy for sensitive groups
            elif aqi <= 150:
                # Orange: stay in
                emoji, message = (
                    "🟠",
                    "Not great, not terrible. Stay in, unless you fancy a diet of delusions. Wear a mask.",
                )

            # Unhealthy
            elif aqi <= 200:
                # Red: mask up, freedom arguments ignored
                emoji, message = (
                    "🔴",
                    "Unhealthy. Breathing's like Engelhardt's coconut-only dreams. Wear a mask - and, no, it's not \"infringing on your freedom.\"",
                )

            # Hazardous
            else:
                # Black: even coconuts can't save this
                emoji, message = (
                    "⚫️",
                    "Apocalypse air! Even Engelhardt's coconuts couldn't save this. Mask up, or you'll be seeing coconuts soon.",
                )

            # Glue emoji, facts, sermon, timestamp
            output = f"{emoji} {pre_output} {message} (Last checked: {updated_ago})"

            # Reply
            await interaction.response.send_message(output)

        # Anything unexpected
        except Exception as e:
            # Include str(e); original behavior, not a new format
            output = f"{ERROR_MESSAGE} An error occurred while fetching pollution data: {str(e)}"

            # Still try to answer
            await interaction.response.send_message(output)


# discord.py loader
async def setup(bot: commands.Bot):
    """
    A setup function to add the PollutionCog to the bot.

    Parameters:
    bot (commands.Bot): The bot instance to which this cog is added.
    """
    # Add PollutionCog
    await bot.add_cog(PollutionCog(bot))
