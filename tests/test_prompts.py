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
