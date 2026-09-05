#  Copyright (C) 2026 by Kolja Nolte
#  kolja.nolte@gmail.com
#  https://gitlab.com/thailand-discord/bots/cocobot
#
#  This work is licensed under the MIT License. You are free to use, copy, modify,
#  merge, publish, distribute, sublicense, and/or sell copies of the Software,
#  and to permit persons to whom the Software is furnished to do so, subject to the
#  condition that the above copyright notice and this permission notice shall be
#  included in all
#  copies or substantial portions of the Software.
#
#  For more information, visit: https://opensource.org/licenses/MIT
#
#  Author:    Kolja Nolte
#  Email:     kolja.nolte@gmail.com
#  License:   MIT
#  Date:      2024-2026
#  Package:   cocobot Discord Bot

"""
Application configuration management for CocoBot.
"""

# Env vars: where secrets hide until someone commits a .env
import os

# Fail closed with sys.exit when config is a dumpster fire
import sys

# Dataclasses keep this from becoming a 400-line dict
from dataclasses import dataclass

# Optional fields: tokens that may be missing in tests
from typing import Optional

# Load .env before anyone reads os.getenv and panics
from dotenv import load_dotenv

# Typed config failures, not a naked ValueError
from utils.exceptions import ConfigurationError

# Pull .env into the process; no-op if the file is a myth
load_dotenv()


# Database knobs from env, sqlite if you forgot Postgres
@dataclass
class DatabaseConfig:
    """
    Configuration class for database connection settings.

    This class encapsulates configurations necessary for connecting to a database.
    It retrieves values from environment variables with defaults specified for each
    attribute. This makes it highly adaptable for different environments such as
    development, testing, and production.

    Attributes:
        url (str): The database connection URL. Defaults to the value of the
            'DATABASE_URL' environment variable or 'sqlite:///cocobot.db' if the
            variable is not set.
        pool_size (int): The size of the connection pool. Defaults to the value of
            the 'DB_POOL_SIZE' environment variable, with a default value of '5'.
        echo (bool): A flag to enable SQL query logging. Defaults to the value of
            the 'DB_ECHO' environment variable, interpreted as a boolean. If not
            set, the flag is False.
    """

    # Default local sqlite file; production should set DATABASE_URL
    url: str = os.getenv('DATABASE_URL', 'sqlite:///cocobot.db')

    # Pool size as int; env is always a string, because of course it is
    pool_size: int = int(os.getenv('DB_POOL_SIZE', '5'))

    # Echo SQL only if someone set DB_ECHO=true on purpose
    echo: bool = os.getenv('DB_ECHO', 'false').lower() == 'true'


# Discord token and friends; token is required unless pytest is lying
@dataclass
class DiscordConfig:
    """
    Configuration class for Discord bot settings.

    This class is used to configure various settings required to run a Discord bot, such as
    authentication token, bot and server ID, command prefix, and other related settings. It
    also includes validation to ensure that mandatory configurations are specified unless the
    application is running in a testing environment.

    Attributes:
        token (str): The bot authentication token required to connect to the Discord API.
        bot_id (Optional[str]): The unique identifier of the Discord bot (if applicable).
        server_id (Optional[str]): The unique identifier of the Discord server (if applicable).
        command_prefix (str): The command prefix used to trigger bot commands (default is '!').
        max_messages (int): The maximum number of messages to cache in memory (default is 1000).
        shard_count (Optional[int]): The number of shards to use when connecting to Discord
            (if sharding is enabled).
    """

    # Required token; empty string is not a personality
    token: str

    # Optional bot snowflake
    bot_id: Optional[str] = None

    # Optional guild snowflake
    server_id: Optional[str] = None

    # Prefix leftover from the slash-command future
    command_prefix: str = '!'

    # Message cache size; 1000 is "enough until it isn't"
    max_messages: int = 1000

    # Sharding: None means one process, one coconut
    shard_count: Optional[int] = None

    # Validate token unless tests asked us to chill
    def __post_init__(self):
        # Local import so tests can patch os.getenv after class load
        import os

        # pytest or ENVIRONMENT=testing: skip the token lecture
        if os.getenv('ENVIRONMENT') == 'testing' or os.getenv('PYTEST_CURRENT_TEST'):
            # Tests don't owe Discord a token
            return

        # Empty token in real life: fail closed
        if not self.token:
            # Point at DISCORD_BOT_TOKEN so Kolja knows which env var
            raise ConfigurationError(
                "Discord bot token is required. Please set DISCORD_BOT_TOKEN in your environment.",
                config_key="DISCORD_BOT_TOKEN",
            )


