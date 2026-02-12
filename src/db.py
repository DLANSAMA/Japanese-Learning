import sqlite3
import os
import json
from contextlib import contextmanager

DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
DB_FILE = os.path.join(DATA_DIR, 'vocab.db')

def init_db():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Vocabulary Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS vocabulary (
            word TEXT PRIMARY KEY,
            kana TEXT,
            romaji TEXT,
            meaning TEXT,
            level INTEGER,
            last_review TEXT,
            tags TEXT,
            ease_factor REAL,
            interval INTEGER,
            due_date TEXT,
            status TEXT,
            pos TEXT,
            example_sentence TEXT,
            fsrs_stability REAL,
            fsrs_difficulty REAL,
            fsrs_retrievability REAL,
            fsrs_last_review TEXT
        )
    ''')

    conn.commit()
    conn.close()

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_FILE)
    # Enable row factory for dict-like access if needed, but we'll map manually to dataclass
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
