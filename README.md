# 🥥 cocobot

![GitLab Release](https://img.shields.io/gitlab/v/release/thaikolja%2Fdiscord-cocobot?style=flat&label=version&color=%23d87630&link=https%3A%2F%2Fgitlab.com%2Fthaikolja%2Fdiscord-cocobot) [![pipeline status](https://gitlab.com/thailand-discord/bots/cocobot/badges/main/pipeline.svg)](https://gitlab.com/thailand-discord/bots/cocobot/-/commits/main) ![GitLab License](https://img.shields.io/gitlab/license/thailand-discord%2Fbots%2Fcocobot?style=flat) [![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)

**@cocobot** is your friendly, feature-rich **Discord bot** designed for the [**Discord Thailand** server](https://discord.gg/6JXCqVdmTZ), bringing a tropical twist to your server with useful utilities and fun interactions. Built with **Python** and the `discord.py` library, cocobot offers **a variety of commands** for practical tasks like weather checking, translation, and currency conversion, all wrapped in a coconut-themed package.

![GitHub Repository Banner](https://p.ipic.vip/srmtct.jpg)

[TOC]

---

## 🌴 Features

**cocobot** comes packed with useful commands. Parameters displayed in `<...>` are mandatory, whereas `[...]` are optional parameters that default to a specific value.

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

**Returns:** "💰`50` **USD** are currently `1685.96` **THB** (Updated: a day ago)"

### Check the air quality in Chiang Mai

```bash
/pollution city: Chiang Mai
```

**Returns:** "🟠 PM2.5 level in **Chiang Mai** is at `136` **AQI**. Not great, not terrible. Stay in, unless you fancy a diet of delusions. Wear a mask. (Last checked: 7 hours ago)"

### Translate text

```bash
/translate text: "Where is the bathroom?" from_language: English to_language: Thai
```

**Returns:** "🇹🇭 ห้องน้ำอยู่ที่ไหน"[^4]

### Transliterate Thai text into the Latin alphabet

```bash
/transliterate text: "ห้องน้ำอยู่ที่ไหน"
```

**Returns:** "🇺🇸 hâwng-nám yùu-tìi-nǎi"[^4]

---

## 🛠️ Installation

### Prerequisites
- A server with root access (Debian/Ubuntu recommended)
- Git, Python 3.8+, and pip installed

### As Service

1. **Clone the repository:**
   ```bash
   git clone https://gitlab.com/thailand-discord/bots/cocobot.git
   cd cocobot
   ```

2. **Install dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your API keys (see `.env.example` for required values)

4. **Run as a service:**
   - Create service file: `sudo nano /etc/systemd/system/cocobot.service`
   - Copy and paste the [service configuration](https://gitlab.com/-/snippets/4800805)
   - Start the service:
     ```bash
     sudo systemctl daemon-reload
     sudo systemctl enable cocobot.service
     sudo systemctl start cocobot.service
     ```

5. **Invite bot to server:**
   - Create bot at [Discord Developer Portal](https://discord.com/developers/applications)
   - Enable `Message Content Intent` in Privileged Gateway Intents
   - Use OAuth2 URL with `bot` scope and required permissions
   - Add bot to your server

Your bot should now be online with the `/coco` command available.

---

## ⚙️ Configuration

**cocobot** is highly configurable through the `config/config.py` file and environment variables. Key configuration options include:

### Required Environment Variables
- `DISCORD_BOT_TOKEN`: Discord bot token from Developer Portal
- `DISCORD_BOT_ID`: Bot application ID
- `DISCORD_SERVER_ID`: Default server ID
- At least one LLM provider API key:
  - `GOOGLE_API_KEY`: Google Gemini API key
  - `DEEPSEEK_API_KEY`: DeepSeek API key
  - `GROQ_API_KEY`: Groq API key

### LLM Provider Configuration

**Summarization** (`/summarize` command):
- `SUMMARY_PROVIDER`: LLM provider (google, groq, deepseek)
- `SUMMARY_MODEL`: Model name (e.g., `gemini-2.5-flash`, `llama-3.3-70b-versatile`, `deepseek-chat`)

### Optional Configuration
- **Database**: `DATABASE_URL`, `DB_POOL_SIZE`, `DB_ECHO`, `INIT_DB_ON_STARTUP`
- **Cache**: `CACHE_ENABLED`, `REDIS_URL`, `CACHE_TTL`
- **Logging**: `LOG_LEVEL`, `LOG_FILE`, `LOG_MAX_BYTES`, `LOG_BACKUP_COUNT`
- **Security**: `MAX_CONTENT_LENGTH`, `ALLOWED_MENTIONS`, `ENABLE_CORS`
- **Environment**: `ENVIRONMENT` (development/production), `DEBUG`
- **Jail System**: `JAIL_ROLE_ID`, `AUGUST_INTERNAL_PORT`, `AUGUST_INTERNAL_SECRET`

### API Response Caching

As of `v3.4.0`, all external API responses (`/weather`, `/time`, `/exchangerate`, `/pollution`) are cached in the local database for **10 minutes** to reduce latency and API usage.

The `CACHE_BYPASS_PRIVILEGED` constant in `config/config.py` controls whether privileged users skip the cache:

```python
# config/config.py

# When True, guild owners, administrators, and users with Manage Server permission
# always receive a fresh API response, bypassing the 10-minute cache.
CACHE_BYPASS_PRIVILEGED: bool = True
```

Set it to `False` to apply the cache equally to all users.

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

1. [Fork the repository](https://gitlab.com/thailand-discord/bots/cocobot/-/forks/new)
2. Create a new branch for your feature/fix
3. Commit your changes with a meaningful commit message
4. Submit a pull request

**Please ensure your code follows the existing style and includes appropriate documentation.**

---

##  📜 License

**cocobot** is licensed under the MIT License. See the [LICENSE](https://opensource.org/licenses/MIT) file for details.

---

## 🙏 Acknowledgements

**cocobot** was created by Kolja Nolte and is maintained by the Thailand Discord community. Special thanks to:

- The `discord.py` team for their excellent library
- All API and AI providers for their services
- [August Engelhardt](https://en.wikipedia.org/wiki/August_Engelhardt) for inspiration

---

[^1]: Using `.` works only if the current directory is completely empty. If not, leave don't use it and use `mv ./discord-bot/{*,.*} ../`
[^2]: Keep your `.env` file secret and remember to add it to the `.gitignore` file.

[^3]: Uses Google's Gemini 2.5 Flash and can produce inaccuracies.
[^4]: Since `v2.2.0`, this has been handled by *Gemini 2.5 Flash Lite.* An API key is required, but usage of up to a million tokens is free.
