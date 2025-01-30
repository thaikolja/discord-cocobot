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

# Import the os module for interacting with environment variables
import os

# Import the load_dotenv function from the dotenv module
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Define the error message format using an emoji and bold text
ERROR_MESSAGE: str = f"🥥 Oops, something's cracked, and it's **not** the coconut!"

# Retrieve Discord bot token from environment variables
DISCORD_BOT_TOKEN: str = os.getenv('DISCORD_BOT_TOKEN')

# Retrieve Discord server ID from environment variables
DISCORD_SERVER_ID: str = os.getenv('DISCORD_SERVER_ID')

# Retrieve Discord bot ID from environment variables
DISCORD_BOT_ID: str = os.getenv('DISCORD_BOT_ID')

# Retrieve WeatherAPI API key from environment variables
WEATHERAPI_API_KEY: str = os.getenv('WEATHERAPI_API_KEY')

# Retrieve LocalTime API key from environment variables
LOCALTIME_API_KEY: str = os.getenv('LOCALTIME_API_KEY')

# Retrieve CurrencyAPI API key from environment variables
CURRENCYAPI_API_KEY: str = os.getenv('CURRENCYAPI_API_KEY')

# Retrieve Groq API key from environment variables
GROQ_API_KEY: str = os.getenv('GROQ_API_KEY')

# Retrieve OpenAI API key from environment variables
OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY')

# Retrieve Google API key from environment variables
GOOGLE_API_KEY: str = os.getenv('GOOGLE_API_KEY')

# Retrieve Geoapify API key from environment variables
GEOAPFIY_API_KEY: str = os.getenv('GEOAPFIY_API_KEY')

# Retrieve Acqin API key from environment variables
ACQIN_API_KEY: str = os.getenv('ACQIN_API_KEY')

# Retrieve Google Maps API key from environment variables
GOOGLE_MAPS_API_KEY: str = os.getenv('GOOGLE_MAPS_API_KEY')
