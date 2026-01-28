import sqlite3
from pathlib import Path
from typing import Iterator

DB_PATH = Path("data/app.db")


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                purchase_date TEXT NOT NULL,
                status TEXT NOT NULL,
                last_sent_at TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day_offset INTEGER NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                event TEXT NOT NULL,
                detail TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(customer_id) REFERENCES customers(id)
            )
            """
        )


def fetch_all(query: str, params: tuple = ()) -> list[sqlite3.Row]:
    conn = get_connection()
    with conn:
        cursor = conn.execute(query, params)
        return list(cursor.fetchall())


def execute(query: str, params: tuple = ()) -> int:
    conn = get_connection()
    with conn:
        cursor = conn.execute(query, params)
        return cursor.lastrowid


def execute_many(query: str, params_seq: Iterator[tuple]) -> None:
    conn = get_connection()
    with conn:
        conn.executemany(query, params_seq)
