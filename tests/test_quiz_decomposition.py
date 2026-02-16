import unittest
from src.quiz import decompose_sentence

class TestQuizDecomposition(unittest.TestCase):
    def test_verb_masu(self):
        sentence = "私は食べます。"
        # MeCab+UniDic typically splits: "私", "は", "食べ", "ます", "。"
        expected = ["私", "は", "食べ", "ます", "。"]
        self.assertEqual(decompose_sentence(sentence), expected)

    def test_verb_shimasu(self):
        sentence = "私は勉強します。"
        # "勉強" + "し" + "ます" + "。"
        expected = ["私", "は", "勉強", "し", "ます", "。"]
        self.assertEqual(decompose_sentence(sentence), expected)

    def test_noun_desu(self):
        sentence = "これはペンです。"
        # "これ", "は", "ペン", "です", "。"
        expected = ["これ", "は", "ペン", "です", "。"]
        self.assertEqual(decompose_sentence(sentence), expected)

    def test_simple_desu(self):
        sentence = "元気です。"
        # "元気", "です", "。"
        expected = ["元気", "です", "。"]
        self.assertEqual(decompose_sentence(sentence), expected)

    def test_complex_sentence(self):
        # Previously impossible: "今日はいい天気ですね。"
        sentence = "今日はいい天気ですね。"
        # Likely: "今日", "は", "いい", "天気", "です", "ね", "。"
        result = decompose_sentence(sentence)
        self.assertIsNotNone(result)
        self.assertIn("今日", result)
        self.assertIn("天気", result)
        self.assertIn("ね", result)

    def test_empty_string(self):
        self.assertIsNone(decompose_sentence(""))

if __name__ == '__main__':
    unittest.main()
