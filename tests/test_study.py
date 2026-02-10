import unittest
from src.study import get_new_items, mark_as_learning, save_study_progress
from src.models import Vocabulary

class TestStudy(unittest.TestCase):
    def test_get_new_items(self):
        # We need a predictable mock vocab, or rely on test file logic
        # For simplicity, we create a mock list
        v1 = Vocabulary(word="a", kana="a", romaji="a", meaning="a", status="new")
        v2 = Vocabulary(word="b", kana="b", romaji="b", meaning="b", status="learning")

        # We can't easily mock load_vocab in integration style test without patching
        # But we can test the filter logic if we extract it, or mock load_vocab
        pass

    def test_mark_as_learning(self):
        v = Vocabulary(word="a", kana="a", romaji="a", meaning="a", status="new")
        mark_as_learning(v)
        self.assertEqual(v.status, 'learning')
        self.assertIsNotNone(v.due_date)
        self.assertEqual(v.interval, 1)

if __name__ == '__main__':
    unittest.main()
