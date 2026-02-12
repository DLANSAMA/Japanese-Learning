import json
import os
from dataclasses import asdict
from typing import List, Dict, Optional
from .models import Vocabulary, GrammarLesson, UserProfile, GrammarExample, GrammarExercise

DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
VOCAB_FILE = os.path.join(DATA_DIR, 'vocab.json')
GRAMMAR_FILE = os.path.join(DATA_DIR, 'grammar.json')
USER_FILE = os.path.join(DATA_DIR, 'user.json')

# Cache for Vocabulary to avoid reloading on every request
_VOCAB_CACHE: Optional[List[Vocabulary]] = None
_VOCAB_DICT_CACHE: Optional[Dict[str, Vocabulary]] = None
_VOCAB_MTIME: float = 0.0

def load_vocab() -> List[Vocabulary]:
    global _VOCAB_CACHE, _VOCAB_DICT_CACHE, _VOCAB_MTIME

    if not os.path.exists(VOCAB_FILE):
        return []

    try:
        current_mtime = os.path.getmtime(VOCAB_FILE)
    except OSError:
        # Fallback if we can't read mtime
        current_mtime = 0

    if _VOCAB_CACHE is not None and current_mtime == _VOCAB_MTIME:
        return _VOCAB_CACHE

    with open(VOCAB_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        vocab_list = [Vocabulary(**item) for item in data]

        # Update Cache
        _VOCAB_CACHE = vocab_list
        _VOCAB_DICT_CACHE = {v.word: v for v in vocab_list}
        _VOCAB_MTIME = current_mtime

        return _VOCAB_CACHE

def get_vocab_by_word(word: str) -> Optional[Vocabulary]:
    """Efficiently retrieve a vocabulary item by word using cached dictionary."""
    load_vocab() # Ensure cache is fresh
    if _VOCAB_DICT_CACHE:
        return _VOCAB_DICT_CACHE.get(word)
    return None

def save_vocab(vocab_list: List[Vocabulary]):
    global _VOCAB_CACHE, _VOCAB_DICT_CACHE, _VOCAB_MTIME

    with open(VOCAB_FILE, 'w', encoding='utf-8') as f:
        data = [asdict(v) for v in vocab_list]
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Update cache to reflect saved state and avoid reload on next access
    _VOCAB_CACHE = vocab_list
    _VOCAB_DICT_CACHE = {v.word: v for v in vocab_list}
    try:
        _VOCAB_MTIME = os.path.getmtime(VOCAB_FILE)
    except OSError:
        _VOCAB_MTIME = 0

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

def load_user_profile() -> UserProfile:
    if not os.path.exists(USER_FILE):
        return UserProfile()
    with open(USER_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return UserProfile(**data)

def save_user_profile(profile: UserProfile):
    with open(USER_FILE, 'w', encoding='utf-8') as f:
        json.dump(asdict(profile), f, indent=2, ensure_ascii=False)
