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
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import discord
from discord.ext import commands
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot import Cocobot, INITIAL_EXTENSIONS
from config.config import COCOBOT_VERSION


@pytest.fixture
def bot():
    """Create a bot instance for testing."""
    with patch('bot.DISCORD_BOT_TOKEN', 'test_token'), \
         patch('bot.DISCORD_SERVER_ID', '123456789'), \
         patch('bot.COCOBOT_VERSION', '1.0.0'):
        
        bot_instance = Cocobot()
        
        # Create a mock user for the bot
        mock_user = Mock()
        mock_user.id = 999888777
        mock_user.name = "Cocobot"
        mock_user.__str__ = lambda self: "Cocobot"
        mock_user.display_avatar = Mock()
        mock_user.display_avatar.url = "https://example.com/avatar.png"
        
        # Patch the user property of the bot
        with patch.object(bot_instance.__class__, 'user', property(lambda self: mock_user)):
            yield bot_instance


@pytest.fixture
def mock_user():
    """Create a mock Discord user."""
    user = Mock(spec=discord.User)
    user.id = 123456789
    user.name = "TestUser"
    user.mention = "<@123456789>"
    user.display_avatar = Mock()
    user.display_avatar.url = "https://example.com/avatar.png"
    return user


@pytest.fixture
def mock_guild():
    """Create a mock Discord guild."""
    guild = Mock(spec=discord.Guild)
    guild.id = 987654321
    guild.name = "Test Guild"
    return guild


@pytest.fixture
def mock_channel():
    """Create a mock Discord channel."""
    channel = Mock(spec=discord.TextChannel)
    channel.id = 555666777
    channel.name = "general"
    channel.send = AsyncMock()
    return channel


@pytest.fixture
def mock_message(mock_user, mock_channel):
    """Create a mock Discord message."""
    message = Mock(spec=discord.Message)
    message.author = mock_user
    message.channel = mock_channel
    message.content = "Hello"
    message.mentions = []  # This should be a list to be iterable
    return message


@pytest.fixture
def mock_interaction():
    """Create a mock Discord interaction."""
    interaction = Mock(spec=discord.Interaction)
    interaction.user = Mock()
    interaction.user.id = 123456789
    interaction.response = AsyncMock()
    interaction.followup = AsyncMock()
    interaction.response.is_done = Mock(return_value=False)
    return interaction


class TestBotInitialization:
    """Test bot initialization and configuration."""
    
    def test_bot_version(self, bot):
        """Test that bot version is set correctly."""
        assert bot.version == COCOBOT_VERSION
    
    def test_bot_intents(self, bot):
        """Test that bot intents are configured correctly."""
        assert bot.intents.members is True
        assert bot.intents.message_content is True
    
    def test_bot_prefix(self, bot):
        """Test that bot command prefix is set correctly."""
        assert bot.command_prefix == '!'
    
    def test_initial_cooldowns(self, bot):
        """Test that cooldown tracking structures are initialized."""
        assert isinstance(bot.tate_cooldowns, dict)
        assert len(bot.tate_cooldowns) == 0
    
    def test_initial_reminded_users(self, bot):
        """Test that reminded users set is initialized."""
        assert isinstance(bot.reminded_users, set)
        assert len(bot.reminded_users) == 0


