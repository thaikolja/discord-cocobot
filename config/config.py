import os
from dotenv import load_dotenv

load_dotenv()

ERROR_MESSAGE: str = f"🥥 Oops, something's cracked, and it's **not** the coconut!"

DISCORD_BOT_TOKEN: str = os.getenv('DISCORD_BOT_TOKEN')

DISCORD_SERVER_ID: str = os.getenv('DISCORD_SERVER_ID')

DISCORD_BOT_ID: str = os.getenv('DISCORD_BOT_ID')

WEATHERAPI_API_KEY: str = os.getenv('WEATHERAPI_API_KEY')

LOCALTIME_API_KEY: str = os.getenv('LOCALTIME_API_KEY')

CURRENCYAPI_API_KEY: str = os.getenv('CURRENCYAPI_API_KEY')

GROQ_API_KEY: str = os.getenv('GROQ_API_KEY')

OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY')

GOOGLE_API_KEY: str = os.getenv('GOOGLE_API_KEY')

GEOAPFIY_API_KEY: str = os.getenv('GEOAPFIY_API_KEY')
