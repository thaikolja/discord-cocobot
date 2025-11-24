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
import json
import os
from unittest.mock import Mock, AsyncMock, patch, mock_open
import discord
from discord.ext import commands

# Import the cog to test
from cogs.learn import LearnCog
from config.config import ERROR_MESSAGE


@pytest_asyncio.fixture
async def cog():
    """Create a LearnCog instance for testing."""
    bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
    cog_instance = LearnCog(bot)
    yield cog_instance


@pytest.fixture
def mock_interaction():
    """Create a mock Discord interaction."""
    interaction = Mock()
    interaction.response = AsyncMock()
    return interaction


@pytest.fixture
def sample_vocabulary_data():
    """Sample vocabulary data for testing."""
    return [
        {
            "english": "hello",
            "thai": "สวัสดี",
            "transliteration": "sà-wàt-dee"
        },
        {
            "english": "thank you",
            "thai": "ขอบคุณ",
            "transliteration": "khàwp-khun"
        },
        {
            "english": "goodbye",
            "thai": "ลาก่อน",
            "transliteration": "laa-gòn"
        }
    ]


class TestLearnCogInitialization:
    """Test LearnCog initialization."""
    
    def test_cog_initialization(self, cog):
        """Test that the cog initializes correctly."""
        assert cog.bot is not None
        assert isinstance(cog.bot, commands.Bot)


class TestLearnCommand:
    """Test the learn command functionality."""
    
    @pytest.mark.asyncio
    async def test_learn_command_success(self, cog, mock_interaction, sample_vocabulary_data):
        """Test successful learn command execution."""
        # Mock the file operations
        with patch('os.path.isfile', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(sample_vocabulary_data))):
            
            # Mock random.choice to return a specific word
            with patch('random.choice', return_value=sample_vocabulary_data[0]):
                await cog.learn_command.callback(cog, mock_interaction)
                
                # Verify that response was sent
                mock_interaction.response.send_message.assert_awaited_once()
                
                # Get the call arguments
                call_args = mock_interaction.response.send_message.call_args[0][0]
                
                # Verify the response contains expected content
                assert '"hello"' in call_args
                assert '"สวัสดี"' in call_args
                assert '`sà-wàt-dee`' in call_args
                assert '💡' in call_args
    
    @pytest.mark.asyncio
    async def test_learn_command_file_not_found(self, cog, mock_interaction):
        """Test learn command when vocabulary file is not found."""
        with patch('os.path.isfile', return_value=False):
            await cog.learn_command.callback(cog, mock_interaction)
            
            # Verify error message was sent
            mock_interaction.response.send_message.assert_awaited_once()
            call_args = mock_interaction.response.send_message.call_args[0][0]
            assert ERROR_MESSAGE in call_args
            assert "No vocabulary found" in call_args
    
    @pytest.mark.asyncio
    async def test_learn_command_json_decode_error(self, cog, mock_interaction):
        """Test learn command with corrupted JSON file."""
        with patch('os.path.isfile', return_value=True), \
             patch('builtins.open', mock_open(read_data="invalid json{{}")), \
             patch('json.load', side_effect=json.JSONDecodeError("Invalid JSON", "doc", 0)):
            
            await cog.learn_command.callback(cog, mock_interaction)
            
            # Verify error message was sent
            mock_interaction.response.send_message.assert_awaited_once()
            call_args = mock_interaction.response.send_message.call_args[0][0]
            assert ERROR_MESSAGE in call_args
            assert "Failed to read vocabulary data" in call_args
            assert "corrupted" in call_args
    
    @pytest.mark.asyncio
    async def test_learn_command_empty_vocabulary(self, cog, mock_interaction):
        """Test learn command with empty vocabulary file."""
        with patch('os.path.isfile', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps([]))):
            
            await cog.learn_command.callback(cog, mock_interaction)
            
            # Verify error message was sent
            mock_interaction.response.send_message.assert_awaited_once()
            call_args = mock_interaction.response.send_message.call_args[0][0]
            assert ERROR_MESSAGE in call_args
            assert "contains no words" in call_args
    
    @pytest.mark.asyncio
    async def test_learn_command_missing_fields(self, cog, mock_interaction):
        """Test learn command with word entry missing required fields."""
        incomplete_data = [
            {
                "english": "hello",
                "thai": "สวัสดี"
                # Missing transliteration field
            }
        ]
        
        with patch('os.path.isfile', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(incomplete_data))), \
             patch('random.choice', return_value=incomplete_data[0]):
            
            await cog.learn_command.callback(cog, mock_interaction)
            
            # Verify error message was sent
            mock_interaction.response.send_message.assert_awaited_once()
            call_args = mock_interaction.response.send_message.call_args[0][0]
            assert ERROR_MESSAGE in call_args
            assert "Missing key data" in call_args
    
    @pytest.mark.asyncio
    async def test_learn_command_general_exception(self, cog, mock_interaction):
        """Test learn command with unexpected exception."""
        with patch('os.path.isfile', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps([]))), \
             patch('json.load', side_effect=Exception("Unexpected error")):
            
            await cog.learn_command.callback(cog, mock_interaction)
            
            # Verify error message was sent
            mock_interaction.response.send_message.assert_awaited_once()
            call_args = mock_interaction.response.send_message.call_args[0][0]
            assert ERROR_MESSAGE in call_args
            assert "unexpected error occurred" in call_args
            assert "Unexpected error" in call_args
    
    @pytest.mark.asyncio
    async def test_learn_command_random_selection(self, cog, mock_interaction, sample_vocabulary_data):
        """Test that learn command randomly selects from vocabulary."""
        with patch('os.path.isfile', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(sample_vocabulary_data))):
            
            # Mock random.choice to return different words on successive calls
            call_count = 0
            def mock_random_choice(data):
                nonlocal call_count
                result = data[call_count % len(data)]
                call_count += 1
                return result
            
            with patch('random.choice', side_effect=mock_random_choice):
                # Call the command multiple times
                for i in range(3):
                    mock_interaction.reset_mock()
                    await cog.learn_command.callback(cog, mock_interaction)
                    
                    # Verify response was sent
                    mock_interaction.response.send_message.assert_awaited_once()
                    call_args = mock_interaction.response.send_message.call_args[0][0]
                    
                    # Verify different words are returned
                    expected_word = sample_vocabulary_data[i % len(sample_vocabulary_data)]
                    assert f'"{expected_word["english"]}"' in call_args
                    assert f'"{expected_word["thai"]}"' in call_args
                    assert f'`{expected_word["transliteration"]}`' in call_args