class TestSetupHook:
    """Test the setup hook functionality."""
    
    @pytest.mark.asyncio
    async def test_setup_hook_loads_extensions(self, bot):
        """Test that setup_hook loads all initial extensions."""
        with patch.object(bot, 'load_extension') as mock_load, \
             patch.object(bot.tree, 'copy_global_to') as mock_copy, \
             patch.object(bot.tree, 'sync') as mock_sync:
            
            await bot.setup_hook()
            
            # Verify that load_extension was called for each initial extension
            assert mock_load.call_count == len(INITIAL_EXTENSIONS)
            for extension in INITIAL_EXTENSIONS:
                mock_load.assert_any_call(extension)
    
    @pytest.mark.asyncio
    async def test_setup_hook_syncs_commands(self, bot):
        """Test that setup_hook syncs commands to the guild."""
        with patch.object(bot, 'load_extension'), \
             patch.object(bot.tree, 'copy_global_to') as mock_copy, \
             patch.object(bot.tree, 'sync') as mock_sync:
            
            await bot.setup_hook()
            
            # Verify that commands were synced
            mock_copy.assert_called_once()
            mock_sync.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_setup_hook_extension_load_failure(self, bot):
        """Test that setup_hook handles extension load failures gracefully."""
        with patch.object(bot, 'load_extension', side_effect=Exception("Load failed")), \
             patch.object(bot.tree, 'copy_global_to'), \
             patch.object(bot.tree, 'sync'):
            
            # Should not raise an exception
            await bot.setup_hook()


class TestOnReady:
    """Test the on_ready event handler."""
    
    @pytest.mark.asyncio
    async def test_on_ready_logs_info(self, bot, mock_guild):
        """Test that on_ready logs the correct information."""
        # Create a mock user
        mock_user = Mock()
        mock_user.name = "Cocobot"
        mock_user.id = 999888777
        mock_user.__str__ = lambda self: "Cocobot"  # Make the string representation return the name
        
        # Patch the user and guilds properties of the bot instance using PropertyMock
        with patch.object(bot.__class__, 'user', property(lambda self: mock_user)), \
             patch.object(bot.__class__, 'guilds', property(lambda self: [mock_guild])):
            
            with patch('utils.logger.bot_logger.info') as mock_logger:
                await bot.on_ready()
                
                # Verify that bot ready message was logged
                mock_logger.assert_called()
                call_args = ' '.join([str(call) for call in mock_logger.call_args_list])
                assert "Cocobot is ready" in call_args
                assert "999888777" in call_args


