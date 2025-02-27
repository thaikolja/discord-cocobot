# Configuration file for managing environment variables and application constants
# This file contains all the necessary configurations and API keys for the application

# Import the os module to interact with operating system-dependent functionality
import os

# Import the load_dotenv function from the dotenv module to load environment variables from .env files
from dotenv import load_dotenv

# Load environment variables from the .env file into the application
load_dotenv()

# Define a friendly error message to display when something goes wrong
# This message will be shown to users when an error occurs
ERROR_MESSAGE: str = f"🥥 Oops, something's cracked, and it's **not** the coconut!"

# Configure Discord-related constants
# These constants are used to authenticate and connect to the Discord API

# Retrieve the Discord Bot Token from the environment variables
# This token is used to authenticate the bot with the Discord API
DISCORD_BOT_TOKEN: str = os.getenv('DISCORD_BOT_TOKEN')

# Retrieve the Discord Server ID from the environment variables
# This ID identifies the specific Discord server the bot is associated with
DISCORD_SERVER_ID: str = os.getenv('DISCORD_SERVER_ID')

# Retrieve the Discord Bot ID from the environment variables
# This ID uniquely identifies the bot within Discord
DISCORD_BOT_ID: str = os.getenv('DISCORD_BOT_ID')

# Configure API keys for various services
# These keys are used to authenticate with external APIs

# Retrieve the WeatherAPI API Key from the environment variables
# This key is used to access weather-related data from the WeatherAPI service
WEATHERAPI_API_KEY: str = os.getenv('WEATHERAPI_API_KEY')

# Retrieve the LocalTime API Key from the environment variables
# This key is used to access local time-related data from the LocalTime service
LOCALTIME_API_KEY: str = os.getenv('LOCALTIME_API_KEY')

# Retrieve the CurrencyAPI API Key from the environment variables
# This key is used to access currency conversion data from the CurrencyAPI service
CURRENCYAPI_API_KEY: str = os.getenv('CURRENCYAPI_API_KEY')

# Retrieve the Groq API Key from the environment variables
# This key is used to access AI-related services from Groq
GROQ_API_KEY: str = os.getenv('GROQ_API_KEY')

# Retrieve Google API key from environment variables
GOOGLE_API_KEY: str = os.getenv('GOOGLE_API_KEY')

# Retrieve the Geoapify API Key from the environment variables
# This key is used to access geolocation-related data from Geoapify
GEOAPFIY_API_KEY: str = os.getenv('GEOAPFIY_API_KEY')

# Retrieve the Acqin API Key from the environment variables
# This key is used to access location-based services from Acqin
ACQIN_API_KEY: str = os.getenv('ACQIN_API_KEY')

# Retrieve Google Maps API key from environment variables
GOOGLE_MAPS_API_KEY: str = os.getenv('GOOGLE_MAPS_API_KEY')

# Retrieve the Sambanova API Key from the environment variables
# This key is used to access AI-related services from Sambanova
SAMBANOVA_API_KEY: str = os.getenv('SAMBANOVA_API_KEY')
