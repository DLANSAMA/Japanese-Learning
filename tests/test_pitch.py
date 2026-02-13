import unittest
from src.pitch import get_pitch_pattern, COMMON_ACCENTS

class TestPitchPattern(unittest.TestCase):
    def test_known_words(self):
        """Test words present in COMMON_ACCENTS."""
        for word, expected_pattern in COMMON_ACCENTS.items():
            self.assertEqual(get_pitch_pattern(word, ""), expected_pattern)

    def test_heuristic_simple(self):
        """Test simple words without small characters."""
        # 2 moras: L H
        self.assertEqual(get_pitch_pattern("sushi", "すし"), "LH")
        # 3 moras: L H H
        self.assertEqual(get_pitch_pattern("watashi", "わたし"), "LHH")

    def test_heuristic_yoon(self):
        """Test words with contracted sounds (yoon)."""
        # "kyo" (きょ) -> 1 mora: H (or L? Implementation returns H for 1 mora)
        self.assertEqual(get_pitch_pattern("kyo", "きょ"), "H")
        # "kyou" (きょう) -> 2 moras: L H
        self.assertEqual(get_pitch_pattern("kyou", "きょう"), "LH")

    def test_heuristic_sokuon(self):
        """Test words with sokuon (small tsu)."""
        # "kippu" (きっぷ) -> 3 moras: L H H
        # Current implementation treats 'っ' as small char (-1 count), so it returns LH (2 moras).
        # This test expects the correct behavior (3 moras).
        self.assertEqual(get_pitch_pattern("kippu", "きっぷ"), "LHH")

    def test_single_mora(self):
        """Test single mora words."""
        # 1 mora: H
        self.assertEqual(get_pitch_pattern("ki", "き"), "H")

    def test_empty_input(self):
        """Test empty input."""
        self.assertEqual(get_pitch_pattern("", ""), "")

if __name__ == '__main__':
    unittest.main()
