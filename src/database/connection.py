"""
Database connection utilities for IntelliQuery AI.

Provides helpers to create an engine, obtain sessions, execute raw SQL
that returns a ``pandas.DataFrame``, and introspect the schema.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

import pandas as pd
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.config.settings import Settings
from src.utils.logger import setup_logger
from src.utils.error_handler import DatabaseError

logger = setup_logger("database")

# ── Module-level singletons ──────────────────────────────────────────────────
_engine: Engine | None = None
_SessionFactory: sessionmaker | None = None


def get_engine() -> Engine:
    """Return a SQLAlchemy engine (created once, reused afterwards).

    Uses connection-pool defaults suitable for a Streamlit app.
    """
    global _engine
    if _engine is None:
        try:
            _engine = create_engine(
                Settings.DATABASE_URL,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,  # verify connection is alive
            )
            logger.info("Database engine created successfully.")
        except Exception as exc:
            logger.error("Failed to create database engine: %s", exc)
            raise DatabaseError(f"Cannot create engine: {exc}") from exc
    return _engine


def get_session() -> Session:
    """Return a new SQLAlchemy ``Session``."""
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(bind=get_engine())
    return _SessionFactory()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Context manager that commits on success and rolls back on error."""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def test_connection() -> bool:
    """Return ``True`` if the database is reachable, ``False`` otherwise."""
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection test passed.")
        return True
    except Exception as exc:
        logger.error("Database connection test failed: %s", exc)
        return False


def execute_query(sql: str) -> pd.DataFrame:
    """Execute a raw SQL query and return the result as a DataFrame.

    Args:
        sql: A valid SQL ``SELECT`` statement.

    Returns:
        Query results as a ``pandas.DataFrame``.

    Raises:
        DatabaseError: If the query fails to execute.
    """
    try:
        with get_engine().connect() as conn:
            df = pd.read_sql(text(sql), conn)
        logger.info("Query executed successfully (%d rows).", len(df))
        return df
    except Exception as exc:
        logger.error("Query execution failed: %s | SQL: %s", exc, sql)
        raise DatabaseError(f"Query execution failed: {exc}") from exc


def get_table_info() -> dict[str, list[dict]]:
    """Return schema information for every table in the database.

    Returns:
        Mapping of ``table_name`` → list of column dicts, each containing
        ``name``, ``type``, ``nullable``, and ``primary_key``.
    """
    try:
        insp = inspect(get_engine())
        schema: dict[str, list[dict]] = {}
        for table_name in insp.get_table_names():
            cols = []
            for col in insp.get_columns(table_name):
                cols.append(
                    {
                        "name": col["name"],
                        "type": str(col["type"]),
                        "nullable": col.get("nullable", True),
                        "primary_key": col.get("autoincrement", False)
                        or col["name"].endswith("_id"),
                    }
                )
            schema[table_name] = cols
        return schema
    except Exception as exc:
        logger.error("Failed to retrieve table info: %s", exc)
        raise DatabaseError(f"Schema introspection failed: {exc}") from exc
