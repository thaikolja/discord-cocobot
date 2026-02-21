#  Copyright (C) 2025 by Kolja Nolte
#  kolja.nolte@gmail.com
#  ... (License header as per other files) ...

from unittest.mock import AsyncMock, patch, MagicMock
import pytest
import discord
from discord.ext import commands
from cogs.summarize import SummarizeCog, setup

# Mark all tests in this module as async
pytestmark = pytest.mark.asyncio

@pytest.fixture
def bot():
    """Mock the Discord bot."""
    bot = AsyncMock(spec=commands.Bot)
    return bot

@pytest.fixture
def cog(bot):
    """Create an instance of the SummarizeCog."""
    return SummarizeCog(bot)

@pytest.fixture
def interaction():
    """Mock the Discord interaction."""
    interaction = AsyncMock(spec=discord.Interaction)

    # Mock followup and response
    interaction.response = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.followup = AsyncMock()
    interaction.followup.send = AsyncMock()

    # Mock the channel
    # MagicMock since we need to mock an async generator for channel.history
    channel = MagicMock()

    # Provide a simple async generator helper
    async def async_generator(messages):
        for msg in messages:
            yield msg

    # Function to create an async mock history based on limit
    def mock_history(limit=25):
        # Generate generic mock messages
        msgs = []
        for i in range(limit):
            msg = MagicMock(spec=discord.Message)
            msg.author.display_name = f"User{i}"
            msg.clean_content = f"Message {i}"
            msgs.append(msg)
        return async_generator(msgs)

    channel.history = MagicMock(side_effect=mock_history)
    interaction.channel = channel

    return interaction

async def test_setup(bot):
    """Test the setup function to ensure the cog is added correctly."""
    await setup(bot)
    bot.add_cog.assert_called_once()
    args, _ = bot.add_cog.call_args
    assert isinstance(args[0], SummarizeCog)

@patch('cogs.summarize.UseAI')
async def test_summarize_command_success(MockUseAI, cog, interaction):
    """Test standard execution of summarize_command out of the box."""
    mock_ai_instance = MagicMock()
    # prompt is synchronous inside to_thread but to_thread makes it run in the background.
    # Just mocking prompt to return a string.
    mock_ai_instance.prompt.return_value = "This is a summary of the messages."
    cog.ai = mock_ai_instance

    # Call with default limit
    await cog.summarize_command(interaction, limit=2)

    interaction.response.defer.assert_called_once()

    # We requested limit=2, our mock history function handles this
    interaction.channel.history.assert_called_once_with(limit=2)

    mock_ai_instance.prompt.assert_called_once()
    prompt_arg = mock_ai_instance.prompt.call_args[0][0]
    # Check that transcript was formatted inside prompt
    assert "User0: Message 0" in prompt_arg

    interaction.followup.send.assert_called_once_with("This is a summary of the messages.")

@patch('cogs.summarize.UseAI')
async def test_summarize_command_no_messages(MockUseAI, cog, interaction):
    """Test behavior when history yields no messages."""
    async def empty_generator(*args, **kwargs):
        # explicitly empty
        for i in []: yield i

    interaction.channel.history.side_effect = empty_generator

    await cog.summarize_command(interaction, limit=10)

    interaction.response.defer.assert_called_once()
    interaction.followup.send.assert_called_once_with("There are no messages to summarize.")

@patch('cogs.summarize.UseAI')
async def test_summarize_command_llm_failure(MockUseAI, cog, interaction):
    """Test behavior when the AI returns None or fails to summarize."""
    mock_ai_instance = MagicMock()
    mock_ai_instance.prompt.return_value = None
    cog.ai = mock_ai_instance

    await cog.summarize_command(interaction, limit=5)

    interaction.followup.send.assert_called_once()
    args = interaction.followup.send.call_args[0][0]
    assert "failed to generate a summary" in args

@patch('cogs.summarize.UseAI')
async def test_summarize_command_history_forbidden(MockUseAI, cog, interaction):
    """Test behavior when reading message history throws Forbidden error."""
    interaction.channel.history.side_effect = discord.errors.Forbidden(MagicMock(), 'Forbidden')

    await cog.summarize_command(interaction, limit=5)

    interaction.followup.send.assert_called_once()
    args = interaction.followup.send.call_args[0][0]
    assert "permission to read the message history" in args
