import json
import os
import sqlite3
import threading
import tempfile
from dataclasses import asdict, fields
from typing import List, Optional, Dict
from .models import Vocabulary, GrammarLesson, UserProfile, GrammarExample, GrammarExercise
from .db import get_db, init_db, DB_FILE

DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
VOCAB_FILE = os.path.join(DATA_DIR, 'vocab.json')
GRAMMAR_FILE = os.path.join(DATA_DIR, 'grammar.json')
CURRICULUM_FILE = os.path.join(DATA_DIR, 'curriculum.json')
USER_FILE = os.path.join(DATA_DIR, 'user.json')

# Ensure DB is initialized
init_db()

# Constants for vocabulary insertion
VOCAB_KEYS = [
    'word', 'kana', 'romaji', 'meaning', 'level', 'last_review', 'tags',
    'ease_factor', 'interval', 'due_date', 'status', 'pos',
    'example_sentence', 'fsrs_stability', 'fsrs_difficulty',
    'fsrs_retrievability', 'fsrs_last_review', 'failure_count', 'is_leech'
]

VOCAB_COLUMNS = ', '.join(VOCAB_KEYS)
VOCAB_PLACEHOLDERS = ', '.join(['?'] * len(VOCAB_KEYS))
VOCAB_INSERT_QUERY = f'INSERT OR REPLACE INTO vocabulary ({VOCAB_COLUMNS}) VALUES ({VOCAB_PLACEHOLDERS})'

def _vocab_to_row(v: Vocabulary) -> tuple:
    """
    Optimized converter from Vocabulary object to DB row tuple.
    Avoids asdict() overhead and pre-computes JSON serialization for tags.
    """
    return (
        v.word,
        v.kana,
        v.romaji,
        v.meaning,
        v.level,
        v.last_review,
        json.dumps(v.tags),
        v.ease_factor,
        v.interval,
        v.due_date,
        v.status,
        v.pos,
        v.example_sentence,
        v.fsrs_stability,
        v.fsrs_difficulty,
        v.fsrs_retrievability,
        v.fsrs_last_review,
        v.failure_count,
        v.is_leech
    )

def _migrate_schema():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(vocabulary)")
        columns = [row['name'] for row in cursor.fetchall()]

        if 'failure_count' not in columns:
            cursor.execute("ALTER TABLE vocabulary ADD COLUMN failure_count INTEGER DEFAULT 0")

        if 'is_leech' not in columns:
            cursor.execute("ALTER TABLE vocabulary ADD COLUMN is_leech BOOLEAN DEFAULT 0")

        conn.commit()

