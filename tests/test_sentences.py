import unittest
from src.sentence_builder import check_sentence_answer, get_random_sentence, Sentence, load_sentences

class TestSentences(unittest.TestCase):
    def test_loading(self):
        s = load_sentences()
        self.assertIsInstance(s, list)
        if len(s) > 0:
            self.assertIsInstance(s[0], Sentence)

    def test_check_answer(self):
        s = Sentence(japanese="JP", romaji="watashi wa", english="I am", broken_down=[], level=5)

        self.assertTrue(check_sentence_answer(s, "watashi wa"))
        self.assertTrue(check_sentence_answer(s, "Watashi Wa"))
        self.assertTrue(check_sentence_answer(s, "watashiwa")) # Space tolerance
        self.assertFalse(check_sentence_answer(s, "anata wa"))

    def test_random_get(self):
        s = get_random_sentence(5)
        if s:
            self.assertIsInstance(s, Sentence)
            self.assertLessEqual(s.level, 5)

if __name__ == '__main__':
    unittest.main()
