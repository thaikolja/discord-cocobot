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

"""Release-metadata guards for shipping v3.9.0."""

import dataclasses
from pathlib import Path

from config.app_config import AppConfig

ROOT = Path(__file__).resolve().parent.parent
CHANGELOG = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
BOT_PY = (ROOT / "bot.py").read_text(encoding="utf-8")


def test_version_default_is_3_9_0():
    field = next(f for f in dataclasses.fields(AppConfig) if f.name == "version")
    assert field.default == "3.9.0"


def test_changelog_ships_as_v3_9_0_with_restored_history():
    assert "## Unreleased" not in CHANGELOG
    assert CHANGELOG.find("## v3.9.0") != -1
    assert CHANGELOG.find("## v3.9.0") < CHANGELOG.find("## v3.8.0")
    assert "## v3.7.0" in CHANGELOG
    assert "## v3.6.0" in CHANGELOG
    assert "## v3.5.3" in CHANGELOG


def test_changelog_leave_copy_is_not_italic():
    assert "italic line" not in CHANGELOG
    section = CHANGELOG.split("## v3.9.0", 1)[1].split("## v3.8.0", 1)[0]
    assert "feat(leave)" in section
    assert "simulate" in section.lower()


def test_changelog_v3_9_0_uses_conventional_commits_with_hashes():
    section = CHANGELOG.split("## v3.9.0", 1)[1].split("## v3.8.0", 1)[0]
    assert "### What's Changed" in section
    assert "[`8aef0e2`](https://gitlab.com/thailand-discord/bots/cocobot/-/commit/8aef0e2397dccbdcbb1169a84ab2e69218a364a0)" in section
    assert "by @" not in section


def test_contributing_requires_conventional_commits():
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "https://www.conventionalcommits.org/en/v1.0.0/" in contributing
    assert "<type>[optional scope][optional !]: <description>" in contributing


def test_bot_loads_leave_and_warn():
    assert "'cogs.leave'" in BOT_PY
    assert "'cogs.warn'" in BOT_PY


def test_user_docs_mention_v3_9_0():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "v3.9.0" in readme
    assert "*Version: 3.9.0*" in agents
    assert "3.9.0" in contributing


def test_deploy_sh_invokes_existing_docker_script():
    deploy = (ROOT / "deploy.sh").read_text(encoding="utf-8")
    script = ROOT / "scripts" / "deploy-as-docker.sh"
    assert "scripts/deploy-as-docker.sh" in deploy
    assert script.is_file()
