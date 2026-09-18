#!/usr/bin/env python3
"""
Script to prepare your local SQLite database for uploading to Turso.
This enables WAL mode and exports the database in Turso-compatible format.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "dwts.db"
OUTPUT_PATH = Path(__file__).parent / "dwts_for_turso.db"


def migrate_to_wal():
    """Convert SQLite database to WAL mode for Turso compatibility."""

    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        print("Run the app first to create the database.")
        return False

    # Copy the database
    import shutil
    shutil.copy(DB_PATH, OUTPUT_PATH)

    # Enable WAL mode on the copy
    conn = sqlite3.connect(OUTPUT_PATH)
    cursor = conn.cursor()

    # Check current mode
    cursor.execute("PRAGMA journal_mode")
    current_mode = cursor.fetchone()[0]
    print(f"Current journal mode: {current_mode}")

    # Enable WAL mode
    cursor.execute("PRAGMA journal_mode=WAL")
    new_mode = cursor.fetchone()[0]
    print(f"New journal mode: {new_mode}")

    # Optimize the database
    cursor.execute("VACUUM")

    conn.commit()
    conn.close()

    print(f"\n✅ Success! Database exported to: {OUTPUT_PATH}")
    print(f"\nNext steps:")
    print(f"1. Upload {OUTPUT_PATH.name} to Turso:")
    print(f"   turso db create dwts-tracker --from-file {OUTPUT_PATH}")
    print(f"2. Get your database URL and token:")
    print(f"   turso db show dwts-tracker --url")
    print(f"   turso db tokens create dwts-tracker")

    return True


if __name__ == "__main__":
    migrate_to_wal()
