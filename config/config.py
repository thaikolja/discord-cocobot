#  Copyright (C) 2025 by Kolja Nolte
#  kolja.nolte@gmail.com
#  https://gitlab.com/thaikolja/discord-cocobot
#
#  This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
#  You are free to use, share, and adapt this work for non-commercial purposes, provided that you:
#  - Give appropriate credit to the original author.
#  - Provide a link to the license.
#  - Distribute your contributions under the same license.
#
#  For more information, visit: https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#  Author:    Kolja Nolte
#  Email:     kolja.nolte@gmail.com
#  License:   CC BY-NC-SA 4.0
#  Date:      2014-2025
#  Package:   Thailand Discord

"""
Configuration file for managing environment variables and application constants.

This module centralizes the retrieval of sensitive keys and configuration parameters
from the environment, making them readily available as constants throughout the application.
It leverages the `dotenv` library to load these values from a `.env` file,
promoting a clean separation of configuration from code.
"""

import os
# Imports the standard 'os' module, providing functions for interacting with the operating system,
# particularly for accessing environment variables.

from dotenv import load_dotenv

# Imports the 'load_dotenv' function specifically from the 'dotenv' library,
# which is used to parse `.env` files and load their key-value pairs into environment variables.


# Executes the function to load variables from a `.env` file located in the project's root
# or parent directories into the system's environment variables.
load_dotenv()

# Defines a user-facing error message string, potentially used in exception handling
# or user feedback when an operation fails within the application.
ERROR_MESSAGE: str = f"🥥 Oops, something's cracked, and it's **not** the coconut!"

# Retrieves the authentication token for the Discord bot account from environment variables.
# This token is essential for the bot to connect to and interact with the Discord API.
DISCORD_BOT_TOKEN: str = os.getenv('DISCORD_BOT_TOKEN')

# Fetches the unique identifier for the target Discord server (guild) from environment variables.
# This ID specifies which server the bot's operations are primarily associated with.
DISCORD_SERVER_ID: str = os.getenv('DISCORD_SERVER_ID')

# Obtains the unique application ID assigned to the Discord bot from environment variables.
# Used for various API interactions and identifying the bot application itself.
DISCORD_BOT_ID: str = os.getenv('DISCORD_BOT_ID')

# Retrieves the API key required for accessing the WeatherAPI service.
# This key authenticates requests for fetching current weather conditions and forecasts.
WEATHERAPI_API_KEY: str = os.getenv('WEATHERAPI_API_KEY')

# Fetches the API key for the LocalTime service (assuming a service providing time zone or local time data).
# This key is necessary for making authenticated requests to retrieve time-related information.
LOCALTIME_API_KEY: str = os.getenv('LOCALTIME_API_KEY')

# Obtains the API key for the CurrencyAPI service, used for currency conversion functionalities.
# This key authorizes requests to fetch real-time or historical exchange rates.
CURRENCYAPI_API_KEY: str = os.getenv('CURRENCYAPI_API_KEY')

# Retrieves the API key for accessing Groq's AI services (e.g., language models).
# This key is required to authenticate requests made to the Groq API endpoints.
GROQ_API_KEY: str = os.getenv('GROQ_API_KEY')

# Fetches a general Google API key from environment variables.
# This key might be used for various Google Cloud Platform services or other Google APIs.
GOOGLE_API_KEY: str = os.getenv('GOOGLE_API_KEY')

# Obtains the API key for the Geoapify service, specializing in geolocation and map-related data.
# This key authenticates requests for services like geocoding, routing, or map tiles.
GEOAPFIY_API_KEY: str = os.getenv('GEOAPFIY_API_KEY')

# Retrieves the API key for the AcqIn service (purpose assumed, e.g., location intelligence or data acquisition).
# This key is needed to authenticate requests to the AcqIn platform's API.
ACQIN_API_KEY: str = os.getenv('ACQIN_API_KEY')

# Fetches the specific API key for Google Maps Platform services.
# This key authorizes usage of APIs like Maps JavaScript API, Geocoding API, Places API, etc.
GOOGLE_MAPS_API_KEY: str = os.getenv('GOOGLE_MAPS_API_KEY')

# Obtains the API key for accessing Sambanova's AI platform or services.
# This key is required for authenticating interactions with Sambanova's AI models or infrastructure.
SAMBANOVA_API_KEY: str = os.getenv('SAMBANOVA_API_KEY')
