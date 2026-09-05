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

from pathlib import Path

from utils.prompts import load_language_prompt_sections, render_language_prompt


def test_default_file_has_all_sections():
    sections = load_language_prompt_sections()
    assert set(sections) == {'transliterate', 'translate', 'summarize'}


def test_translate_substitution():
    prompt = render_language_prompt(
        'translate',
        text='สวัสดีชาวโลก',
        from_language='Thai',
        to_language='English',
    )
    assert (
        prompt
        == 'Translate the text "สวัสดีชาวโลก" from Thai to English. Keep the tone and meaning of the original text. Stay accurate.'
    )


def test_transliterate_includes_input_text():
    prompt = render_language_prompt('transliterate', text='สวัสดี')
    assert prompt is not None
    assert '"สวัสดี"' in prompt
    assert 'exact Thai-to-Latin transliteration engine' in prompt


def test_summarize_includes_transcript():
    prompt = render_language_prompt('summarize', transcript='Alice: hi\nBob: bye')
    assert prompt is not None
    assert 'Alice: hi\nBob: bye' in prompt
    assert 'no more than 800 characters' in prompt


def test_missing_section_returns_none(tmp_path: Path):
    path = tmp_path / 'prompts.md'
    path.write_text('# Translate\nHello {text}\n', encoding='utf-8')
    assert render_language_prompt('transliterate', path=str(path), text='x') is None


def test_missing_placeholder_returns_none():
    assert render_language_prompt('translate', text='hello') is None


def test_transliterate_useai_disables_thinking_and_zero_temperature():
    from cogs.transliterate import Transliterate
    from cogs.translate import TranslateCog
    from discord.ext import commands
    from discord import Intents

    bot = commands.Bot(command_prefix='!', intents=Intents.default())
    transliterate = Transliterate(bot)
    translate = TranslateCog(bot)

    assert transliterate.ai.temperature == 0.0
    assert transliterate.ai.disable_thinking is True
    assert translate.ai.temperature is None
    assert translate.ai.disable_thinking is False


def test_gemini_thinking_config_uses_budget_for_2_5_and_level_for_3():
    from utils.helpers import UseAI

    class FakeThinking:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class FakeTypes:
        ThinkingConfig = FakeThinking

    class FakeGenai:
        types = FakeTypes

    two_five = UseAI(provider='gemini', disable_thinking=True)
    two_five.model_name = 'gemini-2.5-flash-lite'
    assert two_five._gemini_thinking_config(FakeGenai).kwargs == {'thinking_budget': 0}

    three = UseAI(provider='gemini', disable_thinking=True)
    three.model_name = 'gemini-3.5-flash-lite'
    assert three._gemini_thinking_config(FakeGenai).kwargs == {'thinking_level': 'minimal'}
