import unittest
from unittest.mock import patch
from src.study import get_new_items, mark_as_learning
from src.models import Vocabulary

class TestStudy(unittest.TestCase):
    def test_get_new_items_general(self):
        # Mock load_vocab
        with patch('src.study.load_vocab') as mock_load:
            v1 = Vocabulary(word="A", kana="a", romaji="a", meaning="a", status="new", tags=["core"])
            v2 = Vocabulary(word="B", kana="b", romaji="b", meaning="b", status="new", tags=["rpg"])
            mock_load.return_value = [v1, v2]

            items = get_new_items(limit=5, track="General")
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0].word, "A")

    def test_get_new_items_pop_culture(self):
        with patch('src.study.load_vocab') as mock_load:
            v1 = Vocabulary(word="A", kana="a", romaji="a", meaning="a", status="new", tags=["core"])
            v2 = Vocabulary(word="B", kana="b", romaji="b", meaning="b", status="new", tags=["rpg"])
            mock_load.return_value = [v1, v2]

            items = get_new_items(limit=5, track="Pop Culture")
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0].word, "B")

    def test_mark_as_learning(self):
        v = Vocabulary(word="a", kana="a", romaji="a", meaning="a", status="new")
        mark_as_learning(v)
        self.assertEqual(v.status, 'learning')
        self.assertIsNotNone(v.due_date)

if __name__ == '__main__':
    unittest.main()
