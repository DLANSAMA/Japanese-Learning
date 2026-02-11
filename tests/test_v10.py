import unittest
from unittest.mock import patch, MagicMock
from src.srs_engine import update_card_fsrs
from src.models import Vocabulary
from src.pitch import get_pitch_pattern
import datetime

class TestV10(unittest.TestCase):

    def test_fsrs_scheduling(self):
        v = Vocabulary(word="Test", kana="test", romaji="test", meaning="test", status="new")

        # 1. First Review: Good (3)
        update_card_fsrs(v, 3)

        self.assertIsNotNone(v.fsrs_last_review)
        self.assertGreater(v.fsrs_stability, 0)
        self.assertGreater(v.interval, 0)

        initial_stability = v.fsrs_stability

        # 2. Simulate time passing via _get_now mock
        future = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=2)

        with patch('src.srs_engine._get_now', return_value=future):
            # Second Review: Good (3)
            update_card_fsrs(v, 3)

        self.assertGreater(v.fsrs_stability, initial_stability)

    def test_pitch_pattern(self):
        self.assertEqual(get_pitch_pattern("食べる", "たべる"), "LHHH")
        self.assertEqual(get_pitch_pattern("飲む", "のむ"), "LHL")
        self.assertEqual(get_pitch_pattern("Unknown", "abc"), "LHH")

    @patch('src.api.get_due_vocab')
    @patch('src.api.load_vocab')
    def test_api_includes_pitch(self, mock_load, mock_due):
        v = Vocabulary(word="食べる", kana="たべる", romaji="taberu", meaning="eat", status="learning")
        mock_due.return_value = ([v], [v])

        from fastapi.testclient import TestClient
        from src.api import app
        client = TestClient(app)

        response = client.get("/api/quiz/vocab")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("pitch_pattern", data)
        self.assertEqual(data["pitch_pattern"], "LHHH")

if __name__ == '__main__':
    unittest.main()
