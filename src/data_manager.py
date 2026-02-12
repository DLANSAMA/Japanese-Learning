import json
import os
from dataclasses import asdict
from typing import List, Optional
from .models import Vocabulary, GrammarLesson, UserProfile, GrammarExample, GrammarExercise

DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
VOCAB_FILE = os.path.join(DATA_DIR, 'vocab.json')
GRAMMAR_FILE = os.path.join(DATA_DIR, 'grammar.json')
USER_FILE = os.path.join(DATA_DIR, 'user.json')

_VOCAB_CACHE: Optional[List[Vocabulary]] = None

def load_vocab() -> List[Vocabulary]:
    global _VOCAB_CACHE
    if _VOCAB_CACHE is not None:
        return _VOCAB_CACHE

    if not os.path.exists(VOCAB_FILE):
        _VOCAB_CACHE = []
        return _VOCAB_CACHE

    with open(VOCAB_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        _VOCAB_CACHE = [Vocabulary(**item) for item in data]
        return _VOCAB_CACHE

def save_vocab(vocab_list: List[Vocabulary]):
    global _VOCAB_CACHE
    _VOCAB_CACHE = vocab_list
    with open(VOCAB_FILE, 'w', encoding='utf-8') as f:
        data = [asdict(v) for v in vocab_list]
        json.dump(data, f, indent=2, ensure_ascii=False)

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
