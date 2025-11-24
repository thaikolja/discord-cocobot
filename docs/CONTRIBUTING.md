# Contributing to Cocobot

We welcome contributions to the Cocobot Discord bot! This guide will help you get started with contributing to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Testing](#testing)
- [Bug Reports](#bug-reports)
- [Feature Requests](#feature-requests)
- [Community](#community)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A Discord account and developer application
- Basic knowledge of Python and Discord bots

### Fork and Clone

1. Fork the repository on GitLab
2. Clone your fork locally:
```bash
git clone https://gitlab.com/yourusername/cocobot.git
cd cocobot
```

3. Add the original repository as upstream:
```bash
git remote add upstream https://gitlab.com/thailand-discord/bots/cocobot.git
```

## Development Setup

### 1. Set up the Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit the file with your configuration
# You'll need Discord bot token and API keys for testing
```

### 3. Run Tests

```bash
# Run the test suite
pytest tests/

# Run with coverage
pytest tests/ --cov=cogs --cov=utils --cov-report=html
```

### 4. Run the Bot

```bash
python bot.py
```

## Code Style

We follow Python's PEP 8 style guide with some additional conventions:

### Formatting

- Use Black for code formatting: `black .`
- Maximum line length: 88 characters
- Use f-strings for string formatting
- Prefer type hints where appropriate

### Naming Conventions

- **Variables and functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`
- **Special methods**: `__dunder_methods__`

### Documentation

- Use docstrings for all public functions and classes
- Follow Google-style docstring format
- Include type hints in function signatures
- Add inline comments for complex logic

```python
def process_weather_data(location: str) -> WeatherData:
    """Process weather data for a given location.
    
    Args:
        location: The location to get weather data for.
        
    Returns:
        WeatherData object with processed weather information.
        
    Raises:
        APIError: If the weather API request fails.
    """
    # Implementation here
```

## Submitting Changes

### 1. Create a Branch

```bash
# Create a new branch for your feature
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

### 2. Make Your Changes

- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### 3. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a clear message
git commit -m "feat: add new weather command feature"

# Use conventional commit messages:
# feat: new feature
# fix: bug fix
# docs: documentation changes
# style: formatting changes
# refactor: code refactoring
# test: test changes
# chore: maintenance tasks
```

### 4. Push and Create Merge Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create a merge request on GitLab
# Target the main branch from the original repository
```

## Testing

### Writing Tests

- Place tests in the `tests/` directory
- Name test files as `test_*.py`
- Use pytest conventions
- Test both positive and negative cases

### Test Structure

```python
import pytest
from unittest.mock import AsyncMock, patch
from cogs.weather import WeatherCog

class TestWeatherCog:
    def setup_method(self):
        """Set up test fixtures."""
        self.bot = AsyncMock()
        self.cog = WeatherCog(self.bot)
    
    async def test_weather_command_success(self):
        """Test successful weather command."""
        # Test implementation
        pass
    
    async def test_weather_command_invalid_location(self):
        """Test weather command with invalid location."""
        # Test implementation
        pass
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_weather.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=cogs --cov=utils --cov-report=html
```

### Test Coverage

- Aim for >80% code coverage
- Focus on critical paths and edge cases
- Mock external API calls
- Test error conditions

## Bug Reports

### Before Reporting

1. Check existing issues for duplicates
2. Try the latest version of the bot
3. Check if the issue is environment-specific

### Reporting a Bug

1. Use the issue template in GitLab
2. Provide clear and concise description
3. Include steps to reproduce
4. Add environment information
5. Include relevant logs or screenshots

### Bug Report Template

```markdown
**Bug Description**
A clear and concise description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear description of what you expected to happen.

**Actual Behavior**
A clear description of what actually happened.

**Environment**
- OS: [e.g. Windows 10, macOS 11.0, Ubuntu 20.04]
- Python version: [e.g. 3.9.0]
- Bot version: [e.g. 2.3.0]

**Additional Context**
Add any other context about the problem here.
```

## Feature Requests

### Requesting Features

1. Check if the feature already exists
2. Look for similar feature requests
3. Use the feature request template

### Feature Request Template

```markdown
**Feature Description**
A clear and concise description of the feature you'd like to add.

**Use Case**
Describe why this feature would be useful and how you would use it.

**Proposed Solution**
If you have ideas on how to implement this feature, describe them here.

**Alternatives Considered**
Describe any alternative solutions or features you've considered.

**Additional Context**
Add any other context or screenshots about the feature request here.
```

## Development Guidelines

### Adding New Commands

1. Create a new cog or add to an existing one
2. Use discord.py's slash commands (`@app_commands.command`)
3. Include proper error handling
4. Add comprehensive tests
5. Update documentation

### Adding Dependencies

1. Add to `requirements.txt`
2. Update the import statements
3. Document the new dependency
4. Ensure it's compatible with existing code

### Database Changes

1. Create migration scripts if needed
2. Update the database models
3. Add tests for database operations
4. Document the schema changes

## Code Review Process

### What We Look For

- Code follows style guidelines
- Tests are comprehensive
- Documentation is updated
- No breaking changes without discussion
- Security considerations are addressed

### Review Guidelines

- Be constructive and respectful
- Focus on the code, not the person
- Provide specific suggestions
- Ask questions if something is unclear
- Acknowledge good work

## Community

### Getting Help

- Join our Discord server
- Ask questions in the appropriate channels
- Check the documentation first
- Search existing issues

### Communication

- Be respectful and inclusive
- Help others when you can
- Share knowledge and experiences
- Follow the code of conduct

## Recognition

Contributors are recognized in several ways:

- Contributor list in README
- Changelog mentions for significant contributions
- Special roles in Discord community
- Opportunities for maintainership

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

## Questions?

If you have questions about contributing, feel free to:

- Create an issue with the "question" label
- Ask in our Discord server
- Contact the maintainers directly

Thank you for contributing to Cocobot! 🥥