#!/usr/bin/env python3
"""Sync local SQLite database to Turso."""

import sqlite3
import libsql_experimental as libsql
import toml
from pathlib import Path

# Load secrets
with open('.streamlit/secrets.toml', 'r') as f:
    secrets = toml.load(f)

turso_url = secrets['TURBO_URL'].replace('libsql://', 'https://')
turso_token = secrets['TURBO_TOKEN']

# Connect to local SQLite
local_db = Path(__file__).parent / "dwts.db"
if not local_db.exists():
    print("❌ Local database not found. Run the app first to create it.")
    exit(1)

local_conn = sqlite3.connect(local_db)
local_cursor = local_conn.cursor()

# Connect to Turso
print(f"Connecting to Turso: {turso_url}")
turso_conn = libsql.connect(database=turso_url, auth_token=turso_token)
turso_cursor = turso_conn.cursor()

print("\n📋 Copying schema and data to Turso...\n")

# Get schema from local database
local_cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
tables_sql = local_cursor.fetchall()

for (sql,) in tables_sql:
    if sql:
        print(f"Creating table: {sql[:50]}...")
        try:
            turso_cursor.execute(sql)
            turso_conn.commit()
        except Exception as e:
            print(f"  ⚠️ Warning: {e}")

# Get all table names
local_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
tables = [row[0] for row in local_cursor.fetchall()]

# Copy data from each table
for table in tables:
    print(f"\n📊 Copying data from table: {table}")

    # Get column names
    local_cursor.execute(f"PRAGMA table_info({table})")
    columns = [col[1] for col in local_cursor.fetchall()]

    # Get all rows
    local_cursor.execute(f"SELECT * FROM {table}")
    rows = local_cursor.fetchall()

    print(f"  Found {len(rows)} rows")

    if rows:
        placeholders = ','.join(['?' for _ in columns])
        insert_sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"

        for row in rows:
            try:
                turso_cursor.execute(insert_sql, row)
            except Exception as e:
                print(f"  ⚠️ Error inserting row: {e}")

        turso_conn.commit()
        print(f"  ✅ Copied {len(rows)} rows")

# Verify
print("\n✅ Migration complete! Verifying...")
turso_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
turso_tables = turso_cursor.fetchall()
print(f"\nTurso database now has {len(turso_tables)} tables:")
for (table,) in turso_tables:
    turso_cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = turso_cursor.fetchone()[0]
    print(f"  - {table}: {count} rows")

# Close connections
local_conn.close()
turso_conn.close()

print("\n🎉 Done! Your Turso database is now synced with your local data.")
