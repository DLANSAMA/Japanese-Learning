import unittest
from unittest.mock import patch, MagicMock
from src.cleanup_data import cleanup
from src.models import Vocabulary

class TestCleanup(unittest.TestCase):
    @patch('src.cleanup_data.load_vocab')
    @patch('src.cleanup_data.save_vocab')
    def test_cleanup_logic(self, mock_save, mock_load):
        # Create test data
        v1 = Vocabulary(word="猫", kana="ねこ", romaji="neko", meaning="cat", status="new", fsrs_stability=1.0)
        v2 = Vocabulary(word="猫", kana="ねこ", romaji="neko", meaning="cat", status="learning", fsrs_stability=2.0)
        v3 = Vocabulary(word="犬", kana="いぬ", romaji="inu", meaning="dog", status="new", fsrs_stability=-1.0, fsrs_retrievability=1.5)
        v4 = Vocabulary(word="鳥", kana="とり", romaji="tori", meaning="bird", status="new", fsrs_stability=0.0)

        mock_load.return_value = [v1, v2, v3, v4]

        cleanup()

        # Verify save_vocab called with cleaned data
        mock_save.assert_called_once()
        saved_list = mock_save.call_args[0][0]

        # Check duplicates removed (v1 vs v2 -> v2 kept)
        neko = [item for item in saved_list if item.word == "猫"]
        self.assertEqual(len(neko), 1)
        self.assertEqual(neko[0].status, "learning")
        self.assertEqual(neko[0].fsrs_stability, 2.0)

        # Check invalid FSRS fixed (v3)
        inu = [item for item in saved_list if item.word == "犬"][0]
        self.assertEqual(inu.fsrs_stability, 0.0)
        self.assertEqual(inu.fsrs_retrievability, 1.0)

        # Check normal preserved (v4)
        tori = [item for item in saved_list if item.word == "鳥"][0]
        self.assertEqual(tori.status, "new")

if __name__ == '__main__':
    unittest.main()
