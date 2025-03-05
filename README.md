# 🥥 cocobot

[![pipeline status](https://gitlab.com/thaikolja/discord-cocobot/badges/main/pipeline.svg)](https://gitlab.com/thaikolja/discord-cocobot/-/commits/main) [![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-blue.svg)](LICENSE) [![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)

**@cocobot** is a feature-rich, customized **Discord bot** for the [**Discord Thailand** server](https://discord.gg/6JXCqVdmTZ) designed to provide useful utilities and fun interactions with a tropical twist. Built with **Python** and the `discord.py` library, cocobot offers **a variety of commands** for practical tasks like weather checking, translation, and currency conversion, all wrapped in a coconut-themed package.

![GitHub Repository Banner](https://p.ipic.vip/srmtct.jpg)

[TOC]

---

## 🌴 Features

**cocobot** comes packed with useful commands. Parameters displayed in `<...>` are mandatory whereas `[...]` are optional parameters that default to a specific value.

- **🌤️ Weather**: Get current weather conditions for any location
  - `/weather [location]` *(string)* **Default:** Bangkok

- **🕓 Time**: Check the local time in any city or country
  - `/time [location]` *(string)* **Default:** Thailand

- **💱 Exchange Rates**: Convert between currencies with up-to-date rates
  - `/exchangerates`
    - `[from_currency]` *(string)* **Default:** `USD`
    - `[to_currency]` *(string)* **Default:** `THB`
    - `[amount]` *(number)* **Default:** `1`

- **📍 Location**: Find addresses and get a Google Maps link
  - `/locate`
    - `<location>` *(string)* **Required**
    - `[city]` *(string)* **Default:** Bangkok

- **🌫️ Pollution**: Check air quality index (AQI) for any city
  - `/pollution <city>` *(string)*

- **🔤 Transliteration**: Convert Thai text to Latin script[^3]
  - `/transliterate <text>` *(string)* Change Thai script into the Latin alphabet

- 💡 **Learn:** Shows one of the 250 core Thai words and its translation and transliteration
  - `/learn`
  
- **🌐 Translation**: Translate text between languages using AI[^3]
  - `/translate`
    - `<text>` *(string)* The text to be translated
    - `[from_language]` *(string)* **Default:** Thai
    - `[to_language]` *(string)* **Default:** English

## 🥥 Examples

**cocobot** uses [slash commands](https://support-apps.discord.com/hc/en-us/articles/26501837786775-Slash-Commands-FAQ). Here are some examples. The parameter with the colon (`:`) at the end are the parameters you can choose as described in the **Features** section.

### Get the current weather in Bangkok

```bash
/weather location: Bangkok
```

**Returns:** "🌤️ The weather in **Bangkok**, **Thailand** is currently clear with temperatures of `23.4°C` (feels like `25.2°C`). **Humidity** is at `69%`."

### Convert `50` USD to THB

```bash
/exchangerate from_currency: USD to_currency: THB amount: 50
```

**Returns:** "💰`50` **USD** is currently `1685.96` **THB** (Updated: a day ago)"

### Check air quality in Chiang Mai

```bash
/pollution city: Chiang Mai
```

**Returns:** "🟠 PM2.5 level in **Chiang Mai** is at `136` **AQI**. Not great, not terrible. Stay in, unless you fancy a diet of delusions. Wear a mask. (Last checked: 7 hours ago)"

### Translate text

```bash
/translate text: "Where is the bathroom?" from_language: English to_language: Thai
```

**Returns:** "🇹🇭 ห้องน้ำอยู่ที่ไหน"

### Transliterate the translated text into the Latin alphabet

```bash
/transliterate text: "ห้องน้ำอยู่ที่ไหน"
```

**Returns:** "🇺🇸 hông-náam yùu thîi-năi"

---

## 🛠️ Installation

In order to keep cocobot running on your Discord server, a web server with root access and feel comfortable with Bash commands **is required**. These steps assume that you're running Debian or Ubuntu and have experience in using SSH.

1. Log in into your server's command line interface as user with root privileges.
   1. If you don't have it yet, install Git via `sudo apt-get install git`

2. For security reasons, you'd want to create a new user who belongs to a group that only has permissions to run the bot (note that both, the user and the group have the same name):
   1. Create group: `sudo groupapp discord-bot`

   2. Create user: `sudo useradd -m -g discord-bot discord-bot`

3. Change (`cd`) into the newly created home directory, which would be `/home/discord-bot` and use `git clone https://gitlab.com/thaikolja/discord-cocobot.git .` to download the source code into your bot directory[^1].
4. Change the permissions of the entire folder and files to match your user and group name: `sudo chown -R discord-bot:discord-bot .` (Don't leave the `.` away)
5. Install all packages needed for installing the Discord bot: `sudo apt-get update && sudo apt-get install python3 python3-pip`
6. To not depend on the OS' Python version, you need to create a virtual environment. In the root folder of your bot, run `python -m venv venv` to create one. Use `source venv/bin/activate` to switch into the environment.
7. Install all dependencies via `pip install -r requirements.txt`.
8. Copy the invisible file `.env.example` and rename it to `.env` via `cp .env.example .env`. Fill out the API keys and tokens[^2] which you can find via a simple Google search:
   1. `DISCORD_BOT_TOKEN`=your_discord_bot_token

   2. `WEATHERAPI_API_KEY`=your_weatherapi_key

   3. `LOCALTIME_API_KEY`=your_localtime_key

   4. … and more

9. To turn the bot into a background service on your server so it can stay online 24/7, create a service file: `sudo nano /etc/systemd/system/discord-bot.service`
10. Inside this file, [paste this code](https://gitlab.com/-/snippets/4800805) and save the file.
11. Enable and start the bot as a service with these commands:
    1. `sudo systemctl daemon-reload`
    2. `sudo systemctl enable discord-bot.service`
    3. `sudo systemctl start discord-bot.service`

12. (Optional) Check the status of your bot via `sudo systemctl status discord-bot.service`.
13. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
14. Select your application (or create a new one if you haven't done so yet) and navigate to the "Bot" tab.
15. Under "Privileged Gateway Intents," enable the necessary permissions for your bot, especially enabling the option `Message Content Intent`.
16. Under "OAuth2," enable the checkbox "bot" and choose the appropriate permissions your bot needs (i.e., `application.commands`,  `messages.read`)
17. Copy the generated URL and open it in your browser to invite the bot to your server.
18. A bot named `@cocobot` should now have entered your server, and you can use `/coco` (without pressing enter) to see all commands the bot has to offer.

---

## ⚙️ Configuration

**cocobot** is highly configurable through the `config/config.py` file and environment variables. Key configuration options include:

- API keys for various services
- Default locations and currencies
- Error messages and bot behavior

---

## 🧪 Testing

**cocobot** includes unit tests in the `tests/` directory. To run tests:

```bash
pytest tests/
```

We recommend adding tests for any new features or bug fixes.

---

## 🧑‍💻 Authors and Contributors

* **Kolja Nolte** (kolja.nolte@gmail.com)

---

## 🤝 Contribute to cocobot

We welcome contributions via Git! Please follow these standard steps:

1. [Fork the repository](https://gitlab.com/thaikolja/discord-cocobot/-/forks/new)
2. Create a new branch for your feature/fix
3. Commit your changes with a meaningful commit message
4. Submit a pull request

**Please ensure your code follows the existing style and includes appropriate documentation.**

---

##  📜 License

**cocobot** is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

**cocobot** was created by Kolja Nolte and is maintained by the Thailand Discord community. Special thanks to:

- The `discord.py` team for their excellent library
- All API and AI providers for their services
- [August Engelhardt](https://en.wikipedia.org/wiki/August_Engelhardt) for inspiration

---

[^1]: Using `.` works only if the current directory is completely empty. If not, leave don't use it and use `mv ./discord-bot/{*,.*} ../`
[^2]: Keep your `.env` file secret and remember to add it to the `.gitignore` file. 
[^3]: Uses Perplexity's AI LLM "Sonar Pro" and can produce inaccuracies.