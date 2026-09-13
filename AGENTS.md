# Cocobot Discord Bot - AI Agent Instructions

## Project Overview

**Cocobot** is a feature-rich Discord bot designed for the Thailand Discord community. It provides various useful features including weather queries, time conversion, currency exchange, translation services, Thai language learning, air quality monitoring, AI-powered chat summarization, and more.

### Key Features
- 🌤️ **Weather** - Real-time weather for any location worldwide with °C/°F toggle
- 🕓 **Time** - Local time for cities and countries around the world
- 💱 **Exchange Rates** - Real-time currency conversion
- 🌐 **Translation** - Multi-language text translation with auto-detection
- 🎓 **Thai Learning** - 250 core Thai vocabulary words
- 🌫️ **Air Quality** - AQI queries for global cities
- 🔤 **Transliteration** - Thai to Latin script conversion via AI
- 📝 **AI Summarize** - Summarize recent chat messages using AI
- 🔒 **AI Jail** - Admin-only jail system with AI harassment
- 🛡️ **Admin Commands** - Admin-only commands (reset visa reminders, jail/unjail)
- ⚡ **API Caching** - Database-backed caching for API responses with privileged user bypass

## Tech Stack

- **Language**: Python 3.13+ (Docker: Python 3.11)
- **Framework**: discord.py 2.6
- **Database**: SQLAlchemy 2.0 (SQLite/PostgreSQL)
- **Cache**: Database-backed cache with Redis support (Docker deployment)
- **Testing**: pytest + pytest-asyncio + pytest-mock + requests-mock
- **Code Style**: black + isort + flake8
- **AI Services**: Google GenAI (Gemini), Groq, DeepSeek
- **HTTP Client**: aiohttp
- **Deployment**: systemd/Docker

## Project Structure

```
cocobot/
├── bot.py                  # Main entry point (Cocobot class)
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── pyproject.toml         # Tool configuration (black, isort, flake8, pytest)
├── pytest.ini             # pytest configuration
├── .flake8               # flake8 configuration
├── .editorconfig         # Editor configuration
├── .gitlab-ci.yml        # GitLab CI/CD pipeline (test + deploy)
├── CHANGELOG.md          # Release changelog
├── CONTRIBUTING.md       # Contribution guidelines
├── deploy.sh             # Docker deployment shortcut
├── on.sh                 # systemd start shortcut
├── off.sh                # systemd stop shortcut
├── docker-compose.yml    # Docker deployment configuration
├── Dockerfile            # Docker image build configuration
│
├── cogs/                 # Command modules
│   ├── __init__.py
│   ├── admin.py          # Admin commands (reset visa reminders)
│   ├── exchangerate.py   # Currency exchange
│   ├── jail.py           # AI Jail system (admin-only)
│   ├── learn.py          # Thai learning
│   ├── pollution.py      # Air quality
│   ├── summarize.py      # AI chat summarization
│   ├── time.py           # Time queries
│   ├── translate.py      # Translation services (auto-detect Thai/English)
│   ├── transliterate.py  # AI-based Thai transliteration
│   └── weather.py        # Weather queries with °C/°F toggle
│
├── config/               # Configuration management
│   ├── __init__.py
│   ├── app_config.py     # Advanced configuration system (dataclasses)
│   └── config.py         # Configuration constants
│
├── utils/                # Utility functions
│   ├── __init__.py
│   ├── cache.py          # CacheManager (Redis + in-memory, @cached decorators)
│   ├── database.py       # Database ORM (CacheEntry, RateLimit, VisaReminder, JailedUser)
│   ├── exceptions.py     # Custom exception hierarchy
│   ├── helpers.py        # UseAI class, channel-to-location mapping
│   ├── logger.py         # Logging configuration
│   ├── rate_limit.py     # Rate limiters (in-memory, DB-backed, hybrid)
│   ├── security.py       # InputValidator, InputSanitizer, SecurityChecker
│   └── monitoring.py     # MetricsCollector, HealthChecker, BotMetrics
│
├── tests/                # Test suite
│   ├── __init__.py
│   ├── conftest.py       # pytest fixtures and configuration
│   ├── test_database.py  # Database tests
│   ├── test_exceptions.py
│   ├── test_exchangerate.py
│   ├── test_jail.py
│   ├── test_learn.py
│   ├── test_pollution.py
│   ├── test_security.py  # Security tests
│   ├── test_summarize.py
│   ├── test_time.py
│   ├── test_translate.py
│   ├── test_transliterate.py
│   ├── test_utils.py     # Cache tests
│   └── test_weather.py
│
├── scripts/              # Script tools
│   ├── dependency_audit.py
│   ├── deploy-as-docker.sh
│   └── deploy-as-service.sh
│
├── assets/               # Static assets
│   ├── data/            # Data files
│   │   ├── thai-words.json (250 core Thai vocabulary)
│   │   └── thai-vocabulary-level-1.json
│   └── img/             # Image assets (avatars, banners)
│
├── logs/                # Log directory (gitignored)
└── venv/                # Virtual environment (gitignored)
```