# Third-party API keys; weather and currency are the actual requirements
@dataclass
class APIConfig:
    """
    Represents the configuration required for various APIs used in the application.

    This class holds API keys needed for different services such as weather, currency conversion, geolocation,
    and integration with external platforms like Google Gemini, Groq, DeepSeek, or Acqin. It ensures that required API keys are
    properly set unless the application is in a testing environment. Keys are validated after initialization
    to ensure the application has the necessary configurations.

    Attributes:
        weatherapi_key: The API key for the weather service, if applicable.
        currencyapi_key: The API key for the currency conversion service, if applicable.
        localtime_key: The API key for time zone or local time services, if applicable.
        gemini_api_key: The API key for Gemini services, if applicable.
        gemini_model: The model name for Gemini services.
        geoapify_api_key: The API key for Geoapify services, if applicable.
        groq_api_key: The API key for Groq services, if applicable.
        groq_model: The model name for Groq services.
        acqin_api_key: The API key for Acqin services, if applicable.
        deepseek_api_key: The API key for DeepSeek services, if applicable.
        deepseek_model: The model name for DeepSeek services.
    """
    # WeatherAPI; required outside tests
    weatherapi_key: Optional[str] = None

    # CurrencyAPI; also required outside tests
    currencyapi_key: Optional[str] = None

    # Local time API if we bother
    localtime_key: Optional[str] = None

    # Gemini
    gemini_api_key: Optional[str] = None

    # Gemini model name; default filled in AppConfig
    gemini_model: str = None

    # Geoapify (env typo GEOAPFIY is preserved, don't "fix" it)
    geoapify_api_key: Optional[str] = None

    # Groq
    groq_api_key: Optional[str] = None

    # Groq model
    groq_model: str = None

    # Acqin
    acqin_api_key: Optional[str] = None

    # DeepSeek key
    deepseek_api_key: Optional[str] = None

    # DeepSeek model
    deepseek_model: str = None

    # Require weather + currency unless testing
    def __post_init__(self):
        """
        Ensures that required API keys are present in the configuration unless the application is running
        in a testing environment.

        During initialization, this method checks if the required API keys are set for weather and currency
        services. If running in a test environment, the validation is skipped to allow more flexibility in
        testing scenarios. An error is raised if any required API key is missing and the environment is not
        configured properly.

        Raises:
            ConfigurationError: If a required API key is missing in the environment and the application is not
                                running in testing mode.
        """
        # Patch-friendly os import
        import os

        # Tests skip required-key checks
        if os.getenv('ENVIRONMENT') == 'testing' or os.getenv('PYTEST_CURRENT_TEST'):
            # No keys, no problem, in CI
            return

        # The two APIs we actually refuse to boot without
        required_keys = ['weatherapi_key', 'currencyapi_key']

        # Check each required attr
        for key in required_keys:
            # Pull the attribute
            value = getattr(self, key)

            # Missing: map field name to env var style
            if not value:
                # weatherapi_key -> WEATHERAPI_API_KEY-ish via this replace
                env_key = key.upper().replace('KEY', 'API_KEY')

                # Fail with the env name humans should set
                raise ConfigurationError(
                    f"Required API key {env_key} is missing. Please set it in your environment.",
                    config_key=env_key,
                )


# Rate limits so one user cannot /weather the process to death
@dataclass
class RateLimitConfig:
    """
    Configuration for rate limits across various contexts.

    This class provides configuration options to define rate limits for commands
    and other operations in different contexts such as user, channel, and guild.
    It is designed to help manage and enforce limits to prevent abuse and ensure
    fair usage.

    Attributes:
        default_commands_per_minute (int): The default number of commands a user
            is allowed to execute per minute.
        user_global_per_minute (int): The global limit on commands a specific user
            can execute per minute across all contexts.
        channel_per_minute (int): The number of commands allowed per minute within
            a single channel.
        guild_per_minute (int): The number of commands allowed per minute within
            a single guild.
    """

    # Per-user default
    default_commands_per_minute: int = 10

    # Global per user
    user_global_per_minute: int = 20

    # Per channel
    channel_per_minute: int = 15

    # Per guild
    guild_per_minute: int = 50


