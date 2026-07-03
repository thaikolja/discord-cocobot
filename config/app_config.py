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
    Represents the configuration required for various APIs used in the application.

    Each AI-powered feature has its own fully self-contained provider configuration
    consisting of a provider name (gemini/deepseek/groq), an API key, and a model name.
    """

    # ---- Weather & time & currency (not AI) ----
    weatherapi_key: Optional[str] = None
    currencyapi_key: Optional[str] = None
    localtime_key: Optional[str] = None
    geoapify_api_key: Optional[str] = None
    acqin_api_key: Optional[str] = None

    # ---- Transliterate - primary ----
    transliterate_provider: str = 'gemini'
    transliterate_provider_api_key: Optional[str] = None
    transliterate_provider_model: str = 'models/gemini-3-flash-preview'

    # ---- Transliterate - fallback (leave provider empty to disable) ----
    transliterate_fallback_provider: str = ''
    transliterate_fallback_provider_api_key: Optional[str] = None
    transliterate_fallback_provider_model: str = ''

    # ---- Translate - primary ----
    translate_provider: str = 'deepseek'
    translate_provider_api_key: Optional[str] = None
    translate_provider_model: str = 'deepseek-v4-flash'

    # ---- Translate - fallback (leave provider empty to disable) ----
    translate_fallback_provider: str = ''
    translate_fallback_provider_api_key: Optional[str] = None
    translate_fallback_provider_model: str = ''

    # ---- Summarize - primary ----
    summarize_provider: str = 'deepseek'
    summarize_provider_api_key: Optional[str] = None
    summarize_provider_model: str = 'deepseek-v4-flash'

    # ---- Summarize - fallback (leave provider empty to disable) ----
    summarize_fallback_provider: str = ''
    summarize_fallback_provider_api_key: Optional[str] = None
    summarize_fallback_provider_model: str = ''

    _PROVIDER_FIELDS: tuple[tuple[str, ...], ...] = (
        ('transliterate_provider', 'transliterate_provider_api_key'),
        ('transliterate_fallback_provider', 'transliterate_fallback_provider_api_key'),
        ('translate_provider', 'translate_provider_api_key'),
        ('translate_fallback_provider', 'translate_fallback_provider_api_key'),
        ('summarize_provider', 'summarize_provider_api_key'),
        ('summarize_fallback_provider', 'summarize_fallback_provider_api_key'),
    )

    _VALID_PROVIDERS = {'gemini', 'deepseek', 'groq'}

    def __post_init__(self):
        import os

        if os.getenv('ENVIRONMENT') == 'testing' or os.getenv('PYTEST_CURRENT_TEST'):
            return

        required_keys = ['weatherapi_key', 'currencyapi_key']
        for key in required_keys:
            value = getattr(self, key)
            if not value:
                env_key = key.upper().replace('KEY', 'API_KEY')
                raise ConfigurationError(
                    f"Required API key {env_key} is missing. "
                    f"Please set it in your environment.",
                    config_key=env_key,
                )

    def validate_providers(self) -> list[str]:
        """Validate that all configured providers are recognised.

        Returns a list of error messages (empty = all good).
        """
        errors: list[str] = []
        for provider_field, key_field in self._PROVIDER_FIELDS:
            provider = getattr(self, provider_field, None)
            api_key = getattr(self, key_field, None)
            if provider and provider not in self._VALID_PROVIDERS:
                errors.append(
                    f"Invalid provider '{provider}' in {provider_field}. "
                    f"Must be one of {sorted(self._VALID_PROVIDERS)}."
                )
            if provider and not api_key:
                errors.append(
                    f"Missing API key {key_field} for provider '{provider}'."
                )
        return errors


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

    level: str = os.getenv('LOG_LEVEL', 'WARNING')
    file_path: str = os.getenv('LOG_FILE', 'logs/cocobot.log')
    max_bytes: int = int(os.getenv('LOG_MAX_BYTES', '1485760'))  # ~1MB
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

    version: str = "3.7.0"
    name: str = "cocobot"
    description: str = "A feature-rich Discord bot for the Thailand Discord server"
    environment: str = os.getenv('ENVIRONMENT', 'production')
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
                geoapify_api_key=os.getenv('GEOAPFIY_API_KEY'),
                acqin_api_key=os.getenv('ACQIN_API_KEY'),
                transliterate_provider=os.getenv(
                    'TRANSLITERATE_PROVIDER', 'gemini'
                ),
                transliterate_provider_api_key=os.getenv(
                    'TRANSLITERATE_PROVIDER_API_KEY'
                ),
                transliterate_provider_model=os.getenv(
                    'TRANSLITERATE_PROVIDER_MODEL', 'models/gemini-3-flash-preview'
                ),
                transliterate_fallback_provider=os.getenv(
                    'TRANSLITERATE_FALLBACK_PROVIDER', ''
                ),
                transliterate_fallback_provider_api_key=os.getenv(
                    'TRANSLITERATE_FALLBACK_PROVIDER_API_KEY'
                ),
                transliterate_fallback_provider_model=os.getenv(
                    'TRANSLITERATE_FALLBACK_PROVIDER_MODEL', ''
                ),
                translate_provider=os.getenv(
                    'TRANSLATE_PROVIDER', 'deepseek'
                ),
                translate_provider_api_key=os.getenv(
                    'TRANSLATE_PROVIDER_API_KEY'
                ),
                translate_provider_model=os.getenv(
                    'TRANSLATE_PROVIDER_MODEL', 'deepseek-v4-flash'
                ),
                translate_fallback_provider=os.getenv(
                    'TRANSLATE_FALLBACK_PROVIDER', ''
                ),
                translate_fallback_provider_api_key=os.getenv(
                    'TRANSLATE_FALLBACK_PROVIDER_API_KEY'
                ),
                translate_fallback_provider_model=os.getenv(
                    'TRANSLATE_FALLBACK_PROVIDER_MODEL', ''
                ),
                summarize_provider=os.getenv(
                    'SUMMARIZE_PROVIDER', 'deepseek'
                ),
                summarize_provider_api_key=os.getenv(
                    'SUMMARIZE_PROVIDER_API_KEY'
                ),
                summarize_provider_model=os.getenv(
                    'SUMMARIZE_PROVIDER_MODEL', 'deepseek-v4-flash'
                ),
                summarize_fallback_provider=os.getenv(
                    'SUMMARIZE_FALLBACK_PROVIDER', ''
                ),
                summarize_fallback_provider_api_key=os.getenv(
                    'SUMMARIZE_FALLBACK_PROVIDER_API_KEY'
                ),
                summarize_fallback_provider_model=os.getenv(
                    'SUMMARIZE_FALLBACK_PROVIDER_MODEL', ''
                ),
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
    valid_environments = ['development', 'production']
    if config.environment not in valid_environments:
        raise ConfigurationError(
            f"Invalid environment '{config.environment}'. Must be one of {valid_environments}",
            config_key="ENVIRONMENT",
        )

    # Validate AI provider configuration
    provider_errors = config.api.validate_providers()
    if provider_errors:
        raise ConfigurationError(
            "Invalid AI provider configuration:\n  " + "\n  ".join(provider_errors),
            config_key="AI_PROVIDERS",
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
