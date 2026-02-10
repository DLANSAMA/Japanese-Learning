from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class Vocabulary:
    word: str
    kana: str
    romaji: str
    meaning: str
    level: int = 0
    last_review: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    ease_factor: float = 2.5
    interval: int = 0
    due_date: Optional[str] = None
    status: str = "new" # 'new', 'learning', 'mastered'

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
class UserSettings:
    show_furigana: bool = True
    max_jlpt_level: int = 5
    theme: str = "default"

@dataclass
class UserProfile:
    xp: int = 0
    level: int = 1
    streak: int = 0
    last_login: str = ""
    hearts: int = 5
    completed_lessons: List[str] = field(default_factory=list)
    settings: UserSettings = field(default_factory=UserSettings)
    selected_track: str = "General"

    def __post_init__(self):
        if isinstance(self.settings, dict):
            self.settings = UserSettings(**self.settings)
