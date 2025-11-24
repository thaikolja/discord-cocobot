# Cocobot Developer Guide

## Overview

This guide provides comprehensive information for developers looking to contribute to or modify the Cocobot Discord bot. The bot is built using Python and the discord.py library, with additional utilities for configuration, logging, security, and monitoring.

## Project Structure

```
cocobot/
├── bot.py                  # Main application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore patterns
├── README.md             # Main project documentation
├── API_DOCUMENTATION.md  # API reference
├── CHANGELOG.md          # Release history
├── deploy.sh            # Deployment script
├── config/              # Configuration management
│   ├── __init__.py
│   └── app_config.py    # Advanced configuration system
├── cogs/                # Command modules
│   ├── __init__.py
│   ├── exchangerate.py
│   ├── learn.py
│   ├── pollution.py
│   ├── time.py
│   ├── translate.py
│   ├── transliterate.py
│   └── weather.py
├── utils/               # Utility functions
│   ├── __init__.py
│   ├── database.py      # Database models and ORM
│   ├── exceptions.py    # Custom exception classes
│   ├── helpers.py       # Helper functions
│   ├── logger.py        # Logging configuration
│   ├── rate_limit.py    # Rate limiting implementation
│   ├── security.py      # Security utilities
│   └── monitoring.py    # Monitoring and metrics
├── tests/               # Test suite
│   ├── __init__.py
│   ├── test_exchangerate.py
│   ├── test_pollution.py
│   ├── test_time.py
│   ├── test_translate.py
│   ├── test_transliterate.py
│   └── test_weather.py
└── venv/                # Virtual environment
```

## Setting Up Development Environment

### Prerequisites

- Python 3.8 or higher
- Git
- Discord account and developer application
- API keys for required services (WeatherAPI, CurrencyAPI, etc.)

### Steps

1. Clone the repository:
```bash
git clone https://gitlab.com/thailand-discord/bots/cocobot.git
cd cocobot
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
  - On Linux/Mac: `source venv/bin/activate`
  - On Windows: `venv\Scripts\activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Set up environment variables:
```bash
cp .env.example .env
```
Edit `.env` and fill in your API keys and tokens.

6. Run the bot:
```bash
python bot.py
```

## Architecture

### Main Components

#### Bot Class (bot.py)
- Inherits from `commands.Bot`
- Handles Discord events and command processing
- Manages extension loading and command tree synchronization
- Implements global error handling

#### Cogs (cogs/)
- Modular command groups
- Each cog handles a specific feature area
- Follows discord.py's extension system
- Use `@app_commands` for slash commands

#### Configuration System (config/)
- Centralized configuration with validation
- Environment variable management
- Type-safe configuration objects
- Multiple environment support (dev, staging, prod)

#### Utilities (utils/)
- Reusable components across the application
- Logging, security, monitoring, database access
- Rate limiting and input validation

## Adding New Commands

To add a new command:

1. Create a new cog in the `cogs/` directory or add to an existing one
2. Inherit from `commands.Cog`
3. Use `@app_commands.command` for slash commands
4. Include command descriptions and parameter documentation
5. Add error handling
6. Register the cog in `bot.py`'s `INITIAL_EXTENSIONS` list
7. Import the cog in the `cogs/__init__.py` file

### Example Command Structure

```python
import discord
from discord.ext import commands
from discord import app_commands

class NewFeatureCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="newcommand", description="Description of the new command")
    @app_commands.describe(parameter="Description of the parameter")
    async def new_command(self, interaction: discord.Interaction, parameter: str = "default"):
        """Handle the new command."""
        try:
            # Command logic here
            response = f"Response for {parameter}"
            await interaction.response.send_message(response)
        except Exception as e:
            # Handle errors appropriately
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(NewFeatureCog(bot))
```

## Configuration System

The bot uses an advanced configuration system with the following features:

### Configuration Loading
- Loads from environment variables using python-dotenv
- Validates required configuration values
- Provides type-safe configuration objects
- Supports multiple environments

### Adding New Configuration

To add a new configuration option:

1. Add it to the appropriate config class in `config/app_config.py`
2. Define its type and default value
3. Include validation in `validate_config()`
4. Add it to the main `AppConfig` class

### Example Configuration Addition

```python
@dataclass
class MyNewConfig:
    feature_enabled: bool = os.getenv('FEATURE_ENABLED', 'false').lower() == 'true'
    timeout_seconds: int = int(os.getenv('FEATURE_TIMEOUT', '30'))

# In AppConfig:
class AppConfig:
    # ... other configs
    my_new: MyNewConfig = None

    def __post_init__(self):
        # ... other initializations
        if self.my_new is None:
            self.my_new = MyNewConfig()
```

## Security Best Practices

### Input Validation and Sanitization
- Always validate user inputs using `InputValidator`
- Sanitize potentially dangerous content with `InputSanitizer`
- Check for XSS, SQL injection, and command injection patterns
- Use parameterized queries for database operations

### API Security
- Never log API keys or sensitive data
- Validate and sanitize all API responses
- Implement rate limiting to prevent abuse
- Use HTTPS for all external API calls

