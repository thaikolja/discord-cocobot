# cocobot for Discord

A bot for the Discord Thailand-related server **Thailand — Official English-speaking community without trolls or spammers.** Features are added as needed. [Join us](https://discord.gg/DN52SxBpYJ)!

## Installation

1. `git clone https://gitlab.com/thaikolja/discord-cocobot.git`

2. `cd discord-cocobot`

3. Create a virtual environment via `python3 -m venv venv` (optional)

4. Install required modules via `pip install -r requirements.txt`

5. `touch .env && open .env`

6. Enter your private `BOT_TOKEN="..."`

7. Scroll to line `54` and enter your server ID as in this example:

   `````python
   guild = discord.Object(id=1148760268353061077)

8. Run the bot locally or on your server (recommended) via `python3 bot.py`

## Usage

Please refer to [Discord's official documentation](https://discord.com/developers/docs/intro) on how to add a bot to your Discord server.

## Features

* `/translate <text> <language_code>`: Translate text to another language.
    * `<text>`: The text to translate.
    * `<language_code>`: The language code of the language to translate to, i.e., `de` for German or `es` for Spanish.

## Author

* **Kolja Nolte** / [thaikolja](https://gitlab.com/thaikolja/) \<kolja.nolte@gmail.com\>
