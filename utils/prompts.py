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

"""Load Gemini prompt templates from assets/data/language-prompt-definition.md."""

from __future__ import annotations

import logging
import re
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_PROMPT_PATH = (
    Path(__file__).resolve().parent.parent / 'assets' / 'data' / 'language-prompt-definition.md'
)

_SECTION_HEADING = re.compile(r'^# (Transliterate|Translate|Summarize)\s*$')


@lru_cache(maxsize=4)
def load_language_prompt_sections(path: str | None = None) -> dict[str, str]:
    """Read and split the prompt file. Result is cached per path."""
    prompt_path = Path(path) if path else DEFAULT_PROMPT_PATH
    try:
        raw = prompt_path.read_text(encoding='utf-8')
    except OSError as exc:
        logger.error('Failed to read language prompt file %s: %s', prompt_path, exc)
        return {}

    sections: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []

    def _flush() -> None:
        if current is not None:
            sections[current] = '\n'.join(buf).strip()

    for line in raw.splitlines():
        match = _SECTION_HEADING.match(line)
        if match:
            _flush()
            current = match.group(1).casefold()
            buf = []
            continue
        if current is not None:
            buf.append(line)

    _flush()
    return sections


def render_language_prompt(section: str, path: str | None = None, **values: str) -> str | None:
    """Return a filled prompt for translate, transliterate, or summarize."""
    template = load_language_prompt_sections(path).get(section.casefold())
    if not template:
        logger.error('Language prompt section %r is missing', section)
        return None

    try:
        return template.format_map(values)
    except (KeyError, ValueError) as exc:
        logger.error('Failed to format language prompt section %r: %s', section, exc)
        return None
