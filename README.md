# 🥥 cocobot `v3.9.0`

![GitLab Release](https://img.shields.io/gitlab/v/release/thailand-discord%2Fbots%2Fcocobot?style=flat&label=version&color=%23d87630&link=https%3A%2F%2Fgitlab.com%2Fthailand-discord%2Fbots%2Fcocobot/-/releases) [![pipeline status](https://gitlab.com/thailand-discord/bots/cocobot/badges/main/pipeline.svg)](https://gitlab.com/thailand-discord/bots/cocobot/-/commits/main) ![GitLab License](https://img.shields.io/gitlab/license/thailand-discord%2Fbots%2Fcocobot?style=flat) [![Python Version](https://img.shields.io/badge/Python-3.13%2B-blue.svg)](https://www.python.org/downloads/)

**@cocobot** is your friendly, feature-rich **Discord bot** designed for the [**Discord Thailand Server**](https://discord.gg/6JXCqVdmTZ), bringing a tropical wind to your server with useful utilities and fun interactions. Built with **Python** and the `discord.py` library, cocobot offers **a variety of commands** for practical tasks like weather checking, translation, and currency conversion, all wrapped in a coconut-themed package.

![GitHub Repository Banner](https://p.ipic.vip/srmtct.jpg)

[TOC]

---

## 🌴 Features

**cocobot** comes packed with useful commands. Parameters displayed in `<...>` are mandatory, whereas `[...]` are optional parameters that default to a specific value.

- **🌤️ Weather**: Get current weather conditions for any location with °C/°F toggle
  - `/weather [location] [units]` *(string | choice)* **Default:** channel's city or Bangkok, metric

- **🕓 Time**: Check the local time in any city or country
  - `/time [location]` *(string)* **Default:** Bangkok

- **💱 Exchange Rates**: Convert between currencies with up-to-date rates
  - `/exchangerate`
    - `[from_currency]` *(string)* **Default:** `USD`
    - `[to_currency]` *(string)* **Default:** `THB`
    - `[amount]` *(number)* **Default:** `1`

- **🌫️ Pollution**: Check air quality index (AQI) for any city
  - `/pollution [city]` *(string)* **Default:** channel's city or Bangkok

- **🔤 Transliteration**: Convert Thai text to Latin script using AI[^3]
  - `/transliterate <text>` *(string)*

- 💡 **Learn:** Shows one of the 250 core Thai words with English translation and transliteration
  - `/learn`

- **🌐 Translation**: Translate text between languages using AI with auto-detection[^3]
  - `/translate`
    - `<text>` *(string)* The text to be translated
    - `[from_language]` *(string)* **Default:** auto (Thai/English detection)
    - `[to_language]` *(string)* **Default:** auto (opposite of source)

- **📝 Summarize**: Summarize recent messages in the current channel using AI
  - `/summarize [limit]` *(number)* **Default:** `20`, **Max:** `50`

- **⚠️ Warning System**: Three-strike moderator warnings (staff only: owner / admins / mods)
  - `/warn <user> [reason]` *(user required; ephemeral if missing)*
  - `/unwarn <user> [all]` *(user required; `all` default false; `all=true` deletes every warning row)*

- **🚪 Leave announcements**: When a member leaves, is kicked, or is banned, Cocobot posts `👋 **{name} has left the server.**` plus a random coda in the channel of their last message. Members who never spoke are recorded only in `#logs` (professional line, no emoji).
  - `/simulate-leave [user]` *(member)* Staff dry-run in the **current** channel (owner / admins / mods); nobody is removed; never posts to `#logs` or another channel

## 🥥 Examples

**cocobot** uses [slash commands](https://support-apps.discord.com/hc/en-us/articles/26501837786775-Slash-Commands-FAQ) only. Prefix text such as `!test` is ignored and gets no bot reply. Mention `@cocobot` by itself for a single info card. Examples:

### Get the current weather in Bangkok

```bash
/weather location: Bangkok units: Civilized Units (°C)
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

### Warn a member who breaks the rules

```bash
/warn user: @Username reason: "Spamming in #general"
```

**Returns (first warning):** An embed with the warning card, severity-colored (gold → orange → red). On the third warning, the member is automatically kicked. Staff only (owner / admins / mods).

### Dry-run a leave announcement

```bash
/simulate-leave user: @Username
```

**Returns:** `👋 **Username** has left the server.` plus a random Imperium-style coda, in the channel where you ran the command. Nobody is removed.

### Remove a member's warnings

```bash
/unwarn user: @Username
```

**Returns (ephemeral):** confirmation that that member's active warnings were archived. Pass `all: True` to wipe the entire warning table.

---

## 🚢 Production

Merge or push to **`main`** on GitLab. Pipeline:

1. **test** — Python 3.13, `TESTING=1 pytest tests/`
2. **deploy** (main only) — SSH to `/opt/discord/cocobot`, `git reset --hard origin/main` (keeps `.env`), then run `REMOTE_SCRIPT_PATH` (typically `/opt/discord/cocobot/deploy.sh`)

`deploy.sh` → `scripts/deploy-as-docker.sh`: `git pull --ff-only origin main`, rebuild Compose (bot `python:3.13-slim` as `appuser`, Postgres 15, Redis 7, healthchecks). Privileged Discord intents: **Message Content** and **Server Members**. Run **one** bot process for the production token.

---

## ⚙️ Configuration

**cocobot** is highly configurable through the `config/config.py` file and environment variables. Key configuration options include:

### Required Environment Variables
- `DISCORD_BOT_TOKEN`: Discord bot token from Developer Portal
- `DISCORD_BOT_ID`: Bot application ID
- `DISCORD_SERVER_ID`: Default server ID
- At least one LLM provider API key:
  - `GEMINI_API_KEY`: Google Gemini API key (translate, transliterate)
  - `DEEPSEEK_API_KEY`: DeepSeek API key
  - `GROQ_API_KEY`: Groq API key

### LLM Provider Configuration

**Summarization** (`/summarize` command):
- `SUMMARY_PROVIDER`: LLM provider (`groq`, `gemini`, `deepseek`)
- `SUMMARY_MODEL`: Model name (e.g., `deepseek-v4-flash`, `models/gemini-2.5-flash`, `groq/compound`)

### Optional Configuration
- **Database**: `DATABASE_URL`, `DB_POOL_SIZE`, `DB_ECHO`, `INIT_DB_ON_STARTUP`
- **Cache**: `CACHE_ENABLED`, `REDIS_URL`, `CACHE_TTL`
- **Logging**: `LOG_LEVEL`, `LOG_FILE`, `LOG_MAX_BYTES`, `LOG_BACKUP_COUNT`
- **Security**: `MAX_CONTENT_LENGTH`, `ALLOWED_MENTIONS`, `ENABLE_CORS`
- **Environment**: `ENVIRONMENT` (development/production), `DEBUG`
- **Moderation**: `WARNED_ROLE_ID` (optional). Role applied on `/warn`. `/warn`, `/unwarn`, and `/simulate-leave` are staff-only.
- **Leave announcements**: `LEAVE_PUBLIC_ANNOUNCEMENTS` (`True`/`False`, default `False`) toggles the fun line in the member's last text channel. `#logs` is unchanged (`LEAVE_LOG_CHANNEL_ID`, optional; default `1513856672966246410`). Silent members are logged only.

### API Response Caching

As of `v3.4.0`, all external API responses (`/weather`, `/time`, `/exchangerate`, `/pollution`) are cached in the local database for **1 hour** (3600 seconds) to reduce latency and API usage. Cache TTL is configurable via the `CACHE_TTL` environment variable.

The `CACHE_BYPASS_PRIVILEGED` constant in `config/config.py` controls whether privileged users skip the cache:

```python
# config/config.py

# When True, guild owners, administrators, and users with Manage Server permission
# always receive a fresh API response, bypassing the 1-hour cache.
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

* **Kolja Nolte** (https://www.kolja-nolte.com)
* Ally Piechowski (https://piechowski.io)

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

[^3]: Uses Google Gemini and can produce inaccuracies.
[^4]: Translation and transliteration use Gemini. An API key is required.
