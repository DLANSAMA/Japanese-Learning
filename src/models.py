from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Vocabulary:
    word: str
    kana: str
    romaji: str
    meaning: str
    level: int = 0
    last_review: Optional[str] = None
    tags: List[str] = field(default_factory=list)

@dataclass
class GrammarExample:
    jp: str
    romaji: str
    en: str

@dataclass
class GrammarExercise:
    question: str
    answer: str
    type: str

@dataclass
class GrammarLesson:
    id: str
    title: str
    description: str
    explanation: str
    structure: str
    examples: List[GrammarExample]
    exercises: List[GrammarExercise]

@dataclass
class UserProfile:
    xp: int = 0
    level: int = 1
    streak: int = 0
    last_login: str = ""
    hearts: int = 5
    completed_lessons: List[str] = field(default_factory=list)
