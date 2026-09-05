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
Configuration file for managing environment variables and application constants.

This module centralizes the retrieval of sensitive keys and configuration parameters
from the environment, making them readily available as constants throughout the application.
It leverages the `dotenv` library to load these values from a `.env` file,
promoting a clean separation of configuration from code.
"""

# Pull the Discord token through the fancy config layer, not os.getenv in a trenchcoat
from config.app_config import get_discord_token as _get_discord_token

# One object to rule all the other knobs
from config.app_config import get_global_config

# Version string so we can tell which coconut is currently rotting in prod
COCOBOT_VERSION: str = get_global_config().version

# The token Discord wants before it even pretends to listen
DISCORD_BOT_TOKEN: str = _get_discord_token()

# Which guild this bot is supposed to haunt
DISCORD_SERVER_ID: str = get_global_config().discord.server_id

# Application ID, because Discord collects IDs like Pokémon
DISCORD_BOT_ID: str = get_global_config().discord.bot_id

# WeatherAPI key — rain reports, not astrology
WEATHERAPI_API_KEY: str = get_global_config().api.weatherapi_key

# LocalTime key so /time doesn't guess from a wall clock in Berlin
LOCALTIME_API_KEY: str = get_global_config().api.localtime_key

# CurrencyAPI key for converting "how much is this beer in EUR"
CURRENCYAPI_API_KEY: str = get_global_config().api.currencyapi_key

# Groq key for the fast-talking LLM
GROQ_API_KEY: str = get_global_config().api.groq_api_key

# Which Groq model we currently trust not to invent Thai grammar
GROQ_MODEL: str = get_global_config().api.groq_model

# Gemini key for the Google-flavored brain
GEMINI_API_KEY: str = get_global_config().api.gemini_api_key

# Gemini model name, in case last week's model became sentient and left
GEMINI_MODEL: str = get_global_config().api.gemini_model

# AcqIn key — another vendor, another secret
ACQIN_API_KEY: str = get_global_config().api.acqin_api_key

# DeepSeek key for when we want a different flavor of hallucination
DEEPSEEK_API_KEY: str = get_global_config().api.deepseek_api_key

# DeepSeek model identifier
DEEPSEEK_MODEL: str = get_global_config().api.deepseek_model

# User-facing oops line; keep it coconut-themed or the brand police will notice
ERROR_MESSAGE: str = "🥥 Oops, something's cracked, and it's **not** the coconut!"

# Admins skip the 10-minute cache so they can debug without waiting like peasants
CACHE_BYPASS_PRIVILEGED: bool = True
