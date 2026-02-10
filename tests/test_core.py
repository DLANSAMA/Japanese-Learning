import sys
import os
import unittest
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.models import UserProfile, Vocabulary, GrammarLesson
from src.gamification import add_xp, update_streak
from src.data_manager import load_vocab, load_grammar, load_user_profile, save_user_profile

class TestCore(unittest.TestCase):
    def test_vocab_loading(self):
        vocab = load_vocab()
        self.assertIsInstance(vocab, list)
        if len(vocab) > 0:
            self.assertIsInstance(vocab[0], Vocabulary)

    def test_grammar_loading(self):
        grammar = load_grammar()
        self.assertIsInstance(grammar, list)
        if len(grammar) > 0:
            self.assertIsInstance(grammar[0], GrammarLesson)

    def test_user_profile(self):
        profile = UserProfile()
        self.assertEqual(profile.xp, 0)
        self.assertEqual(profile.level, 1)

    def test_xp_system(self):
        profile = UserProfile(xp=0, level=1)
        add_xp(profile, 50)
        self.assertEqual(profile.xp, 50)
        self.assertEqual(profile.level, 1)

        add_xp(profile, 60) # Total 110, Level 1 needs 100
        self.assertEqual(profile.xp, 10)
        self.assertEqual(profile.level, 2)

    def test_streak_system(self):
        profile = UserProfile()
        update_streak(profile)
        self.assertEqual(profile.streak, 1)

        # Simulate already logged in today
        old_streak = profile.streak
        update_streak(profile)
        self.assertEqual(profile.streak, old_streak)

if __name__ == '__main__':
    unittest.main()
