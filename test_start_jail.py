import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

async def ping():
    secret = os.getenv("AUGUST_INTERNAL_SECRET", "")
    url = "http://127.0.0.1:17432/start-jail"
    headers = {
        "Content-Type": "application/json",
        "X-Internal-Token": secret
    }
    payload = {
        "user_id": "123456789",
        "username": "CLI Tester"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                print(f"Status: {resp.status}")
                print(await resp.text())
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(ping())