class TestOnMessage:
    """Test the on_message event handler."""
    
    @pytest.mark.asyncio
    async def test_on_message_bot_self_ignore(self, bot, mock_message):
        """Test that bot ignores messages from itself."""
        mock_message.author = bot.user
        
        with patch.object(bot, 'process_commands') as mock_process:
            await bot.on_message(mock_message)
            
            # Verify that process_commands was not called
            mock_process.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_on_message_visa_channel_reminder(self, bot, mock_message):
        """Test visa channel nationality reminder functionality."""
        mock_message.channel.name = "visa"
        mock_message.content = "How to get visa?"
        mock_message.author.id = 111222333
        
        with patch.object(bot, 'process_commands'):
            await bot.on_message(mock_message)
            
            # Verify that reminder was sent
            mock_message.channel.send.assert_awaited_once()
            call_args = mock_message.channel.send.call_args[0][0]
            assert "mention your nationality" in call_args
            assert mock_message.author.mention in call_args
            
            # Verify user was added to reminded set
            assert 111222333 in bot.reminded_users
    
    @pytest.mark.asyncio
    async def test_on_message_cocobot_command(self, bot, mock_message):
        """Test !cocobot command response."""
        mock_message.content = "!cocobot"
        
        with patch.object(bot, 'process_commands'):
            await bot.on_message(mock_message)
            
            # Verify that embed was sent
            mock_message.channel.send.assert_awaited_once()
            call_args = mock_message.channel.send.call_args[1]
            assert 'embed' in call_args
            embed = call_args['embed']
            assert embed.title == "🥥 Cocobot at your service!"
            # The bot is initialized with the mocked COCOBOT_VERSION in the fixture
            assert "1.0.0" in embed.description  # Using the mocked version
    
    @pytest.mark.asyncio
    async def test_on_message_cocobot_mention(self, bot, mock_message):
        """Test bot mention response."""
        mock_message.content = "Hello @Cocobot"
        mock_bot_user = Mock()
        mock_bot_user.id = bot.user.id
        mock_message.mentions = [mock_bot_user]
        
        with patch.object(bot, 'process_commands'):
            await bot.on_message(mock_message)
            
            # Verify that embed was sent
            mock_message.channel.send.assert_awaited_once()
            call_args = mock_message.channel.send.call_args[1]
            assert 'embed' in call_args
    
    @pytest.mark.asyncio
    async def test_on_message_tate_trigger(self, bot, mock_message):
        """Test 'tate' word trigger."""
        mock_message.content = "Look at this tate photo"
        mock_message.author.id = 444555666
        
        with patch.object(bot, 'process_commands'), \
             patch('bot.datetime') as mock_datetime:
            
            mock_datetime.now.return_value = Mock()
            mock_datetime.timedelta = Mock(return_value=Mock())
            
            await bot.on_message(mock_message)
            
            # Verify that embed with GIF was sent
            mock_message.channel.send.assert_awaited_once()
            call_args = mock_message.channel.send.call_args[1]
            assert 'embed' in call_args
            embed = call_args['embed']
            assert 'tenor.gif' in embed.image.url
    
    @pytest.mark.asyncio
    async def test_on_message_tate_cooldown(self, bot, mock_message):
        """Test 'tate' cooldown functionality."""
        from datetime import datetime, timedelta
        
        mock_message.content = "tate"
        mock_message.author.id = 444555666
        
        # Set up cooldown
        recent_time = datetime.now() - timedelta(minutes=1)
        bot.tate_cooldowns[444555666] = recent_time
        
        with patch.object(bot, 'process_commands'):
            await bot.on_message(mock_message)
            
            # Verify that cooldown message was sent
            mock_message.channel.send.assert_awaited_once()
            call_args = mock_message.channel.send.call_args[0][0]
            assert "needs a 5-minute break" in call_args
    
    @pytest.mark.asyncio
    async def test_on_message_nal_mention(self, bot, mock_message):
        """Test @Nal mention response."""
        mock_message.content = "Thanks @Nal for the help"
        
        nal_user = Mock()
        nal_user.name = "nal_9345"
        mock_message.mentions = [nal_user]
        
        with patch.object(bot, 'process_commands'):
            await bot.on_message(mock_message)
            
            # Verify that embed with image was sent
            mock_message.channel.send.assert_awaited_once()
            call_args = mock_message.channel.send.call_args[1]
            assert 'embed' in call_args
            embed = call_args['embed']
            assert 'nal.avif' in embed.image.url
    
    @pytest.mark.asyncio
    async def test_on_message_normal_processing(self, bot, mock_message):
        """Test normal message processing."""
        mock_message.content = "Hello everyone"
        
        with patch.object(bot, 'process_commands') as mock_process:
            await bot.on_message(mock_message)
            
            # Verify that process_commands was called
            mock_process.assert_awaited_once_with(mock_message)


