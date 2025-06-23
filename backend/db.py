import sqlite3
from contextlib import contextmanager

DB_PATH = 'ri_experiment.db'


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            arm TEXT NOT NULL
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            round INTEGER,
            omega INTEGER,
            decoy INTEGER,
            choice INTEGER,
            payoff REAL
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            round INTEGER,
            arm TEXT,
            tokens INTEGER,
            cost REAL,
            prompt TEXT,
            reply TEXT
        )
        """
    )
    conn.commit()
    conn.close()


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()