### Discord Security
- Validate Discord IDs format
- Handle user mentions safely
- Check user permissions before executing commands
- Use ephemeral responses for sensitive information

## Error Handling and Logging

### Exception Handling
- Use custom exceptions from `utils.exceptions`
- Handle different error types appropriately
- Provide user-friendly error messages
- Log detailed errors for debugging

### Logging
- Use structured logging with different levels
- Log important events and errors
- Include context information in logs
- Use rotating log files to manage log size

### Example Error Handling

```python
from utils.exceptions import ValidationError, APIError
from utils.logger import error_logger

async def my_command(interaction, user_input):
    try:
        # Validate input
        validated_input = validate_and_sanitize_input(user_input, "text", max_length=100)
        
        # Process command
        result = await process_data(validated_input)
        
        # Send response
        await interaction.response.send_message(f"Success: {result}")
        
    except ValidationError as e:
        error_logger.warning(f"Validation error in my_command by {interaction.user.id}: {e}")
        await interaction.response.send_message(f"Invalid input: {e}", ephemeral=True)
        
    except APIError as e:
        error_logger.error(f"API error in my_command: {e}", exc_info=True)
        await interaction.response.send_message("Service temporarily unavailable", ephemeral=True)
        
    except Exception as e:
        error_logger.error(f"Unexpected error in my_command: {e}", exc_info=True)
        await interaction.response.send_message("An unexpected error occurred", ephemeral=True)
```

## Database Integration

### Models
- Use SQLAlchemy ORM for database operations
- Define models in `utils.database.py`
- Include proper relationships and constraints
- Add indexes for frequently queried fields

### Sessions
- Use `get_db_session()` context manager
- Handle database errors gracefully
- Close sessions properly

### Example Database Usage

```python
from utils.database import get_db_session, DatabaseManager

async def get_user_stats(user_id: str):
    with get_db_session() as db:
        user = DatabaseManager.get_user_by_discord_id(db, user_id)
        if not user:
            user = DatabaseManager.create_or_update_user(db, user_id, "username")
        
        # Perform other database operations
        return user
```

## Testing

### Test Structure
- Place tests in the `tests/` directory
- Name test files as `test_*.py`
- Follow pytest conventions
- Test both positive and negative cases

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_weather.py

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=cogs --cov=utils --cov-report=html
```

### Writing Tests
- Test command functionality
- Test error scenarios
- Test edge cases
- Mock external API calls
- Verify expected responses

## Monitoring and Metrics

### Adding Metrics
- Use functions from `utils.monitoring`
- Track command usage and performance
- Monitor API call success rates
- Record error counts

### Example Metrics Collection

```python
from utils.monitoring import record_command_duration, increment_command_usage

async def my_command(interaction):
    start_time = time.time()
    success = True
    
    try:
        # Command logic
        result = await perform_operation()
        await interaction.response.send_message(result)
    except Exception:
        success = False
        raise
    finally:
        # Record metrics
        duration = time.time() - start_time
        record_command_duration("my_command", duration, success)
        increment_command_usage("my_command", success)
```

## Performance Optimization

### Caching
- Use database-backed cache for API responses
- Implement TTL for cached data
- Clear expired cache entries

### Rate Limiting
- Implement multiple layers of rate limiting
- Use both in-memory and database storage
- Provide clear feedback to users when limits are reached

### Asynchronous Operations
- Use async/await for I/O operations
- Avoid blocking operations on the main thread
- Use connection pooling for database and API calls

## Deployment

### Production Deployment
1. Use environment variables for configuration
2. Set up a process manager (systemd, pm2, etc.)
3. Configure logging for production
4. Set up monitoring and alerting

### Example systemd Service

```ini
[Unit]
Description=Discord Cocobot
After=network.target

[Service]
Type=simple
User=discord-bot
Group=discord-bot
WorkingDirectory=/path/to/cocobot
Environment=ENVIRONMENT=production
ExecStart=/path/to/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Troubleshooting

### Common Issues

#### Bot Not Responding
- Check if the bot token is correct
- Verify bot has necessary permissions
- Ensure intents are enabled in Discord Developer Portal

#### API Calls Failing
- Verify API keys are correct and not expired
- Check rate limits for the API service
- Confirm network connectivity

#### Database Issues
- Check database connection string
- Verify database permissions
- Look for migration issues

### Debugging
- Enable debug logging: `LOG_LEVEL=DEBUG`
- Check application logs in `logs/` directory
- Use the monitoring system to check metrics
- Examine test results for errors

## Contributing

### Code Standards
- Follow PEP 8 style guide
- Write type hints for all functions
- Include docstrings for public functions
- Use meaningful variable names
- Keep functions focused and small

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Make your changes following the code standards
4. Write tests for new functionality
5. Update documentation as needed
6. Run the test suite to ensure no regressions
7. Submit a pull request with a clear description

### Testing Checklist
- [ ] New functionality has tests
- [ ] Existing tests pass
- [ ] Error cases are handled
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Configuration is validated

## Versioning

The bot follows semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features (backward-compatible)
- PATCH: Bug fixes (backward-compatible)

## Support

For support, please:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information
4. Include error logs and steps to reproduce

## License

This project is licensed under the MIT License - see the LICENSE file for details.