class TestCommandErrorHandling:
    """Test command error handling."""
    
    @pytest.mark.asyncio
    async def test_on_command_error_command_not_found(self, bot):
        """Test CommandNotFound error handling."""
        ctx = Mock()
        ctx.command = "nonexistent"
        ctx.author = "TestUser"
        ctx.send = AsyncMock()
        
        error = commands.CommandNotFound("Command not found")
        
        with patch('utils.logger.command_logger.warning') as mock_logger:
            await bot.on_command_error(ctx, error)
            
            # Verify error message was sent
            ctx.send.assert_awaited_once()
            call_args = ctx.send.call_args[0][0]
            assert "Command 'nonexistent' not found" in call_args
            
            # Verify error was logged
            mock_logger.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_on_command_error_missing_required_argument(self, bot):
        """Test MissingRequiredArgument error handling."""
        ctx = Mock()
        ctx.command = "test"
        ctx.send = AsyncMock()
        
        error = commands.MissingRequiredArgument(Mock())
        error.param.name = "location"
        
        with patch('utils.logger.command_logger.warning'):
            await bot.on_command_error(ctx, error)
            
            # Verify error message was sent
            ctx.send.assert_awaited_once()
            call_args = ctx.send.call_args[0][0]
            assert "Missing required argument: location" in call_args
    
    @pytest.mark.asyncio
    async def test_on_command_error_bad_argument(self, bot):
        """Test BadArgument error handling."""
        ctx = Mock()
        ctx.command = "test"
        ctx.send = AsyncMock()
        
        error = commands.BadArgument("Invalid argument")
        
        with patch('utils.logger.command_logger.warning'):
            await bot.on_command_error(ctx, error)
            
            # Verify error message was sent
            ctx.send.assert_awaited_once()
            call_args = ctx.send.call_args[0][0]
            assert "Invalid argument provided" in call_args
    
    @pytest.mark.asyncio
    async def test_on_command_error_command_on_cooldown(self, bot):
        """Test CommandOnCooldown error handling."""
        ctx = Mock()
        ctx.command = "test"
        ctx.author = "TestUser"
        ctx.send = AsyncMock()
        
        # CommandOnCooldown requires rate, per, and type parameters
        from discord.ext.commands import BucketType
        error = commands.CommandOnCooldown(1, 30.5, BucketType.user)
        
        with patch('utils.logger.command_logger.info'):
            await bot.on_command_error(ctx, error)
            
            # Verify cooldown message was sent
            ctx.send.assert_awaited_once()
            call_args = ctx.send.call_args[0][0]
            assert "This command is on cooldown" in call_args
            assert "30.50" in call_args
    
    @pytest.mark.asyncio
    async def test_on_command_error_unhandled_error(self, bot):
        """Test unhandled error handling."""
        ctx = Mock()
        ctx.command = "test"
        ctx.send = AsyncMock()
        
        error = Exception("Something went wrong")
        
        with patch('utils.logger.error_logger.error') as mock_logger:
            await bot.on_command_error(ctx, error)
            
            # Verify error message was sent
            ctx.send.assert_awaited_once()
            call_args = ctx.send.call_args[0][0]
            assert "Oops, something's cracked" in call_args
            
            # Verify error was logged
            mock_logger.assert_called_once()


class TestAppCommandErrorHandling:
    """Test application command (slash command) error handling."""
    
    @pytest.mark.asyncio
    async def test_on_app_command_error_with_response(self, bot, mock_interaction):
        """Test app command error handling when response is not done."""
        error = Exception("App command error")
        
        with patch('utils.logger.error_logger.error') as mock_logger:
            await bot.on_app_command_error(mock_interaction, error)
            
            # Verify error message was sent
            mock_interaction.response.send_message.assert_awaited_once()
            call_args = mock_interaction.response.send_message.call_args[0][0]
            assert "Oops, something's cracked" in call_args
            
            # Verify error was logged
            mock_logger.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_on_app_command_error_with_followup(self, bot, mock_interaction):
        """Test app command error handling when response is already done."""
        mock_interaction.response.is_done.return_value = True
        error = Exception("App command error")
        
        with patch('utils.logger.error_logger.error'):
            await bot.on_app_command_error(mock_interaction, error)
            
            # Verify error message was sent via followup
            mock_interaction.followup.send.assert_awaited_once()
            call_args = mock_interaction.followup.send.call_args[0][0]
            assert "Oops, something's cracked" in call_args


class TestBotRun:
    """Test bot run functionality."""
    
    def test_bot_run_calls_parent_run(self):
        """Test that bot.run calls the parent class run method."""
        with patch('bot.DISCORD_BOT_TOKEN', 'test_token'), \
             patch('bot.DISCORD_SERVER_ID', '123456789'), \
             patch('bot.COCOBOT_VERSION', '1.0.0'), \
             patch.object(commands.Bot, 'run') as mock_run:
            
            bot_instance = Cocobot()
            bot_instance.run()  # This should be called with the token from config
            
            # Verify that parent run was called with the token
            mock_run.assert_called_once_with('test_token')
