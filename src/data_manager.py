import json
import os
import sqlite3
from dataclasses import asdict
from typing import List, Optional
from .models import Vocabulary, GrammarLesson, UserProfile, GrammarExample, GrammarExercise
from .db import get_db, init_db, DB_FILE

DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
VOCAB_FILE = os.path.join(DATA_DIR, 'vocab.json')
GRAMMAR_FILE = os.path.join(DATA_DIR, 'grammar.json')
CURRICULUM_FILE = os.path.join(DATA_DIR, 'curriculum.json')
USER_FILE = os.path.join(DATA_DIR, 'user.json')

# Ensure DB is initialized
init_db()

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
            for v in vocab_list:
                _insert_vocab_item(cursor, v)
            conn.commit()
            print("Migration complete.")

def _insert_vocab_item(cursor, v: Vocabulary):
    data = asdict(v)
    data['tags'] = json.dumps(data['tags'])

    # Generate the placeholders and keys dynamically based on the dataclass fields
    # But hardcoding is safer/faster for now to match schema
    keys = [
        'word', 'kana', 'romaji', 'meaning', 'level', 'last_review', 'tags',
        'ease_factor', 'interval', 'due_date', 'status', 'pos',
        'example_sentence', 'fsrs_stability', 'fsrs_difficulty',
        'fsrs_retrievability', 'fsrs_last_review'
    ]

    placeholders = ', '.join(['?'] * len(keys))
    columns = ', '.join(keys)
    values = [data.get(k) for k in keys]

    cursor.execute(f'''
        INSERT OR REPLACE INTO vocabulary ({columns})
        VALUES ({placeholders})
    ''', values)

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
_migrate_json_to_db()

def load_vocab() -> List[Vocabulary]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vocabulary")
        rows = cursor.fetchall()
        return [_row_to_vocab(row) for row in rows]

def save_vocab(vocab_list: List[Vocabulary]):
    """
    Legacy method: overwrites the entire vocabulary in the DB.
    Optimized to use transaction for speed, but still O(N).
    Prefer using add_vocab_item or update_vocab_item for single items.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vocabulary")
        for v in vocab_list:
            _insert_vocab_item(cursor, v)
        conn.commit()

def add_vocab_item(item: Vocabulary):
    with get_db() as conn:
        cursor = conn.cursor()
        _insert_vocab_item(cursor, item)
        conn.commit()

def update_vocab_item(item: Vocabulary):
    # Same as add since we use INSERT OR REPLACE
    add_vocab_item(item)

def get_vocab_item(word: str) -> Optional[Vocabulary]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vocabulary WHERE word = ?", (word,))
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

def load_user_profile() -> UserProfile:
    if not os.path.exists(USER_FILE):
        return UserProfile()
    with open(USER_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return UserProfile(**data)

def save_user_profile(profile: UserProfile):
    with open(USER_FILE, 'w', encoding='utf-8') as f:
        json.dump(asdict(profile), f, indent=2, ensure_ascii=False)
