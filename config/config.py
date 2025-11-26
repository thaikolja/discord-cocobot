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
from .app_config import (
	get_discord_token as _get_discord_token,
	get_global_config,
	ERROR_MESSAGE
)

# Version of the cocobot application, used for tracking and updates.
# This is now managed by the new configuration system
COCOBOT_VERSION: str = get_global_config().version

# Retrieves the authentication token for the Discord bot account from environment variables.
# This token is essential for the bot to connect to and interact with the Discord API.
DISCORD_BOT_TOKEN: str = _get_discord_token()

# Fetches the unique identifier for the target Discord server (guild) from environment variables.
# This ID specifies which server the bot's operations are primarily associated with.
DISCORD_SERVER_ID: str = get_global_config().discord.server_id

# Obtains the unique application ID assigned to the Discord bot from environment variables.
# Used for various API interactions and identifying the bot application itself.
DISCORD_BOT_ID: str = get_global_config().discord.bot_id

# Retrieves the API key required for accessing the WeatherAPI service.
# This key authenticates requests for fetching current weather conditions and forecasts.
WEATHERAPI_API_KEY: str = get_global_config().api.weatherapi_key

# Fetches the API key for the LocalTime service (assuming a service providing time zone or local time data).
# This key is necessary for making authenticated requests to retrieve time-related information.
LOCALTIME_API_KEY: str = get_global_config().api.localtime_key

# Obtains the API key for the CurrencyAPI service, used for currency conversion functionalities.
# This key authorizes requests to fetch real-time or historical exchange rates.
CURRENCYAPI_API_KEY: str = get_global_config().api.currencyapi_key

# Retrieves the API key for accessing Groq's AI services (e.g., language models).
# This key is required to authenticate requests made to the Groq API endpoints.
GROQ_API_KEY: str = get_global_config().api.groq_api_key

# Fetches a general Google API key from environment variables.
# This key might be used for various Google Cloud Platform services or other Google APIs.
GOOGLE_API_KEY: str = get_global_config().api.google_api_key

# Obtains the API key for the Geoapify service, specializing in geolocation and map-related data.
# This key authenticates requests for services like geocoding, routing, or map tiles.
GEOAPFIY_API_KEY: str = get_global_config().api.geoapify_api_key

# Retrieves the API key for the AcqIn service (purpose assumed, e.g., location intelligence or data acquisition).
# This key is needed to authenticate requests to the AcqIn platform's API.
ACQIN_API_KEY: str = get_global_config().api.acqin_api_key

# Fetches the specific API key for Google Maps Platform services.
# This key authorizes usage of APIs like Maps JavaScript API, Geocoding API, Places API, etc.
GOOGLE_MAPS_API_KEY: str = get_global_config().api.google_maps_api_key

# Obtains the API key for accessing Sambanova's AI platform or services.
# This key is required for authenticating interactions with Sambanova's AI models or infrastructure.
SAMBANOVA_API_KEY: str = get_global_config().api.sambanova_api_key
