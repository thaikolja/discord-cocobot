"""
Advanced configuration management for the cocobot application.

This module provides a robust configuration system with validation,
type hints, and fallback mechanisms.
"""

import os
import sys
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

from utils.exceptions import ConfigurationError

# Load environment variables
load_dotenv()


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

    url: str = os.getenv('DATABASE_URL', 'sqlite:///cocobot.db')
    pool_size: int = int(os.getenv('DB_POOL_SIZE', '5'))
    echo: bool = os.getenv('DB_ECHO', 'false').lower() == 'true'


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

    token: str
    bot_id: Optional[str] = None
    server_id: Optional[str] = None
    command_prefix: str = '!'
    max_messages: int = 1000
    shard_count: Optional[int] = None

    def __post_init__(self):
        # Check if we're in a testing environment to be more permissive
        import os

        if os.getenv('ENVIRONMENT') == 'testing' or os.getenv('PYTEST_CURRENT_TEST'):
            # In testing mode, allow missing token
            return

        if not self.token:
            raise ConfigurationError(
                "Discord bot token is required. Please set DISCORD_BOT_TOKEN in your environment.",
                config_key="DISCORD_BOT_TOKEN",
            )


@dataclass
class APIConfig:
    """
    Encapsulates configuration settings for various API integrations.

    This class is designed to hold API keys required for interacting with different
    service providers, including Weather API, Currency API, Google API, and others.
    It includes validation logic to ensure essential keys are provided unless the
    application is running in a testing environment.

    Attributes:
        weatherapi_key (Optional[str]): API key for accessing the Weather API.
        currencyapi_key (Optional[str]): API key for accessing the Currency API.
        localtime_key (Optional[str]): API key for obtaining local time data.
        google_api_key (Optional[str]): Google API key for accessing Google services.
        geoapify_api_key (Optional[str]): API key for Geoapify services.
        groq_api_key (Optional[str]): API key for Groq-related operations.
    """

    weatherapi_key: Optional[str] = None
    currencyapi_key: Optional[str] = None
    localtime_key: Optional[str] = None
    google_api_key: Optional[str] = None
    geoapify_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None,
    acqin_api_key: Optional[str] = None

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
        # Check if we're in a testing environment to be more permissive
        import os

        if os.getenv('ENVIRONMENT') == 'testing' or os.getenv('PYTEST_CURRENT_TEST'):
            # In testing mode, skip validation of required keys
            return

        # Validate required keys are present
        required_keys = ['weatherapi_key', 'currencyapi_key']
        for key in required_keys:
            value = getattr(self, key)
            if not value:
                env_key = key.upper().replace('KEY', 'API_KEY')
                raise ConfigurationError(
                    f"Required API key {env_key} is missing. Please set it in your environment.",
                    config_key=env_key,
                )


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

    default_commands_per_minute: int = 10
    user_global_per_minute: int = 20
    channel_per_minute: int = 15
    guild_per_minute: int = 50


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

    level: str = os.getenv('LOG_LEVEL', 'INFO')
    file_path: str = os.getenv('LOG_FILE', 'logs/cocobot.log')
    max_bytes: int = int(os.getenv('LOG_MAX_BYTES', '10485760'))  # 10MB
    backup_count: int = int(os.getenv('LOG_BACKUP_COUNT', '5'))
    format: str = os.getenv(
        'LOG_FORMAT', '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s'
    )


@dataclass
class CacheConfig:
    """Cache configuration settings."""

    enabled: bool = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    redis_url: Optional[str] = os.getenv('REDIS_URL')
    default_ttl: int = int(os.getenv('CACHE_TTL', '3600'))  # 1 hour


@dataclass
class SecurityConfig:
    """Security configuration settings."""

    max_content_length: int = int(os.getenv('MAX_CONTENT_LENGTH', '10000'))  # 10 KB
    allowed_mentions: bool = os.getenv('ALLOWED_MENTIONS', 'true').lower() == 'true'
    enable_cors: bool = os.getenv('ENABLE_CORS', 'false').lower() == 'true'