def _migrate_json_to_db():
    """Migrate data from vocab.json to SQLite if DB is empty."""
    if not os.path.exists(VOCAB_FILE):
        return

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM vocabulary")
        count = cursor.fetchone()[0]

        if count == 0:
            print("Migrating vocab.json to SQLite database...")
            with open(VOCAB_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                vocab_list = [Vocabulary(**item) for item in data]

            # Bulk insert
            cursor.executemany(VOCAB_INSERT_QUERY, [_vocab_to_row(v) for v in vocab_list])
            conn.commit()
            print("Migration complete.")

def _insert_vocab_item(cursor, v: Vocabulary):
    cursor.execute(VOCAB_INSERT_QUERY, _vocab_to_row(v))

def _row_to_vocab(row) -> Vocabulary:
    data = dict(row)
    if data['tags']:
        try:
            data['tags'] = json.loads(data['tags'])
        except json.JSONDecodeError:
            data['tags'] = []
    else:
        data['tags'] = []
    return Vocabulary(**data)

# Perform migration check on module load
_migrate_schema()
_migrate_json_to_db()

# In-memory cache
_VOCAB_CACHE: Optional[List[Vocabulary]] = None
_VOCAB_MAP: Optional[Dict[str, Vocabulary]] = None

def load_vocab() -> List[Vocabulary]:
    global _VOCAB_CACHE, _VOCAB_MAP
    if _VOCAB_CACHE is not None:
        return list(_VOCAB_CACHE)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vocabulary")
        rows = cursor.fetchall()
        vocab_list = [_row_to_vocab(row) for row in rows]

        _VOCAB_CACHE = vocab_list
        _VOCAB_MAP = {v.word: v for v in vocab_list}

        return list(_VOCAB_CACHE)

def save_vocab(vocab_list: List[Vocabulary]):
    """
    Legacy method: overwrites the entire vocabulary in the DB.
    Optimized to use transaction for speed, but still O(N).
    Prefer using add_vocab_item or update_vocab_item for single items.
    """
    global _VOCAB_CACHE, _VOCAB_MAP

    # Update cache to match new list
    _VOCAB_CACHE = list(vocab_list)
    _VOCAB_MAP = {v.word: v for v in _VOCAB_CACHE}

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vocabulary")
        # Optimized bulk insert using executemany and helper
        cursor.executemany(VOCAB_INSERT_QUERY, [_vocab_to_row(v) for v in vocab_list])
        conn.commit()

def add_vocab_item(item: Vocabulary):
    global _VOCAB_CACHE, _VOCAB_MAP

    with get_db() as conn:
        cursor = conn.cursor()
        _insert_vocab_item(cursor, item)
        conn.commit()

    # Update cache if it exists
    if _VOCAB_MAP is not None:
        if item.word in _VOCAB_MAP:
            cached = _VOCAB_MAP[item.word]
            # If it's the same object, changes are already reflected (if modified in place)
            # If not, we update the cached object in place to maintain references in _VOCAB_CACHE
            if cached is not item:
                for field in fields(Vocabulary):
                    setattr(cached, field.name, getattr(item, field.name))
        else:
            # New item
            _VOCAB_MAP[item.word] = item
            if _VOCAB_CACHE is not None:
                _VOCAB_CACHE.append(item)

def update_vocab_item(item: Vocabulary):
    # Same as add since we use INSERT OR REPLACE
    add_vocab_item(item)

def get_vocab_item(word: str) -> Optional[Vocabulary]:
    global _VOCAB_MAP

    if _VOCAB_MAP is not None:
        return _VOCAB_MAP.get(word)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vocabulary WHERE word = ?", (word,))
        row = cursor.fetchone()
        if row:
            return _row_to_vocab(row)
    return None

def get_due_vocab_items(date_str: str) -> List[Vocabulary]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM vocabulary
            WHERE status != 'new'
            AND (due_date IS NULL OR due_date <= ?)
            ORDER BY due_date ASC
        """, (date_str,))
        rows = cursor.fetchall()
        return [_row_to_vocab(row) for row in rows]

def get_random_distractors(exclude_word: str, limit: int = 3) -> List[Vocabulary]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM vocabulary
            WHERE word != ?
            ORDER BY RANDOM()
            LIMIT ?
        """, (exclude_word, limit))
        rows = cursor.fetchall()
        return [_row_to_vocab(row) for row in rows]

def get_vocab_count() -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM vocabulary")
        return cursor.fetchone()[0]

def get_learned_vocab_count() -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM vocabulary WHERE status != 'new'")
        return cursor.fetchone()[0]

def get_random_learned_vocab_item() -> Optional[Vocabulary]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM vocabulary
            WHERE status != 'new'
            ORDER BY RANDOM()
            LIMIT 1
        """)
        row = cursor.fetchone()
        if row:
            return _row_to_vocab(row)
    return None

def load_grammar() -> List[GrammarLesson]:
    if not os.path.exists(GRAMMAR_FILE):
        return []
    with open(GRAMMAR_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        lessons = []
        for item in data:
            examples_data = item.pop('examples', [])
            exercises_data = item.pop('exercises', [])
            examples = [GrammarExample(**ex) for ex in examples_data]
            exercises = [GrammarExercise(**ex) for ex in exercises_data]
            lessons.append(GrammarLesson(examples=examples, exercises=exercises, **item))
        return lessons

def load_curriculum():
    if not os.path.exists(CURRICULUM_FILE):
        return {"units": []}
    with open(CURRICULUM_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

_user_lock = threading.RLock()

def get_user_lock():
    return _user_lock

def load_user_profile() -> UserProfile:
    if not os.path.exists(USER_FILE):
        return UserProfile()
    with _user_lock:
        with open(USER_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return UserProfile(**data)

def save_user_profile(profile: UserProfile):
    with _user_lock:
        # Atomic write: write to temp file then rename
        with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=DATA_DIR, encoding='utf-8') as f:
            json.dump(asdict(profile), f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
            temp_name = f.name
        os.replace(temp_name, USER_FILE)
