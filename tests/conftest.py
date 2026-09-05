#  Copyright (C) 2025 by Kolja Nolte
#  kolja.nolte@gmail.com
#  https://gitlab.com/thailand-discord/bots/cocobot
#
#  This work is licensed under the MIT License. You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
#  and to permit persons to whom the Software is furnished to do so, subject to the condition that the above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  For more information, visit: https://opensource.org/licenses/MIT
#
#  Author:    Kolja Nolte
#  Email:     kolja.nolte@gmail.com
#  License:   MIT
#  Date:      2014-2025
#  Package:   cocobot Discord Bot

# Fake Discord hard enough that tests never actually log in
from unittest.mock import AsyncMock, MagicMock, patch

# The library we pretend to speak
import discord

# pytest is the only adult in this room
import pytest

# Prefix bots without the full gateway circus
from discord.ext import commands


# Session-wide: never let Cocobot.run phone home
@pytest.fixture(autouse=True, scope='session')
def mock_discord_bot_run():
    """
    Automatically mock the bot.run method for all tests to prevent
    the bot from actually starting and connecting to Discord.
    """
    # Patch the coconut's ignition switch
    with patch('bot.Cocobot.run') as mock_run:

        # Hand the mock to whoever asked
        yield mock_run


# Session-wide: login is a costume, not a credential
@pytest.fixture(autouse=True, scope='session')
def mock_discord_login():
    """
    Mock discord login to prevent actual connection attempts.
    """
    # Client.login stays on the porch
    with patch('discord.client.Client.login', new_callable=MagicMock) as mock_login:

        # Tests may inspect this if they get nosy
        yield mock_login


# Session-wide: no websocket, no tears
@pytest.fixture(autouse=True, scope='session')
def mock_discord_connect():
    """
    Mock discord connection to prevent actual websocket connections.
    """
    # Gateway handshake, but make it imaginary
    with patch('discord.client.Client.connect', new_callable=MagicMock) as mock_connect:

        # Yield the dummy socket
        yield mock_connect


# Session-wide: logging setup would just shout into /dev/null anyway
@pytest.fixture(autouse=True, scope='session')
def mock_logging_setup():
    """
    Mock logging setup to prevent any logging configuration during tests.
    """
    # Don't reconfigure loggers for every coconut
    with patch('utils.logger.setup_logging') as mock_setup:

        # Tests can still assert it was "called"
        yield mock_setup


# Session-wide: slash-command sync is a paid API hobby
@pytest.fixture(autouse=True, scope='session')
def mock_bot_tree_sync():
    """
    Mock the bot's command tree sync to prevent actual API calls.
    """
    # CommandTree.sync is async and expensive; we do neither
    with patch(
        'discord.app_commands.CommandTree.sync', new_callable=AsyncMock
    ) as mock_sync:

        # Give tests the fake sync
        yield mock_sync


# Per-test bot that thinks it is real
@pytest.fixture
def mock_bot():
    """
    Create a properly initialized mock bot for testing cogs.
    """
    # Prefix "!" because tradition, not because anyone types it
    bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

    # Internals Discord would fill in; we lie instead
    bot._connection = MagicMock()

    # Intents live on the fake connection too
    bot._connection.intents = discord.Intents.default()

    # Ship the bot to the cog under test
    return bot


# Shared aiohttp session faker so each cog test doesn't reinvent HTTP
def build_mock_aiohttp_session(mock_session_class, json_payload, status=200):
    """Configure a patched aiohttp.ClientSession mock to return json_payload on .get().

    Usage: call inside a test that has @patch('<cog>.aiohttp.ClientSession') as
    the outermost aiohttp patch; pass the patch mock and the dict the API should
    return.
    """
    # Session object tests will `async with`
    mock_session = MagicMock()

    # Response object hiding inside that session
    mock_response = MagicMock()

    # Entering the session returns itself, like a hall of mirrors
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)

    # Exiting does nothing useful, which is the point
    mock_session.__aexit__ = AsyncMock(return_value=None)

    # HTTP status the API "returned"
    mock_response.status = status

    # JSON body the coconut will parse
    mock_response.json = AsyncMock(return_value=json_payload)

    # Response is also an async context manager because aiohttp said so
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)

    # Leave the response without drama
    mock_response.__aexit__ = AsyncMock(return_value=None)

    # GET just hands back the pre-cooked response
    mock_session.get = MagicMock(return_value=mock_response)

    # Constructor of ClientSession now yields our puppet
    mock_session_class.return_value = mock_session

    # Caller may want the session mock
    return mock_session


# Wipe visa reminders so tests don't inherit yesterday's panic
@pytest.fixture(autouse=True)
def cleanup_visa_reminders():
    """
    Clean up visa reminder entries in the database before each test to ensure test isolation.
    """
    # Late import so conftest doesn't explode if the DB module is mid-refactor
    from utils.database import VisaReminder, get_db_session, init_db

    # Tables first, questions later
    init_db()

    # Empty the reminder table before the test runs
    with next(get_db_session()) as db:

        # Delete every visa row; isolation is not optional
        db.query(VisaReminder).delete()

        # Persist the emptiness
        db.commit()

    # Test body lives here
    yield  # This is where the test runs

    # And mop up afterward in case someone left souvenirs
    with next(get_db_session()) as db:

        # Same delete, different moment
        db.query(VisaReminder).delete()

        # Commit the second wipe
        db.commit()
