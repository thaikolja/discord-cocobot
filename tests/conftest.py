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

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import discord
from discord.ext import commands


@pytest.fixture(autouse=True, scope='session')
def mock_discord_bot_run():
    """
    Automatically mock the bot.run method for all tests to prevent
    the bot from actually starting and connecting to Discord.
    """
    with patch('bot.Cocobot.run') as mock_run:
        yield mock_run


@pytest.fixture(autouse=True, scope='session')
def mock_discord_login():
    """
    Mock discord login to prevent actual connection attempts.
    """
    with patch('discord.client.Client.login', new_callable=MagicMock) as mock_login:
        yield mock_login


@pytest.fixture(autouse=True, scope='session')
def mock_discord_connect():
    """
    Mock discord connection to prevent actual websocket connections.
    """
    with patch('discord.client.Client.connect', new_callable=MagicMock) as mock_connect:
        yield mock_connect


@pytest.fixture(autouse=True, scope='session')
def mock_logging_setup():
    """
    Mock logging setup to prevent any logging configuration during tests.
    """
    with patch('utils.logger.setup_logging') as mock_setup:
        yield mock_setup


@pytest.fixture(autouse=True, scope='session')
def mock_bot_tree_sync():
    """
    Mock the bot's command tree sync to prevent actual API calls.
    """
    with patch('discord.app_commands.CommandTree.sync', new_callable=AsyncMock) as mock_sync, \
         patch('discord.app_commands.CommandTree.copy_global_to', new_callable=MagicMock) as mock_copy:
        yield mock_sync



@pytest.fixture
def mock_bot():
    """
    Create a properly initialized mock bot for testing cogs.
    """
    # Create a bot with mocked internals
    bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
    
    # Mock the internal connection to prevent actual Discord connection
    bot._connection = MagicMock()
    bot._connection.intents = discord.Intents.default()
    
    return bot