## Environment Variables

Copy `.env.example` to `.env` and configure the following:

```bash
# ============================================================================
# DISCORD CONFIGURATION
# ============================================================================
DISCORD_BOT_ID=
DISCORD_BOT_TOKEN=
DISCORD_SERVER_ID=

# ============================================================================
# LLM PROVIDER SETTINGS
# ============================================================================
# Summarization function (options: google, groq, deepseek)
SUMMARY_PROVIDER=deepseek
SUMMARY_MODEL=deepseek-v4-flash

# Google Gemini (Translate, Transliterate) — https://aistudio.google.com/app/apikey
GEMINI_API_KEY=
GEMINI_MODEL=models/gemini-2.5-flash-lite

# DeepSeek — https://platform.deepseek.com/
DEEPSEEK_API_KEY=
DEEPSEEK_MODEL=deepseek-v4-flash

# Groq — https://console.groq.com/keys
GROQ_API_KEY=
GROQ_MODEL=groq/compound

# ============================================================================
# EXTERNAL API KEYS
# ============================================================================
# Weather data — https://www.weatherapi.com/signup.aspx
WEATHERAPI_API_KEY=

# Local time — https://api.ipgeolocation.io/timezone
LOCALTIME_API_KEY=

# Currency exchange rates — https://app.currencyapi.com/register
CURRENCYAPI_API_KEY=

# Air quality — https://acqin.org/api-access
ACQIN_API_KEY=

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
DATABASE_URL=sqlite:///cocobot.db
DB_POOL_SIZE=5
DB_ECHO=false
INIT_DB_ON_STARTUP=true

# ============================================================================
# CACHE CONFIGURATION (Optional)
# ============================================================================
# CACHE_ENABLED=true
# REDIS_URL=
# CACHE_TTL=3600

# ============================================================================
# LOGGING
# ============================================================================
LOG_LEVEL=INFO
LOG_FILE=logs/cocobot.log
LOG_MAX_BYTES=1485760
LOG_BACKUP_COUNT=3

# ============================================================================
# SECURITY & PERFORMANCE
# ============================================================================
MAX_CONTENT_LENGTH=10000
ALLOWED_MENTIONS=true
ENABLE_CORS=false

# ============================================================================
# ENVIRONMENT
# ============================================================================
ENVIRONMENT=production
DEBUG=false

# ============================================================================
# JAIL SYSTEM CONFIGURATION
# ============================================================================
JAIL_ROLE_ID=1475877270898872501
AUGUST_INTERNAL_HOST=127.0.0.1
AUGUST_INTERNAL_PORT=17432
AUGUST_INTERNAL_SECRET=
```

**Note:** The configuration system (`config/app_config.py`) uses dataclasses for type-safe configuration loading from environment variables. Includes component-based configs for Discord, API, Database, Cache, RateLimits, Logging, and Security.

## Available Commands

### Slash Commands

