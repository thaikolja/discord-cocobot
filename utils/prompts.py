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

# Future annotations so the type hints don't demand a time machine
from __future__ import annotations

# Logging, because silent file failures are how production weekends die
import logging

# Regex to spot the three sacred headings in the markdown cookbook
import re

# Cache so we don't re-read the same markdown on every slash command
from functools import lru_cache

# Path objects beat string-concatenated "../.." folklore
from pathlib import Path

# Logger named after this module, not "root" like a mystery novel
logger = logging.getLogger(__name__)

# Default cookbook: walk up from utils/ into assets/data/
DEFAULT_PROMPT_PATH = (
    Path(__file__).resolve().parent.parent / 'assets' / 'data' / 'language-prompt-definition.md'
)

# Only Transliterate, Translate, Summarize — other headings can sit in the hallway
_SECTION_HEADING = re.compile(r'^# (Transliterate|Translate|Summarize)\s*$')


# Four cached paths is plenty; this isn't a CMS
@lru_cache(maxsize=4)
# Split the markdown into named blobs and cache the result
def load_language_prompt_sections(path: str | None = None) -> dict[str, str]:
    """Read and split the prompt file. Result is cached per path."""

    # Honor an override path, otherwise the bundled markdown
    prompt_path = Path(path) if path else DEFAULT_PROMPT_PATH

    # Disk can always lie; catch it before the LLM does
    try:

        # UTF-8 or we get the classic "Thai as mojibake" special
        raw = prompt_path.read_text(encoding='utf-8')

    # Missing file, permissions, NFS having a moment
    except OSError as exc:

        # Log the path so the next human doesn't grep for ghosts
        logger.error('Failed to read language prompt file %s: %s', prompt_path, exc)

        # Empty dict: callers already know how to sulk
        return {}

    # Heading → body map we fill while walking lines
    sections: dict[str, str] = {}

    # Which heading we're currently stuffing
    current: str | None = None

    # Line buffer for the active section
    buf: list[str] = []

    # Commit the current buffer into the map
    def _flush() -> None:

        # Don't invent a section named None; that's not a prompt, that's a cry for help
        if current is not None:

            # Join lines and strip so templates aren't all leading blank lines
            sections[current] = '\n'.join(buf).strip()

    # Walk the file like it's 1998 and XML never happened
    for line in raw.splitlines():

        # Is this one of the three headings we actually care about?
        match = _SECTION_HEADING.match(line)

        # New section starts; park the previous one first
        if match:

            # Save whatever we were collecting
            _flush()

            # Headings stored casefolded so "Translate" and "translate" don't fork
            current = match.group(1).casefold()

            # Fresh buffer for the new sermon
            buf = []

            # Heading line itself is not prompt body
            continue

        # Ignore preamble until the first real heading
        if current is not None:

            # Keep the line, even if it's blank — formatting is part of the prompt
            buf.append(line)

    # Don't drop the last section just because the file ended
    _flush()

    # Hand the cookbook back to whoever asked
    return sections


# Fill a named section with caller-supplied placeholders
def render_language_prompt(section: str, path: str | None = None, **values: str) -> str | None:
    """Return a filled prompt for translate, transliterate, or summarize."""

    # Load (or reuse cache) and pick the section, ignoring shouty callers
    template = load_language_prompt_sections(path).get(section.casefold())

    # Missing section is a config bug, not a creative writing exercise
    if not template:

        # Say which heading we wanted so someone can fix the markdown
        logger.error('Language prompt section %r is missing', section)

        # None means "don't send this to Gemini, you'll just confuse it"
        return None

    # format_map so extra kwargs don't explode; missing keys still do
    try:

        # Substitute {placeholders} from the command
        return template.format_map(values)

    # Typo in the markdown or a missing value from the cog
    except (KeyError, ValueError) as exc:

        # Log section name so we don't debug the wrong template
        logger.error('Failed to format language prompt section %r: %s', section, exc)

        # Fail closed; a half-formatted prompt is worse than silence
        return None
