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

# AcqIn service API key
ACQIN_API_KEY: str = get_global_config().api.acqin_api_key

# ---- Transliterate - primary ----
TRANSLITERATE_PROVIDER: str = get_global_config().api.transliterate_provider
TRANSLITERATE_PROVIDER_API_KEY: str = get_global_config().api.transliterate_provider_api_key
TRANSLITERATE_PROVIDER_MODEL: str = get_global_config().api.transliterate_provider_model

# ---- Transliterate - fallback ----
TRANSLITERATE_FALLBACK_PROVIDER: str = get_global_config().api.transliterate_fallback_provider
TRANSLITERATE_FALLBACK_PROVIDER_API_KEY: str = get_global_config().api.transliterate_fallback_provider_api_key
TRANSLITERATE_FALLBACK_PROVIDER_MODEL: str = get_global_config().api.transliterate_fallback_provider_model

# ---- Translate - primary ----
TRANSLATE_PROVIDER: str = get_global_config().api.translate_provider
TRANSLATE_PROVIDER_API_KEY: str = get_global_config().api.translate_provider_api_key
TRANSLATE_PROVIDER_MODEL: str = get_global_config().api.translate_provider_model

# ---- Translate - fallback ----
TRANSLATE_FALLBACK_PROVIDER: str = get_global_config().api.translate_fallback_provider
TRANSLATE_FALLBACK_PROVIDER_API_KEY: str = get_global_config().api.translate_fallback_provider_api_key
TRANSLATE_FALLBACK_PROVIDER_MODEL: str = get_global_config().api.translate_fallback_provider_model

# ---- Summarize - primary ----
SUMMARIZE_PROVIDER: str = get_global_config().api.summarize_provider
SUMMARIZE_PROVIDER_API_KEY: str = get_global_config().api.summarize_provider_api_key
SUMMARIZE_PROVIDER_MODEL: str = get_global_config().api.summarize_provider_model

# ---- Summarize - fallback ----
SUMMARIZE_FALLBACK_PROVIDER: str = get_global_config().api.summarize_fallback_provider
SUMMARIZE_FALLBACK_PROVIDER_API_KEY: str = get_global_config().api.summarize_fallback_provider_api_key
SUMMARIZE_FALLBACK_PROVIDER_MODEL: str = get_global_config().api.summarize_fallback_provider_model

# Standard error message to display to users when something goes wrong
ERROR_MESSAGE: str = "🥥 Oops, something's cracked, and it's **not** the coconut!"

# When True, server owners, administrators, and moderators (manage_guild permission)
# will always receive a fresh API response, bypassing the 10-minute cache.
# Set to False to cache responses for all users equally.
CACHE_BYPASS_PRIVILEGED: bool = True
