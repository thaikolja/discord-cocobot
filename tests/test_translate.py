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

# Import mocking utilities from unittest.mock
from unittest.mock import AsyncMock, MagicMock, patch

# Import pytest framework for testing
import pytest

# Import Discord commands extension
from discord.ext import commands

# Import the TranslateCog class from cogs.translate module
from cogs.translate import TranslateCog


# Fixture to create a bot instance with default configuration
@pytest.fixture
def bot():
    # The translation cog only stores the bot reference; no live client is needed.
    return MagicMock(spec=commands.Bot)


# Fixture to create an instance of TranslateCog with the bot instance
@pytest.fixture
def cog(bot):
    # Initialize and return a new TranslateCog instance with the bot
    return TranslateCog(bot)


# Fixture to create a mock Discord interaction object
@pytest.fixture
def interaction():
    # Return an AsyncMock object to simulate Discord interaction
    return AsyncMock()


@pytest.fixture(autouse=True)
def run_translation_inline(monkeypatch):
    """Avoid creating real worker threads for the mocked AI call."""

    async def to_thread(function, *args, **kwargs):
        return function(*args, **kwargs)

    monkeypatch.setattr("cogs.translate.asyncio.to_thread", to_thread)


def assert_translation_response(interaction, expected):
    """Assert a follow-up is safe from mentions and contains expected content."""
    interaction.followup.send.assert_awaited_once()
    assert interaction.followup.send.await_args.args == (expected,)
    allowed_mentions = interaction.followup.send.await_args.kwargs["allowed_mentions"]
    assert allowed_mentions.to_dict() == {"parse": []}


# Test case for successful translation with specified languages
@pytest.mark.asyncio
@patch("cogs.translate.UseAI")
async def test_successful_translation(mock_prompt, cog, interaction):
    # Set up mock response from AI with expected translation
    mock_prompt.return_value.prompt.return_value = "Hello world"

    # Call the translate command with test parameters
    await cog.translate_command.callback(
        cog,
        interaction,
        text="สวัสดีชาวโลก",
        from_language="Thai",
        to_language="English",
    )

    # Verify interaction response was deferred once
    interaction.response.defer.assert_awaited_once()

    # Verify followup message was sent with translated text
    assert_translation_response(
        interaction,
        "📚️ **Input (Thai):** สวัสดีชาวโลก\n**Output (English):** Hello world",
    )

    # Verify AI prompt was called with correct translation parameters
    mock_prompt.return_value.prompt.assert_called_once_with(
        'Translate the text "สวัสดีชาวโลก" from Thai to English. Keep the tone and meaning of the original text. Stay accurate.'
    )


@pytest.mark.asyncio
@patch("cogs.translate.UseAI")
async def test_auto_detect_english_to_thai(mock_prompt, cog, interaction):
    mock_prompt.return_value.prompt.return_value = "สวัสดี"

    await cog.translate_command.callback(cog, interaction, text="Hello")

    interaction.response.defer.assert_awaited_once()
    assert_translation_response(
        interaction,
        "📚️ **Input (English):** Hello\n**Output (Thai):** สวัสดี",
    )
    mock_prompt.return_value.prompt.assert_called_once_with(
        'Translate the text "Hello" from English to Thai. Keep the tone and meaning of the original text. Stay accurate.'
    )


@pytest.mark.asyncio
@patch("cogs.translate.UseAI")
async def test_explicit_english_to_thai(mock_prompt, cog, interaction):
    mock_prompt.return_value.prompt.return_value = "สวัสดี"

    await cog.translate_command.callback(
        cog,
        interaction,
        text="Hello",
        from_language="English",
        to_language="Thai",
    )

    assert_translation_response(
        interaction,
        "📚️ **Input (English):** Hello\n**Output (Thai):** สวัสดี",
    )
    mock_prompt.return_value.prompt.assert_called_once_with(
        'Translate the text "Hello" from English to Thai. Keep the tone and meaning of the original text. Stay accurate.'
    )


