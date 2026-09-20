#!/usr/bin/env python3
"""Test different SQLAlchemy connection formats for Turso."""

from sqlalchemy import create_engine, text
import toml
import sqlalchemy_libsql

# Load secrets
with open('.streamlit/secrets.toml', 'r') as f:
    secrets = toml.load(f)

turso_url = secrets['TURBO_URL']
turso_token = secrets['TURBO_TOKEN']

# Test different formats
formats = [
    {
        "name": "Format 1: authToken in query string",
        "url": turso_url.replace('libsql://', 'sqlite+libsql://') + f"?authToken={turso_token}&secure=true",
        "connect_args": {'check_same_thread': False}
    },
    {
        "name": "Format 2: auth_token in query string",
        "url": turso_url.replace('libsql://', 'sqlite+libsql://') + f"?auth_token={turso_token}&secure=true",
        "connect_args": {'check_same_thread': False}
    },
    {
        "name": "Format 3: auth_token in connect_args",
        "url": turso_url.replace('libsql://', 'sqlite+libsql://') + "?secure=true",
        "connect_args": {'check_same_thread': False, 'auth_token': turso_token}
    },
]

for fmt in formats:
    print(f"\nTrying: {fmt['name']}")
    print(f"URL: {fmt['url'][:80]}...")
    try:
        engine = create_engine(fmt['url'], connect_args=fmt['connect_args'], echo=False)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM players"))
            count = result.fetchone()[0]
            print(f"✅ SUCCESS! Found {count} players")
            break
    except Exception as e:
        print(f"❌ Failed: {str(e)[:100]}")
