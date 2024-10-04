# cocobot for Discord

A bot for the Discord Thailand-related server **Thailand — Official English-speaking community without trolls or spammers.** Features are added as needed. [Join us](https://discord.gg/DN52SxBpYJ)!

## Installation

1. `git clone https://gitlab.com/thaikolja/discord-cocobot.git`

2. `cd discord-cocobot`

3. `touch .env && open .env`

4. Enter your private `BOT_TOKEN="..."`

5. Scroll to line `54` and enter your server ID as in this example:

   `````python
   guild = discord.Object(id=1148760268353061077)

6. Run the bot locally or on your server (recommended) via `python3 bot.py`

## Features

* `/translate <text> <language_code>`: Translate text to another language.
    * `<text>`: The text to translate.
    * `<language_code>`: The language code of the language to translate to, i.e., `de` for German or `es` for Spanish.

## Author

* **Kolja Nolte** / [thaikolja](https://gitlab.com/thaikolja/) \<kolja.nolte@gmail.com\>
