import unittest
from unittest.mock import patch, MagicMock
from src.pitch import get_pitch_pattern, get_moras

class TestPitchPattern(unittest.TestCase):
    def test_get_moras(self):
        """Test mora tokenization."""
        # Simple
        self.assertEqual(get_moras("すし"), ["す", "し"])
        # Small kana
        self.assertEqual(get_moras("とうきょう"), ["と", "う", "きょ", "う"])
        # Sokuon
        self.assertEqual(get_moras("きっぷ"), ["き", "っ", "ぷ"])
        # Choonpu
        self.assertEqual(get_moras("コーヒー"), ["コ", "ー", "ヒ", "ー"])
        # Small kana combo
        self.assertEqual(get_moras("キャ"), ["キャ"])

    def test_mecab_integration_neko(self):
        """Test 'neko' (Cat) -> HL (Atamadaka)."""
        # Neko is Atamadaka [1].
        # Mora 1 (Ne): H
        # Mora 2 (Ko): L
        # Chars: 2. Pattern: HL.
        self.assertEqual(get_pitch_pattern("猫", "ねこ"), "HL")

    def test_mecab_integration_inu(self):
        """Test 'inu' (Dog) -> LH (Heiban)."""
        # Inu is Heiban [0].
        # Mora 1 (I): L
        # Mora 2 (Nu): H
        # Pattern: LH.
        self.assertEqual(get_pitch_pattern("犬", "いぬ"), "LH")

    def test_mecab_integration_taberu(self):
        """Test 'taberu' (Eat) -> LHL (Nakadaka [2])."""
        # Taberu [2].
        # Mora 1 (Ta): L
        # Mora 2 (Be): H (kernel)
        # Mora 3 (Ru): L
        self.assertEqual(get_pitch_pattern("食べる", "たべる"), "LHL")

    def test_small_kana_expansion_tokyo(self):
        """Test 'Tokyo' -> LHHHH (Heiban [0])."""
        # Tokyo [0].
        # Moras: To, u, kyo, u. (4 moras).
        # Kernel 0 -> L H H H.
        # Expansion:
        # To (L) -> 1 char -> L
        # u (H) -> 1 char -> H
        # kyo (H) -> 2 chars -> HH
        # u (H) -> 1 char -> H
        # Result: L H HH H -> LHHHH.
        self.assertEqual(get_pitch_pattern("東京", "とうきょう"), "LHHHH")

    def test_small_kana_expansion_kyou(self):
        """Test 'Kyou' (Today) -> HHL (Atamadaka [1])."""
        # Kyou [1].
        # Moras: Kyo, u. (2 moras).
        # Kernel 1 -> H L.
        # Expansion:
        # Kyo (H) -> 2 chars -> HH
        # u (L) -> 1 char -> L
        # Result: HHL.
        self.assertEqual(get_pitch_pattern("今日", "きょう"), "HHL")

    def test_empty_input(self):
        self.assertEqual(get_pitch_pattern("", ""), "")

    @patch('src.pitch.get_tagger')
    def test_robustness_alternate_index(self, mock_get_tagger):
        """Test adaptive index search (e.g., if accent is at index 17)."""
        # Mock tagger behavior
        mock_tagger = MagicMock()
        mock_node = MagicMock()

        # Simulate a feature string where index 23 is NOT accent (e.g. empty or non-digit),
        # but index 17 IS accent (e.g., '1' for Atamadaka).
        # Schema length usually > 24.
        # Let's make index 23 '*' and index 17 '1'.
        features = ["*"] * 30
        features[17] = "1" # Accent Kernel
        features[23] = "*" # Invalid/Missing

        mock_node.surface = "MockWord"
        mock_node.feature = ",".join(features)
        mock_node.next = None

        mock_tagger.parseToNode.return_value = mock_node
        mock_get_tagger.return_value = mock_tagger

        # Word: "Test" -> "tesu" (2 moras)
        # Kernel 1 (Atamadaka) -> HL.
        # Check if it correctly finds '1' at index 17.
        result = get_pitch_pattern("MockWord", "てす")
        self.assertEqual(result, "HL")

    @patch('src.pitch.get_tagger')
    def test_fallback_logic(self, mock_get_tagger):
        """Test fallback when MeCab fails."""
        # Mock get_tagger to return None or raise exception
        mock_get_tagger.return_value = None

        # Fallback assumes Heiban [0].
        # Word: "Test" -> "tesuto" (3 moras: te, su, to).
        # Heiban: L H H.
        self.assertEqual(get_pitch_pattern("Test", "てすと"), "LHH")

if __name__ == '__main__':
    unittest.main()
