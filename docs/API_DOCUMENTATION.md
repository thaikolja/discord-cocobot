# Cocobot API Documentation

## Overview

Cocobot is a feature-rich Discord bot providing various utilities including weather, time, currency conversion, translation, and more. This document provides comprehensive information about the bot's commands, API endpoints (if any), and configuration.

## Commands

### Weather Command
- **Command**: `/weather`
- **Description**: Get the current weather for a location
- **Parameters**:
  - `location` (string, optional): The location you want the weather for (Default: Bangkok)
  - `units` (choice, optional): Unit system: Metric (°C) or Imperial (°F) (Default: Civilized Units (°C))
- **Response**: Weather information including temperature, feels like, humidity, and condition

### Exchange Rate Command
- **Command**: `/exchangerate`
- **Description**: Get the current exchange rate between two currencies
- **Parameters**:
  - `from_currency` (string, optional): The currency to convert from (Default: USD)
  - `to_currency` (string, optional): The currency to convert to (Default: THB)
  - `amount` (integer, optional): The amount of money to convert (Default: 1)
- **Response**: Exchange rate information with conversion result

### Time Command
- **Command**: `/time`
- **Description**: Get the current time in a specific location
- **Parameters**:
  - `location` (string, optional): The location to get time for (Default: Thailand)
  - `format` (choice, optional): Time format (Default: 24-hour)
- **Response**: Current time in the specified location

### Locate Command
- **Command**: `/locate`
- **Description**: Find addresses and get a Google Maps link
- **Parameters**:
  - `location` (string, required): The location to search for
  - `city` (string, optional): The city to search in (Default: Bangkok)
- **Response**: Location information with Google Maps link

### Pollution Command
- **Command**: `/pollution`
- **Description**: Check air quality index (AQI) for any city
- **Parameters**:
  - `city` (string, required): The city to check pollution for
- **Response**: Air quality information with AQI level

### Transliterate Command
- **Command**: `/transliterate`
- **Description**: Convert Thai text to Latin script
- **Parameters**:
  - `text` (string, required): The text to transliterate
- **Response**: Transliterated text in Latin script

### Learn Command
- **Command**: `/learn`
- **Description**: Shows one of the 250 core Thai words and its translation and transliteration
- **Parameters**: None
- **Response**: Thai word with translation and transliteration

### Translate Command
- **Command**: `/translate`
- **Description**: Translate text between languages using AI
- **Parameters**:
  - `text` (string, required): The text to be translated
  - `from_language` (string, optional): Source language (Default: Thai)
  - `to_language` (string, optional): Target language (Default: English)
- **Response**: Translated text

## Configuration

### Environment Variables

The bot requires several environment variables to function properly. Copy `.env.example` to `.env` and fill in the values:

- `DISCORD_BOT_TOKEN`: Your Discord bot token (required)
- `WEATHERAPI_API_KEY`: Your WeatherAPI key (required)
- `CURRENCYAPI_API_KEY`: Your CurrencyAPI key (required)
- `LOCALTIME_API_KEY`: Your LocalTime API key
- `GOOGLE_API_KEY`: Your Google API key
- `GOOGLE_MAPS_API_KEY`: Your Google Maps API key
- `GEOAPFIY_API_KEY`: Your Geoapify API key
- `ACQIN_API_KEY`: Your AcqIn API key
- `GROQ_API_KEY`: Your Groq API key
- `SAMBANOVA_API_KEY`: Your Sambanova API key
- `DISCORD_SERVER_ID`: Your Discord server ID
- `DISCORD_BOT_ID`: Your Discord bot ID

### Configuration File

The bot uses a centralized configuration system. Key configuration options include:

- **Database Configuration**:
  - `url`: Database connection URL (default: sqlite:///cocobot.db)
  - `pool_size`: Connection pool size (default: 5)
  - `echo`: Enable SQL logging (default: false)

- **Discord Configuration**:
  - `token`: Bot token (required)
  - `server_id`: Target server ID (optional)
  - `bot_id`: Bot application ID (optional)
  - `command_prefix`: Prefix for text commands (default: !)
  - `max_messages`: Max messages to cache (default: 1000)

- **Rate Limiting Configuration**:
  - `default_commands_per_minute`: Default rate limit per user (default: 10)
  - `user_global_per_minute`: Global rate limit per user (default: 20)
  - `channel_per_minute`: Rate limit per channel (default: 15)
  - `guild_per_minute`: Rate limit per guild (default: 50)

## Development

### Prerequisites

- Python 3.8+
- Discord account and developer application
- API keys for required services

### Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill in API keys
6. Run the bot: `python bot.py`

### Architecture

The bot follows a modular architecture with the following components:

- `bot.py`: Main application entry point
- `cogs/`: Command modules (weather, time, currency, etc.)
- `config/`: Configuration management
- `utils/`: Utility functions (logging, security, monitoring, etc.)
- `tests/`: Test suite

Each command is implemented as a separate cog following Discord.py's extension system.

## Error Handling

The bot includes comprehensive error handling:

- Missing required arguments
- Invalid parameters
- API request failures
- Rate limit exceeded
- Network timeouts
- Database connection errors

Users receive user-friendly error messages while detailed logs are maintained for debugging.

## Monitoring and Metrics

The bot collects various metrics:

- Command usage statistics
- API call success/failure rates
- Response times
- System resource usage
- Error counts

Metrics are available via the monitoring system for operational visibility.

## Rate Limiting

The bot implements multiple layers of rate limiting:

- Per-user limits (default: 10 commands per minute)
- Per-channel limits (default: 15 requests per minute)
- Per-guild limits (default: 50 requests per minute)
- Global limits (default: 100 requests per minute)

Rate limits are enforced both in-memory and persisted to the database.

## Security

Security measures include:

- Input validation and sanitization
- Protection against XSS and injection attacks
- Rate limiting to prevent abuse
- Secure handling of API keys
- Validation of user inputs

## API Reference

### Database Models

The bot uses SQLAlchemy ORM with the following models:

#### User Model
- `id`: Primary key
- `discord_id`: Unique Discord user ID
- `username`: Discord username
- `discriminator`: Discord discriminator (legacy)
- `avatar_url`: User avatar URL
- `is_premium`: Premium status
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `last_command_at`: Last command execution timestamp

#### Guild Model
- `id`: Primary key
- `discord_id`: Unique Discord guild ID
- `name`: Guild name
- `owner_id`: Guild owner ID
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `is_active`: Active status
- `prefix`: Custom command prefix

#### CommandUsage Model
- `id`: Primary key
- `command_name`: Name of the command
- `user_id`: User ID (foreign key)
- `guild_id`: Guild ID (foreign key, optional)
- `channel_id`: Channel ID
- `executed_at`: Execution timestamp
- `execution_time_ms`: Execution time in milliseconds
- `success`: Success status
- `error_message`: Error message if failed

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request with a clear description

Please follow the existing code style and include documentation for new features.