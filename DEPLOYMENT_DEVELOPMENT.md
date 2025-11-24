# Development Deployment Guide

This guide provides step-by-step instructions for setting up a development environment for the Discord bot.

## Prerequisites

- Operating System: Windows, macOS, or Linux
- Python 3.8 or higher
- Git
- A Discord application and bot token
- API keys for all required services

## Step 1: Clone the Repository

### 1.1 Open terminal/command prompt
For Windows: Open Command Prompt or PowerShell
For macOS/Linux: Open Terminal

### 1.2 Clone the repository
```bash
git clone https://github.com/yourusername/cocobot.git
cd cocobot
```

## Step 2: Python Environment Setup

### 2.1 Check Python version
```bash
python --version
# or
python3 --version
```
> Make sure you have Python 3.8 or higher

### 2.2 Create virtual environment
```bash
# On Windows
python -m venv venv
# On macOS/Linux
python3 -m venv venv
```

### 2.3 Activate virtual environment
```bash
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 2.4 Upgrade pip
```bash
python -m pip install --upgrade pip
```

## Step 3: Install Dependencies

### 3.1 Install required packages
```bash
pip install -r requirements.txt
```

### 3.2 (Optional) Install development dependencies
```bash
pip install pytest pytest-asyncio black flake8 mypy
```

## Step 4: Configuration

### 4.1 Create environment file
```bash
# On Windows
copy .env.example .env
# On macOS/Linux
cp .env.example .env
```

### 4.2 Edit the environment file
```bash
# On Windows (use Notepad or any text editor)
notepad .env
# On macOS
open -e .env
# On Linux (using nano)
nano .env
```

### 4.3 Fill in the environment variables:
- `DISCORD_BOT_TOKEN=` - Your Discord bot token
- `WEATHERAPI_API_KEY=` - WeatherAPI key
- `CURRENCYAPI_API_KEY=` - CurrencyAPI key
- `LOCALTIME_API_KEY=` - LocalTime API key
- `GOOGLE_API_KEY=` - Google API key
- `GOOGLE_MAPS_API_KEY=` - Google Maps API key
- `GEOAPFIY_API_KEY=` - Geoapify API key
- `ACQIN_API_KEY=` - AcqIn API key
- `GROQ_API_KEY=` - Groq API key
- `SAMBANOVA_API_KEY=` - Sambanova API key
- `DISCORD_SERVER_ID=` - Your Discord server ID
- `DISCORD_BOT_ID=` - Your Discord bot ID
- `ENVIRONMENT=development`
- `LOG_LEVEL=DEBUG` (for development)

> **Note**: You can find your Discord bot token in the Discord Developer Portal under your application's Bot section.

## Step 5: Database Setup (Optional for Development)

### 5.1 For development, you can use SQLite (default)
- No additional setup needed, uses `cocobot.db` file
- Perfect for local development

### 5.2 For PostgreSQL (optional advanced setup)
- Install PostgreSQL locally
- Update `DATABASE_URL` in `.env` to point to your PostgreSQL instance
- Install PostgreSQL client: `pip install psycopg2-binary`

## Step 6: Redis Setup (Optional for Development)

### 6.1 For development, you can skip Redis (the bot will use in-memory cache)
- The bot automatically falls back to in-memory cache if Redis is unavailable

### 6.2 To use Redis in development:
- Install Redis locally
- Update `REDIS_URL` in `.env` to point to your Redis instance
- On macOS: `brew install redis && brew services start redis`
- On Ubuntu: `sudo apt install redis-server && sudo systemctl start redis-server`

## Step 7: Running the Bot

### 7.1 Ensure virtual environment is activated
```bash
# Verify activation - you should see (venv) at the beginning of your prompt
```

### 7.2 Run the bot
```bash
python bot.py
```

### 7.3 Add the bot to your server
1. Go to Discord Developer Portal
2. Navigate to your application
3. Go to OAuth2 > URL Generator
4. Select "bot" scope
5. Select required permissions (e.g., "Send Messages", "View Channels", etc.)
6. Copy the generated URL and open in browser
7. Add the bot to your Discord server

### 7.4 Test the bot
- The bot should appear online in your server
- Try using a command like `/weather` in a text channel

## Step 8: Development Tools

### 8.1 Run tests
```bash
# Run all tests
python -m pytest tests/

# Run tests in verbose mode
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=cogs --cov=utils --cov-report=html
```

### 8.2 Code formatting
```bash
# Format code with black
black .

# Check formatting with flake8
flake8 .
```

### 8.3 Type checking (if using mypy)
```bash
mypy .
```

## Step 9: Development Workflow

### 9.1 Making changes
1. Stop the bot (Ctrl+C in the terminal)
2. Make your code changes
3. Restart the bot: `python bot.py`

### 9.2 Adding new dependencies
1. Install the package: `pip install package_name`
2. Update requirements.txt: `pip freeze > requirements.txt`
3. Commit the updated requirements.txt

## Step 10: Common Development Tasks

### 10.1 Adding a new command
1. Create a new file in the `cogs/` directory
2. Follow the pattern in existing cogs
3. Add the cog to `bot.py`'s `INITIAL_EXTENSIONS`

### 10.2 Debugging
- Set `LOG_LEVEL=DEBUG` in your `.env` file
- Check the logs in the console output
- Use Python debugging tools if needed

### 10.3 Testing new features
1. Create a test file in the `tests/` directory
2. Follow existing test patterns
3. Run your specific tests: `python -m pytest tests/your_test_file.py -v`

## Troubleshooting

### Bot won't start
- Verify virtual environment is activated
- Check that `.env` file contains all required variables
- Verify Python version is 3.8 or higher
- Look for error messages in the console

### Dependency installation fails
- Update pip: `python -m pip install --upgrade pip`
- Try installing packages individually
- Check for platform-specific issues

### Commands not showing up in Discord
- Wait a few minutes as Discord may cache commands
- Restart the bot to force command sync
- Check that the bot has proper permissions

### API requests failing
- Verify all API keys in `.env` are correct
- Check API service status
- Look at rate limiting for the services

### Error: "ImportError" or missing modules
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version compatibility

## Tips for Development

- Set `LOG_LEVEL=DEBUG` during development for more detailed logs
- Use the SQLite database for simple development setups
- Regularly run tests to ensure no regressions
- Follow the existing code style and patterns
- Test commands in a private Discord server during development
- Use version control (git) to track your changes
- Keep dependencies updated but test thoroughly after updates