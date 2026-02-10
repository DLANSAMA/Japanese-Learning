from dataclasses import dataclass
from typing import List, Optional
import random
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
SENTENCE_FILE = os.path.join(DATA_DIR, 'sentences.json')

@dataclass
class Sentence:
    japanese: str
    romaji: str
    english: str
    broken_down: List[str]
    level: int

def load_sentences() -> List[Sentence]:
    if not os.path.exists(SENTENCE_FILE):
        return []
    with open(SENTENCE_FILE, 'r') as f:
        data = json.load(f)
        return [Sentence(**item) for item in data]

def check_sentence_answer(sentence: Sentence, user_input: str) -> bool:
    """
    Checks if the user input matches the sentence (Romaji or Kana).
    For now, we focus on Romaji exact match (case-insensitive) or 'broken_down' assembly.
    """
    normalized_input = user_input.strip().lower().replace(" ", "")
    normalized_romaji = sentence.romaji.strip().lower().replace(" ", "")

    # Simple check: does the input match the romaji without spaces?
    if normalized_input == normalized_romaji:
        return True

    # Check against Japanese (if user inputs kana/kanji)
    if user_input.strip() == sentence.japanese:
        return True

    return False

def get_random_sentence(level: int = 5) -> Optional[Sentence]:
    sentences = load_sentences()
    candidates = [s for s in sentences if s.level <= level]
    if not candidates:
        return None
    return random.choice(candidates)
