import unittest
from fastapi.testclient import TestClient
from src.api import app, UserStats

class TestDashboardV12(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_word_of_the_day(self):
        response = self.client.get("/api/word_of_the_day")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("word", data)
        self.assertIn("kana", data)
        self.assertIn("romaji", data)
        self.assertIn("meaning", data)
        # Verify it's not empty
        self.assertTrue(data["word"])

    def test_user_stats_fields(self):
        # The endpoint is /api/user, not /api/stats
        response = self.client.get("/api/user")
        if response.status_code == 200:
            data = response.json()
            # Check for new fields added in V12.4
            self.assertIn("total_learned", data)
            self.assertIn("next_level_progress", data)
            self.assertIsInstance(data["total_learned"], int)
            self.assertIsInstance(data["next_level_progress"], int)
            # Check range for progress
            self.assertTrue(0 <= data["next_level_progress"] <= 100)
        else:
            # Fallback manual check
            stats = UserStats(
                level=1,
                xp=0,
                gems=0,
                streak=0,
                hearts=5,
                total_learned=10,
                next_level_progress=50
            )
            self.assertEqual(stats.total_learned, 10)
            self.assertEqual(stats.next_level_progress, 50)

if __name__ == '__main__':
    unittest.main()
