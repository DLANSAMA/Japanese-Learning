import random
from typing import List, Optional, Any
from dataclasses import dataclass

from .models import Vocabulary, GrammarLesson, UserSettings, UserProfile
from .sentence_builder import get_random_sentence, check_sentence_answer, Sentence

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

def generate_assemble_question(item: Vocabulary, example_sentence: str) -> Question:
    # Basic Sentence Assembly: Break the example sentence into parts
    # Naive split by spaces usually works for "Watashi wa tabemasu" style simple sentences.
    # But Japanese is continuous.
    # If the example_sentence is Japanese "私は食べます。", we need a tokenizer or simple heuristic.
    # The current `mine_sentence` output is Japanese.
    # Let's assume we want to assemble the Japanese sentence from tokens.

    # Simple Tokenizer for our templates (Space not reliable, but our generator outputs standard forms)
    # Actually, `mine_sentence` outputs "私は食べます。" (No spaces).
    # Hard to tokenize without MeCab.
    # Plan B: Use the English meaning -> User assembles Japanese words?
    # Or: Assemble the Meaning from English words?
    # Prompt: "Bubble Sentence Builder... Translate: I eat sushi. Pool: [Sushi] [o] [Tabemasu]..."
    # This implies assembling Japanese.

    # Since we don't have a tokenizer, let's create a "Constructed" sentence for this purpose
    # OR rely on `sentence_builder.py` logic which has broken_down parts.
    # But this function takes a `Vocabulary` item.

    # Workaround: For now, if we can't easily break down the sentence, fall back to "Input".
    # BUT, we can make a pseudo-assemble for the Word itself if it's a phrase? No.

    # Better approach:
    # 1. Use `mine_sentence` logic to generate the PARTS first, then the sentence.
    # But `mine_sentence` returns a string.
    # Let's parse the simple templates we made.
    # They are predictable: "Watashi", "wa", "[stem]masu".
    # We can fake it by knowing the structure.

    parts = []
    target_sentence = example_sentence

    # Reverse engineer the templates from `sentence_mining.py`
    if "私は" in example_sentence and "ます。" in example_sentence:
        # Verb sentence: "私は" + stem + "ます。"
        # Parts: "私は", stem+"ます" (or split stem and masu?)
        # Let's just split by particles roughly if possible, or character based? No.
        # Let's just provide the full sentence as one block? No point.

        # Let's fallback to `generate_input_question` if we can't generate parts properly without a tokenizer.
        # UNLESS we update `mine_sentence` to return parts?
        # That would be cleaner but requires touching that file again.

        # Let's just create a dummy assemble for the WORD itself + particles?
        # e.g. "Taberu" -> "Tabemasu"
        # Question: "Conjugate to Polite Form"
        # Options: "Tabemasu", "Taberumasu", "Tabe"
        pass

    # Alternative: The prompt says "Assemble... replaces some Input questions".
    # Let's implement it for sentences from `sentence_builder` if available, or just generic Japanese construction?
    # If we are quizzing a VOCAB word "Taberu", asking to translate "I eat" is good.
    # We know the answer is "Watashi wa Tabemasu".
    # Parts: ["Watashi", "wa", "Tabemasu", "Taberu", "ga", "desu"] (distractors).

    # Logic:
    # 1. Generate target sentence (Polite form usually).
    # 2. Split into plausible chunks.
    # 3. Add distractors.

    # Simplified splitting for our templates:
    parts = []
    if "私は" in example_sentence:
        parts.append("私は")
        remainder = example_sentence.replace("私は", "").replace("。", "")
        parts.append(remainder)
        parts.append("。")
    elif "これは" in example_sentence:
        parts.append("これは")
        remainder = example_sentence.replace("これは", "").replace("。", "")
        parts.append(remainder)
        parts.append("。")
    else:
        # Adjective/Default: "X desu"
        parts.append(item.word)
        parts.append("です")
        parts.append("。")

    correct_order = "".join(parts) # Should match example_sentence roughly (ignoring spaces)

    # Distractors
    pool = list(parts)
    distractors = ["が", "を", "ではありません", "か", "の"]
    pool.extend(random.sample(distractors, 3))
    random.shuffle(pool)

    return Question(
        type="assemble",
        question_text=f"Assemble: '{item.meaning}'\n(Hint: {example_sentence})", # Giving hint because tokenization is weak
        correct_answers=[example_sentence],
        options=pool,
        explanation=f"Answer: {example_sentence}",
        context=item
    )

def generate_sentence_question(level: int = 5) -> Optional[Question]:
    sentence = get_random_sentence(level)
    if not sentence:
        return None

    # Shuffle the components for "Assemble" hint
    components = sentence.broken_down[:]
    random.shuffle(components)
    hint = " / ".join(components)

    return Question(
        type="sentence",
        question_text=f"Translate into Japanese (Romaji): '{sentence.english}'\nHint: {hint}",
        correct_answers=[sentence.romaji.lower()],
        explanation=f"Answer: {sentence.romaji}\nJP: {sentence.japanese}",
        context=sentence
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
        # 33% chance of Assemble if sentence exists
        if item.example_sentence and rand_val > 0.66:
            return generate_assemble_question(item, item.example_sentence)
        # 33% chance of Multiple Choice if enough items exist
        elif len(self.all_vocab) >= 4 and rand_val > 0.33:
            return generate_mc_question(item, self.all_vocab, display_mode)
        else:
            return generate_input_question(item, display_mode)

    def check_answer(self, question: Question, user_answer: str) -> bool:
        if question.type == "sentence":
            return check_sentence_answer(question.context, user_answer)

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
            is_correct = user_answer.strip().lower() in [a.lower() for a in question.correct_answers]

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
        is_correct = user_answer.strip().lower() in [a.lower() for a in question.correct_answers]
        if is_correct:
            self.score += 1
        self.total += 1
        return is_correct
