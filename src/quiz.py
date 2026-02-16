import random
import unicodedata
import re
from typing import List, Optional, Any
from dataclasses import dataclass

import MeCab
import unidic_lite

from .models import Vocabulary, GrammarLesson, UserSettings, UserProfile

# Initialize MeCab tagger once
tagger = MeCab.Tagger(f"-d {unidic_lite.DICDIR} -Owakati")

def normalize_answer(text: str) -> str:
    """
    Normalizes text for comparison:
    - NFKC normalization (handles wide/narrow width)
    - Strips punctuation (Japanese and English)
    - Lowercase
    - Strips whitespace
    """
    if not text:
        return ""
    text = unicodedata.normalize('NFKC', text)
    # Remove punctuation
    text = re.sub(r'[.,!?;:。、！？]', '', text)
    return text.strip().lower()

@dataclass
class Question:
    type: str # 'input', 'multiple_choice', 'grammar', 'sentence'
    question_text: str
    correct_answers: List[str] # List of valid answers (e.g. kana, romaji)
    options: Optional[List[str]] = None # For MC
    explanation: Optional[str] = None # Shown after answer
    context: Optional[Any] = None # The Vocabulary, GrammarExercise, or Sentence object

def get_display_text(item: Vocabulary, display_mode: str) -> str:
    if display_mode == "kana":
        return item.kana
    elif display_mode == "kanji":
        return item.word
    else: # furigana or default
        return f"{item.word} ({item.kana})"

def generate_input_question(item: Vocabulary, display_mode: str = "kanji") -> Question:
    display = get_display_text(item, display_mode)
    return Question(
        type="input",
        question_text=f"What is the meaning of: {display}?",
        correct_answers=[item.meaning.lower()],
        explanation=f"{item.word} ({item.kana}) means '{item.meaning}'",
        context=item
    )

def generate_mc_question(item: Vocabulary, all_vocab: List[Vocabulary], display_mode: str = "kanji") -> Question:
    distractors = random.sample([v for v in all_vocab if v.word != item.word], 3)
    options = [d.meaning for d in distractors]
    options.append(item.meaning)
    random.shuffle(options)

    display = get_display_text(item, display_mode)

    return Question(
        type="multiple_choice",
        question_text=f"Select the correct meaning for: {display}",
        correct_answers=[item.meaning.lower()], # Check against lowercase for robustness
        options=options,
        explanation=f"{item.word} means '{item.meaning}'",
        context=item
    )

def decompose_sentence(sentence: str) -> Optional[List[str]]:
    """
    Decomposes a sentence into tokens using MeCab.
    Returns None if the sentence is empty.
    """
    if not sentence:
        return None

    try:
        # MeCab output with -Owakati is space-separated tokens
        result = tagger.parse(sentence).strip()
        if not result:
            return None
        return result.split(" ")
    except Exception:
        return None

def generate_assemble_question(item: Vocabulary, example_sentence: str) -> Optional[Question]:
    parts = decompose_sentence(example_sentence)
    if not parts:
        return None

    # Distractors
    pool = list(parts)
    distractors = ["が", "を", "ではありません", "か", "の"]

    # Ensure unique distractors
    unique_distractors = [d for d in distractors if d not in parts]

    count = min(3, len(unique_distractors))
    if count > 0:
        pool.extend(random.sample(unique_distractors, count))

    random.shuffle(pool)

    return Question(
        type="assemble",
        question_text=f"Assemble the sentence for: '{item.meaning}'",
        correct_answers=[example_sentence],
        options=pool,
        explanation=f"Answer: {example_sentence}",
        context=item
    )

class QuizSession:
    def __init__(self, items: List[Vocabulary], all_vocab: List[Vocabulary], settings: UserSettings = None):
        self.items = items
        self.all_vocab = all_vocab
        self.score = 0
        self.total = 0
        self.current_index = 0
        self.settings = settings or UserSettings()

        # Filter items by JLPT level if settings exist
        if self.settings:
            # Assuming item.level corresponds roughly to mastery, not JLPT.
            # But prompt says "Level Gating: Only show words <= User Level + 1".
            # Let's interpret max_jlpt_level as a ceiling for complexity if tags exist,
            # OR just use the UserProfile level gating logic in main.py.
            # Here we just store settings for display logic.
            pass

    def has_next(self):
        return self.current_index < len(self.items)

    def next_question(self) -> Question:
        item = self.items[self.current_index]
        self.current_index += 1

        display_mode = getattr(self.settings, "display_mode", "kanji")
        # Fallback to show_furigana logic if display_mode not present (for backward compat during migration)
        if not hasattr(self.settings, "display_mode"):
             display_mode = "furigana" if self.settings.show_furigana else "kanji"

        rand_val = random.random()

        # Try to generate an Assemble question (33% chance if sentence exists)
        if item.example_sentence and rand_val > 0.66:
            q = generate_assemble_question(item, item.example_sentence)
            if q:
                return q
            # If decomposition failed, fall through to other types

        # 33% chance of Multiple Choice if enough items exist
        if len(self.all_vocab) >= 4 and rand_val > 0.33:
            return generate_mc_question(item, self.all_vocab, display_mode)

        return generate_input_question(item, display_mode)

    def check_answer(self, question: Question, user_answer: str) -> bool:
        # For assemble, remove spaces from user answer to match target if target has no spaces (Japanese)
        # But if we constructed target with no spaces, and user joined with spaces?
        # script.js does `join(' ')`.
        # So user_answer for assemble has spaces: "私は 食べます 。"
        # But correct_answer is "私は食べます。"

        if question.type == "assemble":
            user_clean = user_answer.replace(" ", "")
            correct_clean = [a.replace(" ", "") for a in question.correct_answers]
            is_correct = user_clean in correct_clean
        else:
            user_norm = normalize_answer(user_answer)
            correct_norm = [normalize_answer(a) for a in question.correct_answers]
            is_correct = user_norm in correct_norm

        if is_correct:
            self.score += 1
        self.total += 1
        return is_correct

class GrammarQuizSession:
    def __init__(self, lesson: GrammarLesson):
        self.lesson = lesson
        self.exercises = lesson.exercises
        self.score = 0
        self.total = 0
        self.current_index = 0

    def has_next(self):
        return self.current_index < len(self.exercises)

    def next_question(self) -> Question:
        ex = self.exercises[self.current_index]
        self.current_index += 1

        return Question(
            type="grammar",
            question_text=ex.question,
            correct_answers=[ex.answer.lower()],
            explanation=f"Correct answer: {ex.answer}",
            context=ex
        )

    def check_answer(self, question: Question, user_answer: str) -> bool:
        user_norm = normalize_answer(user_answer)
        correct_norm = [normalize_answer(a) for a in question.correct_answers]
        is_correct = user_norm in correct_norm
        if is_correct:
            self.score += 1
        self.total += 1
        return is_correct
