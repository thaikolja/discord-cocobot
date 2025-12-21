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

"""
Configuration file for managing environment variables and application constants.

This module centralizes the retrieval of sensitive keys and configuration parameters
from the environment, making them readily available as constants throughout the application.
It leverages the `dotenv` library to load these values from a `.env` file,
promoting a clean separation of configuration from code.
"""

# Import the new advanced configuration system
from config.app_config import get_discord_token as _get_discord_token
from config.app_config import get_global_config

# Version of the cocobot application, used for tracking and updates
COCOBOT_VERSION: str = get_global_config().version

# Discord bot authentication token
DISCORD_BOT_TOKEN: str = _get_discord_token()

# Target Discord server (guild) ID
DISCORD_SERVER_ID: str = get_global_config().discord.server_id

# Discord bot application ID
DISCORD_BOT_ID: str = get_global_config().discord.bot_id

# WeatherAPI service API key
WEATHERAPI_API_KEY: str = get_global_config().api.weatherapi_key

# LocalTime service API key
LOCALTIME_API_KEY: str = get_global_config().api.localtime_key

# CurrencyAPI service API key
CURRENCYAPI_API_KEY: str = get_global_config().api.currencyapi_key

# Groq AI services API key
GROQ_API_KEY: str = get_global_config().api.groq_api_key

# General Google API key
GOOGLE_API_KEY: str = get_global_config().api.google_api_key

# AcqIn service API key
ACQIN_API_KEY: str = get_global_config().api.acqin_api_key

# Standard error message to display to users when something goes wrong
ERROR_MESSAGE: str = "🥥 Oops, something's cracked, and it's **not** the coconut!"