@dataclass
class AppConfig:
    """Main application configuration."""

    version: str = "3.3.0"  # Updated version
    name: str = "cocobot"
    description: str = "A feature-rich Discord bot for the Thailand Discord server"
    environment: str = os.getenv('ENVIRONMENT', 'development')
    debug: bool = os.getenv('DEBUG', 'false').lower() == 'true'

    # Component configurations
    discord: DiscordConfig = None
    api: APIConfig = None
    database: DatabaseConfig = None
    rate_limit: RateLimitConfig = None
    logging: LoggingConfig = None
    cache: CacheConfig = None
    security: SecurityConfig = None

    def __post_init__(self):
        # Initialize component configurations if not provided
        if self.discord is None:
            self.discord = DiscordConfig(
                token=os.getenv('DISCORD_BOT_TOKEN'),
                bot_id=os.getenv('DISCORD_BOT_ID'),
                server_id=os.getenv('DISCORD_SERVER_ID'),
            )

        if self.api is None:
            self.api = APIConfig(
                weatherapi_key=os.getenv('WEATHERAPI_API_KEY'),
                currencyapi_key=os.getenv('CURRENCYAPI_API_KEY'),
                localtime_key=os.getenv('LOCALTIME_API_KEY'),
                google_api_key=os.getenv('GOOGLE_API_KEY'),
                geoapify_api_key=os.getenv('GEOAPFIY_API_KEY'),
                groq_api_key=os.getenv('GROQ_API_KEY'),
                acqin_api_key=os.getenv('ACQIN_API_KEY'),
            )

        if self.database is None:
            self.database = DatabaseConfig()

        if self.rate_limit is None:
            self.rate_limit = RateLimitConfig()

        if self.logging is None:
            self.logging = LoggingConfig()

        if self.cache is None:
            self.cache = CacheConfig()

        if self.security is None:
            self.security = SecurityConfig()


def get_config() -> AppConfig:
    """
    Get the application configuration instance.

    Returns:
                    AppConfig: The application configuration

    Raises:
                    ConfigurationError: If required configuration is missing
    """
    # Check if we're in a testing environment to be more permissive
    import os

    if os.getenv('ENVIRONMENT') == 'testing' or os.getenv('PYTEST_CURRENT_TEST'):
        # In testing mode, create config but bypass validation that would cause sys.exit
        config = AppConfig()
        return config

    try:
        config = AppConfig()
        validate_config(config)
        return config
    except Exception as e:
        print(f"Configuration error: {e}")
        sys.exit(1)


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
    # Validate Discord configuration
    if not config.discord.token:
        raise ConfigurationError(
            "Discord token is required", config_key="DISCORD_BOT_TOKEN"
        )

    # Validate API keys
    if not config.api.weatherapi_key:
        raise ConfigurationError(
            "WeatherAPI key is required", config_key="WEATHERAPI_API_KEY"
        )

    if not config.api.currencyapi_key:
        raise ConfigurationError(
            "CurrencyAPI key is required", config_key="CURRENCYAPI_API_KEY"
        )

    # Validate environment
    valid_environments = ['development', 'staging', 'production']
    if config.environment not in valid_environments:
        raise ConfigurationError(
            f"Invalid environment '{config.environment}'. Must be one of {valid_environments}",
            config_key="ENVIRONMENT",
        )

    return True


# Global configuration instance
_config: Optional[AppConfig] = None


def get_global_config() -> AppConfig:
    """
    Get the global application configuration instance.

    Returns:
                    AppConfig: The global application configuration
    """
    global _config
    if _config is None:
        _config = get_config()
    return _config


def reset_config():
    """Reset the global configuration (useful for testing)."""
    global _config
    _config = None


# Convenience functions for accessing configuration values
def get_discord_token() -> str:
    """Get the Discord bot token."""
    return get_global_config().discord.token


def get_environment() -> str:
    """Get the current environment."""
    return get_global_config().environment


def is_debug() -> bool:
    """Check if the application is running in debug mode."""
    return get_global_config().debug


def get_version() -> str:
    """Get the application version."""
    return get_global_config().version


# Predefined error message
ERROR_MESSAGE: str = "🥥 Oops, something's cracked, and it's **not** the coconut!"
