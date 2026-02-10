import sys
import os
import unittest
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.models import UserProfile, Vocabulary, GrammarLesson, UserSettings
from src.srs_engine import update_card_srs

class TestCore(unittest.TestCase):
    def test_srs_fields(self):
        v = Vocabulary(word="a", kana="a", romaji="a", meaning="a")
        self.assertEqual(v.interval, 0)
        self.assertEqual(v.ease_factor, 2.5)
        self.assertIsNone(v.due_date)

    def test_srs_update_logic(self):
        v = Vocabulary(word="a", kana="a", romaji="a", meaning="a")

        # 1. Correct (Easy) -> Rating 5
        update_card_srs(v, 5)
        self.assertEqual(v.interval, 1) # Initial interval 1 day
        self.assertIsNotNone(v.due_date)

        # 2. Correct (Hard) -> Rating 3
        v.interval = 10
        update_card_srs(v, 3)
        self.assertEqual(v.interval, 15) # 10 * 1.5 = 15

        # 3. Fail -> Rating 0
        update_card_srs(v, 0)
        self.assertEqual(v.interval, 1)

    def test_user_settings(self):
        p = UserProfile()
        self.assertTrue(p.settings.show_furigana)
        self.assertEqual(p.settings.max_jlpt_level, 5)
        self.assertEqual(p.settings.theme, "default")

    def test_user_tracks(self):
        p = UserProfile()
        self.assertEqual(p.selected_track, "General")

if __name__ == '__main__':
    unittest.main()
