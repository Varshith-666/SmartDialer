"""Database connection and transaction manager for SmartDialer."""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional
from smart_dialer.config import settings


def dict_factory(cursor, row):
    """Convert SQLite row to a Python dict."""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Create a new SQLite connection with production pragma settings."""
    path = db_path or settings.DB_PATH
    conn = sqlite3.connect(
        path,
        timeout=15.0,  # 15s busy timeout for high concurrency
        isolation_level=None,  # Autocommit mode by default; explicit BEGIN for transactions
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
    )
    conn.row_factory = dict_factory

    # Production SQLite pragmas
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA busy_timeout = 15000;")
    return conn


@contextmanager
def get_db(db_path: Optional[str] = None) -> Generator[sqlite3.Connection, None, None]:
    """Context manager yielding a database connection and safely closing it."""
    conn = get_db_connection(db_path)
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def transaction(conn: sqlite3.Connection) -> Generator[sqlite3.Cursor, None, None]:
    """Strict IMMEDIATE transaction context manager ensuring atomicity and isolation."""
    cursor = conn.cursor()
    cursor.execute("BEGIN IMMEDIATE;")
    try:
        yield cursor
        cursor.execute("COMMIT;")
    except Exception:
        try:
            cursor.execute("ROLLBACK;")
        except Exception:
            pass
        raise
    finally:
        cursor.close()


def init_db(db_path: Optional[str] = None) -> None:
    """Execute the DDL schema to create tables and indexes."""
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    path = db_path or settings.DB_PATH
    conn = sqlite3.connect(path, timeout=10.0)
    try:
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()