# Logging: path, rotation, format from env
@dataclass
class LoggingConfig:
    """
    Configuration class for setting up logging details.

    This class defines the configuration parameters for a logging system, including log
    level, file path, file rotation parameters, and log message formatting. It aims to
    provide an easy way to control logging behavior based on environment variables while
    specifying default values when they are not provided.

    Attributes:
        level (str): The logging level defining the severity of messages to capture
            (e.g., DEBUG, INFO, WARNING, ERROR). Defaults to 'INFO'.
        file_path (str): The file path for storing the log file. Defaults to
            'logs/cocobot.log'.
        max_bytes (int): Maximum size in bytes before the log file is rotated. Defaults
            to 10MB.
        backup_count (int): The number of rotated log files to retain. Defaults to 5.
        format (str): The logging message format string. Defaults to
            '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s'.
    """

    # Default WARNING; INFO is a lifestyle choice
    level: str = os.getenv('LOG_LEVEL', 'WARNING')

    # File path
    file_path: str = os.getenv('LOG_FILE', 'logs/cocobot.log')

    # Rotation size; comment in original said ~1MB, number is 1485760
    max_bytes: int = int(os.getenv('LOG_MAX_BYTES', '1485760'))  # ~1MB

    # How many rotated files to keep
    backup_count: int = int(os.getenv('LOG_BACKUP_COUNT', '5'))

    # Format string; lineno is how you find the coconut
    format: str = os.getenv(
        'LOG_FORMAT', '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s'
    )


# Cache: optional Redis, default TTL an hour
@dataclass
class CacheConfig:
    """Cache configuration settings."""

    # Enabled unless CACHE_ENABLED is not true
    enabled: bool = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'

    # Redis URL or None for in-process whatever
    redis_url: Optional[str] = os.getenv('REDIS_URL')

    # TTL seconds
    default_ttl: int = int(os.getenv('CACHE_TTL', '3600'))  # 1 hour


# Content length, mentions, CORS (CORS on a Discord bot; sure)
@dataclass
class SecurityConfig:
    """Security configuration settings."""

    # Max content length ~10KB
    max_content_length: int = int(os.getenv('MAX_CONTENT_LENGTH', '10000'))  # 10 KB

    # Allowed mentions flag
    allowed_mentions: bool = os.getenv('ALLOWED_MENTIONS', 'true').lower() == 'true'

    # CORS off by default
    enable_cors: bool = os.getenv('ENABLE_CORS', 'false').lower() == 'true'


# Root config: version, env, nested component configs
@dataclass
class AppConfig:
    """Main application configuration."""

    # Semver we advertise
    version: str = "3.8.0"

    # Process name
    name: str = "cocobot"

    # One-liner for the Thailand Discord
    description: str = "A feature-rich Discord bot for the Thailand Discord server"

    # production unless ENVIRONMENT says otherwise
    environment: str = os.getenv('ENVIRONMENT', 'production')

    # Debug flag
    debug: bool = os.getenv('DEBUG', 'false').lower() == 'true'

    # Nested Discord config, filled in post_init
    discord: DiscordConfig = None

    # Nested API keys
    api: APIConfig = None

    # Nested DB
    database: DatabaseConfig = None

    # Nested rate limits
    rate_limit: RateLimitConfig = None

    # Nested logging
    logging: LoggingConfig = None

    # Nested cache
    cache: CacheConfig = None

    # Nested security
    security: SecurityConfig = None

    # Fill any None nested configs from env
    def __post_init__(self):
        # Discord block
        if self.discord is None:
            # Token + optional IDs from env
            self.discord = DiscordConfig(
                token=os.getenv('DISCORD_BOT_TOKEN'),
                bot_id=os.getenv('DISCORD_BOT_ID'),
                server_id=os.getenv('DISCORD_SERVER_ID'),
            )

        # API keys block
        if self.api is None:
            # Defaults for models live here, including the GEOAPFIY typo
            self.api = APIConfig(
                weatherapi_key=os.getenv('WEATHERAPI_API_KEY'),
                currencyapi_key=os.getenv('CURRENCYAPI_API_KEY'),
                localtime_key=os.getenv('LOCALTIME_API_KEY'),
                gemini_api_key=os.getenv('GEMINI_API_KEY'),
                gemini_model=os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'),
                geoapify_api_key=os.getenv('GEOAPFIY_API_KEY'),
                groq_api_key=os.getenv('GROQ_API_KEY'),
                groq_model=os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b'),
                acqin_api_key=os.getenv('ACQIN_API_KEY'),
                deepseek_api_key=os.getenv('DEEPSEEK_API_KEY'),
                deepseek_model=os.getenv('DEEPSEEK_MODEL', 'deepseek-chat'),
            )

        # Database defaults
        if self.database is None:
            # Field defaults from env
            self.database = DatabaseConfig()

        # Rate limits
        if self.rate_limit is None:
            # Class defaults
            self.rate_limit = RateLimitConfig()

        # Logging
        if self.logging is None:
            # Env-backed logging
            self.logging = LoggingConfig()

        # Cache
        if self.cache is None:
            # Env-backed cache
            self.cache = CacheConfig()

        # Security
        if self.security is None:
            # Env-backed security
            self.security = SecurityConfig()


