#!/usr/bin/env python
"""
Create all IntelliQuery AI database tables.

Usage::

    python scripts/setup_database.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the project root is on sys.path so ``src`` is importable.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config.settings import Settings
from src.database.models import Base
from src.database.connection import get_engine, test_connection


def main() -> None:
    Settings.validate()

    print("🔌  Testing database connection …")
    if not test_connection():
        print("❌  Cannot connect to the database. Check DATABASE_URL in .env")
        sys.exit(1)

    print("✅  Connection OK")
    print("🏗️  Creating tables …")

    engine = get_engine()
    Base.metadata.create_all(engine)

    print("✅  All tables created successfully!")
    print()
    print("Tables:")
    for table_name in Base.metadata.tables:
        print(f"  • {table_name}")


if __name__ == "__main__":
    main()
