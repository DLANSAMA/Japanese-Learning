import random
from typing import List, Optional, Any
from dataclasses import dataclass

from .models import Vocabulary, GrammarLesson

@dataclass
class Question:
    type: str # 'input', 'multiple_choice', 'grammar'
    question_text: str
    correct_answers: List[str] # List of valid answers (e.g. kana, romaji)
    options: Optional[List[str]] = None # For MC
    explanation: Optional[str] = None # Shown after answer
    context: Optional[Any] = None # The Vocabulary or GrammarExercise object

class QuizSession:
    def __init__(self, items: List[Vocabulary], all_vocab: List[Vocabulary]):
        self.items = items
        self.all_vocab = all_vocab
        self.score = 0
        self.total = 0
        self.current_index = 0

    def has_next(self):
        return self.current_index < len(self.items)

    def next_question(self) -> Question:
        item = self.items[self.current_index]
        self.current_index += 1

        # 50% chance of Multiple Choice if enough items exist
        if len(self.all_vocab) >= 4 and random.random() > 0.5:
            return self._generate_mc_question(item)
        else:
            return self._generate_input_question(item)

    def _generate_input_question(self, item: Vocabulary) -> Question:
        return Question(
            type="input",
            question_text=f"What is the meaning of: {item.word} ({item.kana})?",
            correct_answers=[item.meaning.lower()],
            explanation=f"{item.word} ({item.kana}) means '{item.meaning}'",
            context=item
        )

    def _generate_mc_question(self, item: Vocabulary) -> Question:
        distractors = random.sample([v for v in self.all_vocab if v.word != item.word], 3)
        options = [d.meaning for d in distractors]
        options.append(item.meaning)
        random.shuffle(options)

        return Question(
            type="multiple_choice",
            question_text=f"Select the correct meaning for: {item.word}",
            correct_answers=[item.meaning.lower()], # Check against lowercase for robustness
            options=options,
            explanation=f"{item.word} means '{item.meaning}'",
            context=item
        )

    def check_answer(self, question: Question, user_answer: str) -> bool:
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
