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

    def test_check_answer_japanese_punctuation(self):
        """Test punctuation tolerance for Japanese input."""
        # Canonical sentence without punctuation
        s1 = Sentence(japanese="私は寿司を食べます", romaji="Watashi wa sushi o tabemasu", english="I eat sushi", broken_down=[], level=5)
        # Should pass with various punctuation
        self.assertTrue(check_sentence_answer(s1, "私は寿司を食べます。"))
        self.assertTrue(check_sentence_answer(s1, "私は寿司を食べます！"))
        self.assertTrue(check_sentence_answer(s1, "私は寿司を食べます"))

        # Canonical sentence WITH punctuation
        s2 = Sentence(japanese="元気ですか？", romaji="Genki desu ka", english="How are you?", broken_down=[], level=5)
        # Should pass with or without punctuation
        self.assertTrue(check_sentence_answer(s2, "元気ですか"))
        self.assertTrue(check_sentence_answer(s2, "元気ですか？"))
        self.assertTrue(check_sentence_answer(s2, "元気ですか?")) # half-width

    def test_check_answer_mixed_punctuation(self):
        """Test mixed punctuation scenarios."""
        s = Sentence(japanese="そうですか。", romaji="Sou desu ka.", english="Is that so?", broken_down=[], level=5)
        self.assertTrue(check_sentence_answer(s, "そうですか"))
        self.assertTrue(check_sentence_answer(s, "そうですか。"))
        self.assertTrue(check_sentence_answer(s, "そうですか！")) # Even if meaning slightly changes, we accept it for now as "punctuation shouldn't matter"

    def test_random_get(self):
        s = get_random_sentence(5)
        if s:
            self.assertIsInstance(s, Sentence)
            self.assertLessEqual(s.level, 5)

if __name__ == '__main__':
    unittest.main()
