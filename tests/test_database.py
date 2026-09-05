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

# sqlite3 for peeking under SQLAlchemy's skirt
import sqlite3

# text() so SELECT 1 isn't a crime
from sqlalchemy import text

# The actual persistence helpers under test
from utils.database import get_db_session, init_db


# First-boot should create a real file and the tables we still care about
def test_database_initialization(tmp_path):
    """Test that init_db creates the database file and all required tables."""
    # Park the DB in pytest's sandbox, not next to production
    db_path = tmp_path / "test_cocobot.db"

    # sqlite URL because we are not deploying Postgres in a unit test
    db_url = f"sqlite:///{db_path}"

    # Pretend this is a brand-new coconut
    init_db(db_url)

    # File on disk or we failed at existence
    assert db_path.exists(), "Database file was not created"

    # Bypass SQLAlchemy; sqlite_master never lies
    conn = sqlite3.connect(db_path)

    # Cursor for the gossip query
    cursor = conn.cursor()

    # Ask SQLite which tables it actually built
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

    # Flatten the names; we don't need the tuples
    tables = [row[0] for row in cursor.fetchall()]

    # Close before anyone else wants the lock
    conn.close()

    # The living schema — not the graveyard of unused models
    expected_tables = [
        "cache_entries",
        "rate_limits",
        "visa_reminders",
        "warning_entries",
    ]

    # Each expected table must show up
    for table in expected_tables:

        # Missing table = init_db forgot its job
        assert table in tables, f"Expected table '{table}' is missing from the database"

    # Ghosts from earlier designs should stay dead
    obsolete_tables = ["users", "guilds", "command_usage", "bot_settings"]

    # Confirm we didn't resurrect them
    for table in obsolete_tables:

        # If this fires, someone re-enabled a zombie model
        assert table not in tables, f"Obsolete table '{table}' should not exist"


# Both `with get_db_session()` and `next(get_db_session())` must work — history is messy
def test_get_db_session_supports_both_access_patterns(tmp_path):
    """Database sessions should work with both `with get_db_session()` and `next(get_db_session())`."""
    # Separate file so we don't share state with the previous test
    db_path = tmp_path / "test_session_patterns.db"

    # Fresh schema for the dual-API check
    init_db(f"sqlite:///{db_path}")

    # Context-manager style: the polite way
    with get_db_session() as db:

        # If this isn't 1, the session is decorative
        assert db.execute(text("SELECT 1")).scalar() == 1

    # Generator style: the one half the cogs still use
    with next(get_db_session()) as db:

        # Same query, different handshake
        assert db.execute(text("SELECT 1")).scalar() == 1
