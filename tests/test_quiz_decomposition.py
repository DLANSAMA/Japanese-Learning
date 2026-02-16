import unittest
from src.quiz import decompose_sentence

class TestQuizDecomposition(unittest.TestCase):
    def test_verb_masu(self):
        sentence = "私は食べます。"
        expected = ["私は", "食べ", "ます", "。"]
        self.assertEqual(decompose_sentence(sentence), expected)

    def test_verb_shimasu(self):
        sentence = "私は勉強します。"
        expected = ["私は", "勉強", "します", "。"]
        self.assertEqual(decompose_sentence(sentence), expected)

    def test_noun_desu(self):
        sentence = "これはペンです。"
        expected = ["これは", "ペン", "です", "。"]
        self.assertEqual(decompose_sentence(sentence), expected)

    def test_simple_desu(self):
        sentence = "元気です。"
        expected = ["元気", "です", "。"]
        self.assertEqual(decompose_sentence(sentence), expected)

    def test_unknown_structure(self):
        sentence = "今日はいい天気ですね。"
        self.assertIsNone(decompose_sentence(sentence))

    def test_empty_string(self):
        self.assertIsNone(decompose_sentence(""))

    def test_partial_match(self):
        # Starts with "私は" but doesn't end with "ます。" or "します。" or "です。"
        sentence = "私は行く。"
        self.assertIsNone(decompose_sentence(sentence))

if __name__ == '__main__':
    unittest.main()
