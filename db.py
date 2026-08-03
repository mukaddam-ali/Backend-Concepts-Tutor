"""SQLite storage for document chunks and their embeddings."""

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "knowledge.db"


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            content TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def clear_chunks() -> None:
    conn = get_connection()
    conn.execute("DELETE FROM chunks")
    conn.commit()
    conn.close()


def insert_chunk(source: str, content: str, embedding: list[float]) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO chunks (source, content, embedding) VALUES (?, ?, ?)",
        (source, content, json.dumps(embedding)),
    )
    conn.commit()
    conn.close()


def get_all_chunks() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT id, source, content, embedding FROM chunks").fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "source": row[1],
            "content": row[2],
            "embedding": json.loads(row[3]),
        }
        for row in rows
    ]


def count_chunks() -> int:
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    conn.close()
    return count
