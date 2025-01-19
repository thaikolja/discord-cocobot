import os
from dotenv import load_dotenv

load_dotenv()

ERROR_MESSAGE = f"🥥 Oops, something's cracked, and it's **not** the coconut!"

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

DISCORD_SERVER_ID = os.getenv('DISCORD_SERVER_ID')

DISCORD_BOT_ID = os.getenv('DISCORD_BOT_ID')

WEATHERAPI_API_KEY = os.getenv('WEATHERAPI_API_KEY')
