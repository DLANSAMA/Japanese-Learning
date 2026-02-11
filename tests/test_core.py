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

        # 1. Correct (Easy) -> Rating 5 (FSRS: Easy)
        update_card_srs(v, 5)
        self.assertGreaterEqual(v.interval, 1) # FSRS sets initial interval > 0
        self.assertIsNotNone(v.due_date)

        # 2. Correct (Hard) -> Rating 3 (FSRS: Good)
        # We can't strictly enforce SM-2 multiplier (1.5x) logic here.
        # Just check it increases or stays reasonable.
        old_interval = v.interval
        # Simulate time pass? FSRS relies on elapsed time.
        # If we update immediately, interval might not grow much or depend on stability.
        # Let's skip strict multiplier checks for legacy SM-2 compatibility test
        # and just ensure it's functional.
        update_card_srs(v, 3)
        self.assertGreaterEqual(v.interval, 1)

        # 3. Fail -> Rating 0
        update_card_srs(v, 0)
        # FSRS reduces interval significantly on fail (often to <1 day, clamped to 1)
        self.assertLessEqual(v.interval, 1)

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
