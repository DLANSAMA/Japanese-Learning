import sys
import os
import unittest
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.models import Vocabulary
from src.main import get_due_cards

class TestQuizFilter(unittest.TestCase):
    def test_get_due_cards_excludes_new(self):
        v1 = Vocabulary(word="new", kana="n", romaji="n", meaning="n", status="new")
        v2 = Vocabulary(word="learning", kana="l", romaji="l", meaning="l", status="learning", due_date="2020-01-01")

        due = get_due_cards([v1, v2])
        self.assertEqual(len(due), 1)
        self.assertEqual(due[0].word, "learning")

if __name__ == '__main__':
    unittest.main()
