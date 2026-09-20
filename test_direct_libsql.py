#!/usr/bin/env python3
"""Test direct connection to Turso using libsql_experimental."""

import libsql_experimental as libsql
import toml

# Load secrets
with open('.streamlit/secrets.toml', 'r') as f:
    secrets = toml.load(f)

turso_url = secrets['TURBO_URL']
turso_token = secrets['TURBO_TOKEN']

# Try to connect directly
print(f"Connecting to: {turso_url}")
print(f"Token length: {len(turso_token)}")

# Convert to https URL for libsql
https_url = turso_url.replace('libsql://', 'https://')
print(f"Using URL: {https_url}")

try:
    conn = libsql.connect(database=https_url, auth_token=turso_token)
    print("✅ Connected successfully!")

    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"\nTables found: {len(tables)}")
    for table in tables:
        print(f"  - {table[0]}")

    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