class TestVocabularyFileStructure:
    """Test the vocabulary file structure and integrity."""
    
    def test_vocabulary_file_exists(self):
        """Test that the vocabulary file exists."""
        word_list_path = './assets/data/thai-words.json'
        assert os.path.isfile(word_list_path), f"Vocabulary file not found at {word_list_path}"
    
    def test_vocabulary_file_is_valid_json(self):
        """Test that the vocabulary file contains valid JSON."""
        word_list_path = './assets/data/thai-words.json'
        
        try:
            with open(word_list_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Verify it's a list
            assert isinstance(data, list), "Vocabulary data should be a list"
            
            # Verify list is not empty
            assert len(data) > 0, "Vocabulary list should not be empty"
            
            # Verify each entry has required fields
            for i, word in enumerate(data):
                assert isinstance(word, dict), f"Word entry {i} should be a dictionary"
                assert 'english' in word, f"Word entry {i} missing 'english' field"
                assert 'thai' in word, f"Word entry {i} missing 'thai' field"
                assert 'transliteration' in word, f"Word entry {i} missing 'transliteration' field"
                assert isinstance(word['english'], str), f"Word entry {i} 'english' should be a string"
                assert isinstance(word['thai'], str), f"Word entry {i} 'thai' should be a string"
                assert isinstance(word['transliteration'], str), f"Word entry {i} 'transliteration' should be a string"
        
        except json.JSONDecodeError as e:
            pytest.fail(f"Vocabulary file contains invalid JSON: {e}")
        except Exception as e:
            pytest.fail(f"Error reading vocabulary file: {e}")
