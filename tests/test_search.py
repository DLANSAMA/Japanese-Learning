import unittest
from src.models import Vocabulary
from src.search import search_vocab

class TestSearch(unittest.TestCase):
    def setUp(self):
        self.vocab_list = [
            Vocabulary(word="猫", kana="ねこ", romaji="neko", meaning="cat"),
            Vocabulary(word="犬", kana="いぬ", romaji="inu", meaning="dog"),
            Vocabulary(word="車", kana="くるま", romaji="kuruma", meaning="car")
        ]

    def test_search_meaning(self):
        results = search_vocab("cat", self.vocab_list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['word'], "猫")

    def test_search_kana(self):
        results = search_vocab("いぬ", self.vocab_list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['word'], "犬")

    def test_search_romaji(self):
        results = search_vocab("neko", self.vocab_list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['word'], "猫")

    def test_search_partial(self):
        results = search_vocab("c", self.vocab_list) # 'c' in 'cat' and 'car'
        self.assertEqual(len(results), 2)

    def test_search_no_match(self):
        results = search_vocab("bird", self.vocab_list)
        self.assertEqual(len(results), 0)

if __name__ == '__main__':
    unittest.main()
