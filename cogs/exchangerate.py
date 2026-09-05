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

# Cache payloads are JSON strings; decode before we talk money
import json

# When the money-changers shrug, we still want a traceback
import logging

# Parse the API's last_updated_at into something humanize understands
from datetime import datetime

# Async HTTP so we don't block the bot on currencyapi
import aiohttp

# Interaction types and send_message
import discord

# Slash command + describe
from discord import app_commands

# Cog base
from discord.ext import commands

# "3 minutes ago" beats ISO timestamps in a chat channel
from humanize import naturaltime

# API key, cache-bypass flag, and the shared error banner
from config.config import CACHE_BYPASS_PRIVILEGED, CURRENCYAPI_API_KEY, ERROR_MESSAGE

# SQLite/async cache so we don't hammer the paid endpoint
from utils.database import DatabaseManager

# Logger named after this module, not "root"
logger = logging.getLogger(__name__)


# USD→THB is the house default; coconut shells are not ISO codes
# noinspection PyUnresolvedReferences
class ExchangerateCog(commands.Cog):
    """
    A Discord Cog for fetching and displaying the current exchange rate between two currencies.
    """

    def __init__(self, bot: commands.Bot):
        """
        Initializes the ExchangerateCog with the given bot instance.

        Parameters:
        bot (commands.Bot): The bot instance to which this cog is added.
        """
        # Stash the bot; every cog's first ritual
        self.bot = bot

    # Command name matches the file; keep Discord's catalog boring
    @app_commands.command(
        name="exchangerate",
        description='Get the current exchange rate between two currencies',
    )
    # Defaults: tourist math, one dollar into baht
    @app_commands.describe(
        from_currency='The currency to convert from (Default: USD)',
        to_currency='The currency to convert to (Default: THB)',
        amount='The amount of money to convert (Default: 1)',
    )
    async def exchangerate_command(
        self,
        interaction: discord.Interaction,
        from_currency: str = 'USD',
        to_currency: str = 'THB',
        amount: int = 1,
    ):
        """
        A slash command to get the current exchange rate between two currencies.

        Parameters:
        interaction (discord.Interaction): The interaction object representing the command invocation.
        from_currency (str): The currency to convert from. Defaults to 'USD'.
        to_currency (str): The currency to convert to. Defaults to 'THB'.
        amount (int): The amount of money to convert. Defaults to 1.
        """
        # ISO codes are uppercase; users type "usd " with a space, of course
        from_currency = from_currency.strip().upper()

        # Same treatment for the target
        to_currency = to_currency.strip().upper()

        # Three letters or it isn't a currency in this bot's universe
        if len(to_currency) != 3 or len(from_currency) != 3:
            # Don't even call the API for "DOLLAR" or "฿"
            await interaction.response.send_message(
                f"{ERROR_MESSAGE} Those are not currencies. USD, THB, EUR — three letters, like a proper offering. Coconut shells are not ISO codes."
            )

            # Early exit before we burn quota
            return

        # Key in the query string; that's how this vendor rolls
        api_url = f'https://api.currencyapi.com/v3/latest?apikey={CURRENCYAPI_API_KEY}&currencies={to_currency}&base_currency={from_currency}'

        # Cache per pair, not per amount — amount is just multiplication
        cache_key = f"exchange:{from_currency}:{to_currency}"

        # Mods can force a live fetch if CACHE_BYPASS_PRIVILEGED is on
        user_is_privileged = (
            CACHE_BYPASS_PRIVILEGED
            and interaction.guild is not None
            and (
                interaction.user.id == interaction.guild.owner_id
                or interaction.user.guild_permissions.administrator
                or interaction.user.guild_permissions.manage_guild
            )
        )

        # Cache, HTTP, math, send — one try so errors share a punchline
        try:
            # Privileged users skip the fridge; everyone else gets leftovers
            cached_data = None if user_is_privileged else await DatabaseManager.async_get_cache_entry(cache_key)

            # Hit: parse JSON we stored ourselves
            if cached_data:
                # Trust our cache format; if it's garbage, the outer except catches it
                data = json.loads(cached_data)

            # Miss: talk to currencyapi
            else:
                # One session, one GET, then close
                async with aiohttp.ClientSession() as session:
                    # Follow the URL we built above
                    async with session.get(api_url) as response:
                        # Non-2xx: vendor said no
                        if response.status != 200:
                            # Maybe the pair doesn't exist; coconut money definitely doesn't
                            output = f"{ERROR_MESSAGE} Couldn't convert **{from_currency}** into **{to_currency}**. Are you sure they even exist? Coconut money doesn't count."

                            # Reply immediately; no cache write
                            await interaction.response.send_message(output)

                            # Don't fall through into json()
                            return

                        # Happy HTTP: parse the body
                        else:
                            # Vendor JSON: meta + data[code].value
                            data = await response.json()

                # Ten minutes is plenty for FX chatter
                await DatabaseManager.async_set_cache_entry(cache_key, json.dumps(data), 600)

            # Pair might 200 and still omit the target (vendor quirks)
            if to_currency not in data.get('data', {}):
                # Spell-check the ISO code, not our cache key
                output = f"{ERROR_MESSAGE} Invalid target currency **{to_currency}**. Please check the currency code and try again."

            # We have a rate; format it for humans
            else:
                # Vendor timestamp → "5 minutes ago"
                updated_humanized = naturaltime(
                    datetime.strptime(
                        data['meta']['last_updated_at'],
                        '%Y-%m-%dT%H:%M:%SZ',
                    )
                )

                # Multiply then round; this is chat, not a Bloomberg terminal
                value = round(
                    data['data'][to_currency]['value'] * amount, 2
                )

                # The money line
                output = f"💰 `{amount}` **{from_currency}** is currently `{value}` **{to_currency}** (Updated: {updated_humanized})"

            # One send for both success and "invalid target"
            await interaction.response.send_message(output)

        # Network, JSON, cache, permissions — all become a shrug
        except Exception as e:
            # Log the pair so we can replay the request
            logger.error(
                f"Exchange-rate lookup failed for {from_currency}->{to_currency}: {e}",
                exc_info=True,
            )

            # User-facing: coins remain unconverted
            output = (
                f"{ERROR_MESSAGE} The money-changers of Kabakon shrugged. "
                "Your coins remain unconverted, pilgrim."
            )

            # Still try to answer; if this fails too, discord.py will log it
            await interaction.response.send_message(output)


# Load the cog
async def setup(bot: commands.Bot):
    """
    A setup function to add the ExchangerateCog to the bot.

    Parameters:
    bot (commands.Bot): The bot instance to which this cog is added.
    """
    # Standard add_cog dance
    await bot.add_cog(ExchangerateCog(bot))