# Build AppConfig; tests skip validate+exit
def get_config() -> AppConfig:
    """
    Get the application configuration instance.

    Returns:
                    AppConfig: The application configuration

    Raises:
                    ConfigurationError: If required configuration is missing
    """
    # Patch-friendly os
    import os

    # Testing: construct but don't sys.exit
    if os.getenv('ENVIRONMENT') == 'testing' or os.getenv('PYTEST_CURRENT_TEST'):
        # Bare AppConfig
        config = AppConfig()

        # Return without validate_config
        return config

    # Production path: validate or die
    try:
        # Build from env
        config = AppConfig()

        # Extra checks beyond dataclass post_init
        validate_config(config)

        # Good enough to boot
        return config

    # Any failure: print and exit 1
    except Exception as e:
        # Human-readable line to stderr via print (yes, print)
        print(f"Configuration error: {e}")

        # Don't start a bot with a hole in the hull
        sys.exit(1)


# Extra validation: token, API keys, environment name
def validate_config(config: AppConfig) -> bool:
    """
    Validate the application configuration.

    Args:
                    config: The application configuration to validate

    Returns:
                    bool: True if configuration is valid

    Raises:
                    ConfigurationError: If configuration validation fails
    """
    # Discord token still required here
    if not config.discord.token:
        # Fail with key name
        raise ConfigurationError(
            "Discord token is required", config_key="DISCORD_BOT_TOKEN"
        )

    # WeatherAPI
    if not config.api.weatherapi_key:
        # Fail
        raise ConfigurationError(
            "WeatherAPI key is required", config_key="WEATHERAPI_API_KEY"
        )

    # CurrencyAPI
    if not config.api.currencyapi_key:
        # Fail
        raise ConfigurationError(
            "CurrencyAPI key is required", config_key="CURRENCYAPI_API_KEY"
        )

    # Only development or production; "staging" is not invited
    valid_environments = ['development', 'production']

    # Reject unknown ENVIRONMENT values
    if config.environment not in valid_environments:
        # Include the allowed list
        raise ConfigurationError(
            f"Invalid environment '{config.environment}'. Must be one of {valid_environments}",
            config_key="ENVIRONMENT",
        )

    # Valid
    return True


# Process-wide singleton, lazy
_config: Optional[AppConfig] = None


# Get or create the singleton
def get_global_config() -> AppConfig:
    """
    Get the global application configuration instance.

    Returns:
                    AppConfig: The global application configuration
    """
    # Mutate module singleton
    global _config

    # First call builds it
    if _config is None:
        # May sys.exit on failure
        _config = get_config()

    # Subsequent calls reuse
    return _config


# Tests call this so they don't inherit production secrets
def reset_config():
    """Reset the global configuration (useful for testing)."""
    # Clear the singleton
    global _config

    # Next get_global_config rebuilds
    _config = None


# Convenience: Discord token
def get_discord_token() -> str:
    """Get the Discord bot token."""
    # Via singleton
    return get_global_config().discord.token


# Convenience: environment name
def get_environment() -> str:
    """Get the current environment."""
    # Via singleton
    return get_global_config().environment


# Convenience: debug flag
def is_debug() -> bool:
    """Check if the application is running in debug mode."""
    # Via singleton
    return get_global_config().debug


# Convenience: version string
def get_version() -> str:
    """Get the application version."""
    # Via singleton
    return get_global_config().version


# Shared error copy for cogs that import this
ERROR_MESSAGE: str = "🥥 Oops, something's cracked, and it's **not** the coconut!"
