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

import sqlite3

from sqlalchemy import text

from utils.database import get_db_session, init_db


def test_database_initialization(tmp_path):
    """Test that init_db creates the database file and all required tables."""
    db_path = tmp_path / "test_cocobot.db"
    db_url = f"sqlite:///{db_path}"

    # Initialize the database with a fresh temp path (simulates first-time startup)
    init_db(db_url)

    # Verify the file was eagerly created on disk
    assert db_path.exists(), "Database file was not created"

    # Connect directly via sqlite3 to inspect the created tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    # All actively used persistence tables should be created
    expected_tables = [
        "cache_entries",
        "rate_limits",
        "visa_reminders",
        "warning_entries",
    ]
    for table in expected_tables:
        assert table in tables, f"Expected table '{table}' is missing from the database"

    # Ensure obsolete/unused tables are NOT created
    obsolete_tables = ["users", "guilds", "command_usage", "bot_settings"]
    for table in obsolete_tables:
        assert table not in tables, f"Obsolete table '{table}' should not exist"


def test_get_db_session_supports_both_access_patterns(tmp_path):
    """Database sessions should work with both `with get_db_session()` and `next(get_db_session())`."""
    db_path = tmp_path / "test_session_patterns.db"
    init_db(f"sqlite:///{db_path}")

    with get_db_session() as db:
        assert db.execute(text("SELECT 1")).scalar() == 1

    with next(get_db_session()) as db:
        assert db.execute(text("SELECT 1")).scalar() == 1