- `/weather [location] [units]` - Get real-time weather for a location with °C/°F toggle (default: channel's city or Bangkok, metric)
- `/time [location]` - Get local time for a location (default: Bangkok)
- `/exchangerate [from_currency] [to_currency] [amount]` - Currency conversion (default: USD to THB, amount 1)
- `/translate <text> [from_language] [to_language]` - Translate text with auto-detection of Thai/English (default: auto)
- `/transliterate <text>` - Convert Thai text to Latin script using AI
- `/pollution [city]` - Check air quality index for a city (default: channel's city or Bangkok)
- `/learn` - Learn a random Thai vocabulary word
- `/summarize [limit]` - Summarize recent messages (default: 20, max: 50)
- `/jail <user> [reason]` - Jail a user (admin only)
- `/unjail <user>` - Unjail a user and restore roles (admin only)

### Prefix Commands

- `!reset_reminder [@user]` - Reset user's visa reminder status (admin only)

### Special Triggers

- `@cocobot` or `!cocobot` - Display bot info (version, avatar, contributor link)
- Messages containing "visa" in the `visa` channel - Auto-remind users to mention nationality (persistent via VisaReminder DB)
- Messages containing "tate" - Display Bottom G GIF (3-minute per-user cooldown)
- Mentioning `@Nal` - Display tribute image

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Code Quality Checks
```bash
# Run flake8 check
flake8 .

# Run isort check
isort --check-only --profile=black --line-length=88 .

# Run black check
black --check --line-length=88 --target-version=py313 .

# Auto-format code
black --line-length=88 --target-version=py313 .
isort --profile=black --line-length=88 .
```

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_weather.py -v

# Run with coverage
pytest --cov=cogs --cov=utils tests/

# Verbose output
pytest -v --tb=short
```

### Starting the Bot
```bash
# Development mode
python bot.py

# Production mode (using systemd)
sudo systemctl start cocobot

# Docker mode
docker-compose up -d

# View Docker logs
docker-compose logs -f cocobot
```

## Code Style Guidelines

### Formatting Tool Configuration
- **Black**: Line length 88 characters, Python 3.13+ target version
- **isort**: Black-compatible configuration, group imports by type
- **flake8**: Ignore E203, W503, E402, C901 rules; max line length 88

### Import Order
```python
# 1. Standard library
import os
import sys

# 2. Third-party libraries
import discord
import pytest

# 3. Local modules
from cogs.weather import WeatherCog
from utils.helpers import sanitize_url
```

### Code Organization
- Each cog file corresponds to a feature module
- Use async/await for asynchronous operations
- Add appropriate docstrings and type hints
- Use custom exception classes for error handling

## Adding New Commands

1. Create a new file in the `cogs/` directory (e.g., `newfeature.py`)
2. Inherit from `commands.Cog` class
3. Use `@app_commands.command()` decorator to register slash commands
4. Add the module name to `INITIAL_EXTENSIONS` in `bot.py`

Example:
```python
# cogs/newfeature.py
import discord
from discord import app_commands
from discord.ext import commands

class NewFeatureCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="newcommand", description="Description")
    async def new_command(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello!")

async def setup(bot):
    await bot.add_cog(NewFeatureCog(bot))
```

## Database Schema

### Main Data Models
- **CacheEntry**: Stores cached API responses with TTL expiration
- **RateLimit**: Tracks rate limit usage per user/channel/guild
- **VisaReminder**: Visa reminder status tracking (persistent across restarts)
- **JailedUser**: AI Jail system - stores jailed user data including role snapshots

### Database Initialization
```bash
# SQLite (default)
# Database file is created automatically on startup (configurable via INIT_DB_ON_STARTUP)

# PostgreSQL (production)
# Configure DATABASE_URL environment variable
# Example: postgresql://user:password@localhost:5432/cocobot
```

### Caching System
- All external API responses are cached for 1 hour (3600 seconds) by default
- Cache TTL configurable via `CACHE_TTL` env var
- Redis support in Docker deployment (falls back to DB cache)
- Cache keys are query-specific for different arguments
- Privileged users (server owners, admins, manage_guild permission) bypass cache by default
- Provides `CacheManager` class with `get`, `set`, `delete`, `@cached`, `@api_cached` decorators

## API Integration

### Currently Used API Services
- **WeatherAPI** (weatherapi.com): Weather data
- **ipgeolocation.io**: Time data
- **CurrencyAPI** (currencyapi.com): Exchange rate data
- **waqi.info**: Air quality data (uses ACQIN_API_KEY env var)
- **Google GenAI (Gemini)**: Translation, transliteration, chat
- **Groq / DeepSeek**: AI summarization (configurable via SUMMARY_PROVIDER)

### Adding New APIs
1. Add API key in `.env`
2. Add configuration in `config/app_config.py` (APIConfig class)
3. Add constant in `config/config.py` if needed
4. Implement API calls in the appropriate cog
5. Add error handling and rate limiting
6. Write unit tests

## AI Features

### AI Jail System (`cogs/jail.py`)
- Admin-only `/jail` command to restrict users
- Strips all roles and assigns a "Jailed" role
- Integrates with August Engelhardt bot for harassment
- `/unjail` restores original roles from DB snapshot
- Automatic cleanup when jailed users leave the server
- Stores role snapshots for restoration

### AI Summarization (`cogs/summarize.py`)
- `/summarize [limit]` command (max 50 messages, default 20)
- Provider configurable via `SUMMARY_PROVIDER` env var (groq, google, deepseek)
- Model configurable via `SUMMARY_MODEL` env var
- Uses `asyncio.to_thread()` for non-blocking AI calls
- Truncates output to 1000 characters

### AI Translation (`cogs/translate.py`)
- `/translate <text> [from_language] [to_language]`
- Auto-detects Thai vs English via Unicode range analysis
- Uses Gemini provider with low temperature (0.3)
- Normalizes language names for cross-provider compatibility

### AI Transliteration (`cogs/transliterate.py`)
- `/transliterate <text>` converts Thai to Latin script
- Uses Gemini with detailed diacritic and tone-marking instructions

### AI Helper Class (`utils/helpers.py`)
- `UseAI` class for unified AI provider interface
- Supports three providers: Google (Gemini), Groq, DeepSeek
- Groq uses the native `groq` SDK
- DeepSeek uses the OpenAI-compatible endpoint via `openai` SDK (lazy-imported)
- Google uses `google-genai` SDK
- Async-compatible with `asyncio.to_thread()`

## Deployment

### Systemd Service Deployment
```bash
# Create service file
sudo nano /etc/systemd/system/cocobot.service

# Reload configuration
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable cocobot

# Start service
sudo systemctl start cocobot

# View logs
sudo journalctl -u cocobot -f

# Stop service
sudo systemctl stop cocobot

# Restart service
sudo systemctl restart cocobot
```

### Docker Deployment (Recommended)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f cocobot

# Stop services
docker-compose down

# View database logs
docker-compose logs -f db

# View Redis logs
docker-compose logs -f redis
```

### Docker Service Architecture
- **cocobot**: Main application container (Python 3.11-slim)
- **db**: PostgreSQL 15 Alpine database
- **redis**: Redis 7 Alpine cache and session storage

### Docker-Specific Configuration
- Database URL: `postgresql://cocobot:password@db:5432/cocobot`
- Redis URL: `redis://redis:6379/0`
- August host: `host.docker.internal` (configured via extra_hosts for Linux support)

### Deployment Scripts
- `deploy.sh` → `scripts/deploy-as-docker.sh`: Git pull, docker-compose rebuild, health check
- `scripts/deploy-as-service.sh`: systemctl stop, git pull, pip install, systemctl start
- `on.sh` / `off.sh`: systemctl start/stop shortcuts

## CI/CD (`.gitlab-ci.yml`)

Two-stage pipeline:
- **test**: Python 3.13-slim, pip install, pytest with TESTING environment
- **deploy**: SSH to host, run remote deploy script (main branch only, depends on test pass)

## Debugging and Monitoring

### Log Files
- Logs are located in the `logs/` directory
- Uses rotating file handler with configurable max bytes and backup count
- Loggers: `bot_logger`, `command_logger`, `api_logger`, `error_logger`
- Configurable via `LOG_LEVEL`, `LOG_FILE`, `LOG_MAX_BYTES`, `LOG_BACKUP_COUNT`

### Common Issues
1. **Cannot connect to Discord**: Check `DISCORD_BOT_TOKEN`
2. **API call failures**: Check corresponding API keys and network connection
3. **Commands not responding**: Check bot logs and Discord permissions
4. **Database errors**: Check `DATABASE_URL` and `INIT_DB_ON_STARTUP` settings
5. **Docker container won't start**: Check `.env` file and environment variables
6. **AI Jail not working**: Check `JAIL_ROLE_ID` and August API configuration
7. **Cache issues**: Check `CACHE_ENABLED` and `REDIS_URL` settings

### Monitoring Metrics
- `BotMetrics`: Command usage counts, durations, API calls, errors
- `PerformanceMonitor`: CPU, memory, disk, process metrics via psutil
- `HealthChecker`: Registered health checks for DB, APIs
- `MetricsCollector`: Prometheus-compatible counters, gauges, histograms
- Export to Prometheus format or JSON file

## Testing

### Test Structure
- Each cog has a corresponding test file (`test_*.py`)
- Uses pytest and pytest-asyncio for asynchronous testing
- Uses pytest-mock for mocking
- Uses requests-mock for HTTP request mocking
- Tests properly patch database cache operations
- `conftest.py` provides shared fixtures (mock_bot, mock_discord_*, cleanup_visa_reminders)

### Running Specific Tests
```bash
# Test weather functionality
pytest tests/test_weather.py -v

# Test exchange rate functionality
pytest tests/test_exchangerate.py -v

# Test translation functionality
pytest tests/test_translate.py -v

# Test jail functionality
pytest tests/test_jail.py -v

# Test summarization functionality
pytest tests/test_summarize.py -v

# Test database functionality
pytest tests/test_database.py -v

# Test security functionality
pytest tests/test_security.py -v

# Test cache and utilities
pytest tests/test_utils.py -v
```

### Test Coverage
```bash
# Generate coverage report
pytest --cov=cogs --cov=utils --cov-report=html tests/

# View HTML report
open htmlcov/index.html
```

## Contributing Guidelines

1. Fork the project and create a feature branch
2. Follow existing code style and conventions
3. Add tests for new features
4. Update relevant documentation (including AGENTS.md)
5. Run all tests to ensure they pass
6. Run code quality checks (black, isort, flake8)
7. Submit a Pull Request

### Code Review Checklist
- [ ] Code follows Black and isort conventions
- [ ] All tests pass
- [ ] Appropriate error handling is added
- [ ] Relevant documentation is updated
- [ ] No security vulnerabilities are introduced
- [ ] Performance impact has been assessed
- [ ] Database migrations are handled properly
- [ ] Cache invalidation is considered for API changes

## Security Best Practices

- Never commit `.env` file to version control
- Use strong passwords and API keys
- Rotate API keys regularly
- Limit Discord bot permissions
- Run Docker containers as non-root user (appuser)
- Update dependencies regularly (use `scripts/dependency_audit.py`)
- Monitor exception logs and errors
- Keep `AUGUST_INTERNAL_SECRET` secure and unique
- Validate all user inputs via `utils/security.py` (InputValidator, InputSanitizer, SecurityChecker)
- Use parameterized queries to prevent SQL injection
- Limit message content length (`MAX_CONTENT_LENGTH`)
- Sanitize HTML/markdown injection via bleach

## Configuration Management

### Advanced Configuration System
- Uses dataclasses in `config/app_config.py` for type-safe configuration
- Environment-based configuration loading (via python-dotenv)
- Validation for required settings in production mode
- Support for testing mode with relaxed validation
- Component-based organization: DiscordConfig, APIConfig, DatabaseConfig, CacheConfig, RateLimitConfig, LoggingConfig, SecurityConfig
- Convenience accessors and reset functions

### Environment Modes
- **production**: Default mode with all validations enabled
- **development**: Development mode with debug features
- **testing**: Test mode with relaxed validation

### Dependency Security Audit
The project includes a security audit script at `scripts/dependency_audit.py` that:
- Checks for dependency vulnerabilities using `safety`
- Identifies outdated packages
- Runs Bandit security scans on the codebase
- Generates comprehensive security reports

Run the audit:
```bash
python scripts/dependency_audit.py
```

## License

MIT License - See LICENSE file for details

---

*Last updated: May 13, 2026*
*Version: 3.5.3*
