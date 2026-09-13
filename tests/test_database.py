import sqlite3

from utils.database import init_db


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

    # Only the 3 tables that are actively used by the bot should be created
    expected_tables = [
        "cache_entries",
        "rate_limits",
        "visa_reminders",
    ]
    for table in expected_tables:
        assert table in tables, f"Expected table '{table}' is missing from the database"

    # Ensure obsolete/unused tables are NOT created
    obsolete_tables = ["users", "guilds", "command_usage", "bot_settings"]
    for table in obsolete_tables:
        assert table not in tables, f"Obsolete table '{table}' should not exist"