@pytest.mark.asyncio
@patch("cogs.translate.UseAI")
async def test_auto_detect_thai_to_english(mock_prompt, cog, interaction):
    mock_prompt.return_value.prompt.return_value = "Hello world"

    await cog.translate_command.callback(cog, interaction, text="สวัสดีค่ะ โลก")

    interaction.response.defer.assert_awaited_once()
    assert_translation_response(
        interaction,
        "📚️ **Input (Thai):** สวัสดีค่ะ โลก\n**Output (English):** Hello world",
    )
    mock_prompt.return_value.prompt.assert_called_once_with(
        'Translate the text "สวัสดีค่ะ โลก" from Thai to English. Keep the tone and meaning of the original text. Stay accurate.'
    )


# Test case for translation with special characters
@pytest.mark.asyncio
@patch("cogs.translate.UseAI")
async def test_translation_with_special_characters(mock_prompt, cog, interaction):
    # Set up mock response from AI with expected translation
    mock_prompt.return_value.prompt.return_value = "¿Cómo estás?"

    # Call the translate command with text and language parameters
    await cog.translate_command.callback(
        cog,
        interaction,
        text="How are you?",
        from_language="English",
        to_language="Spanish",
    )

    # Verify interaction response was deferred once
    interaction.response.defer.assert_awaited_once()

    # Verify followup message was sent with translated text
    assert_translation_response(
        interaction,
        "📚️ **Input (English):** How are you?\n**Output (Spanish):** ¿Cómo estás?",
    )

    # Verify AI prompt was called with correct translation parameters
    mock_prompt.return_value.prompt.assert_called_once_with(
        'Translate the text "How are you?" from English to Spanish. Keep the tone and meaning of the original text. Stay accurate.'
    )


@pytest.mark.asyncio
@patch("cogs.translate.UseAI")
async def test_unknown_detection_uses_truthful_label_and_legacy_routing(
    mock_prompt, cog, interaction
):
    mock_prompt.return_value.prompt.return_value = "๑๒๓"

    await cog.translate_command.callback(cog, interaction, text="123")

    assert_translation_response(
        interaction,
        "📚️ **Input (Unknown):** 123\n**Output (Thai):** ๑๒๓",
    )
    mock_prompt.return_value.prompt.assert_called_once_with(
        'Translate the text "123" from English to Thai. Keep the tone and meaning of the original text. Stay accurate.'
    )


@pytest.mark.asyncio
@patch("cogs.translate.UseAI")
async def test_multiline_response_escapes_markdown_and_mentions(
    mock_prompt, cog, interaction
):
    mock_prompt.return_value.prompt.return_value = "บรรทัด *หนึ่ง*\n@everyone"

    await cog.translate_command.callback(
        cog,
        interaction,
        text="line *one*\n@here",
        from_language="English",
        to_language="Thai",
    )

    assert_translation_response(
        interaction,
        "📚️ **Input (English):** line \\*one\\*\n@\u200bhere"
        "\n**Output (Thai):** บรรทัด \\*หนึ่ง\\*\n@\u200beveryone",
    )


@pytest.mark.asyncio
@patch("cogs.translate.UseAI")
async def test_long_translation_response_stays_within_discord_limit(
    mock_prompt, cog, interaction
):
    mock_prompt.return_value.prompt.return_value = "ข" * 3000

    await cog.translate_command.callback(
        cog,
        interaction,
        text="a" * 3000,
        from_language="English",
        to_language="Thai",
    )

    response = interaction.followup.send.await_args.args[0]
    assert len(response.encode("utf-16-le")) // 2 == 2000
    assert response.startswith("📚️ **Input (English):** ")
    assert "\n**Output (Thai):** " in response
    assert response.count("…") == 2
    assert_translation_response(interaction, response)


@pytest.mark.asyncio
@patch("cogs.translate.UseAI")
async def test_emoji_heavy_response_obeys_utf16_limit(mock_prompt, cog, interaction):
    mock_prompt.return_value.prompt.return_value = "ข" * 3000

    await cog.translate_command.callback(
        cog,
        interaction,
        text="😀" * 3000,
        from_language="English",
        to_language="Thai",
    )

    response = interaction.followup.send.await_args.args[0]
    assert len(response.encode("utf-16-le")) // 2 == 2000
    assert len(response) < 2000
    assert response.count("…") == 2
    assert_translation_response(interaction, response)
