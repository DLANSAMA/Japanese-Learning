from fastapi.testclient import TestClient
from src.api import app
import unittest
from unittest.mock import patch, MagicMock

client = TestClient(app)

class TestAPIV7(unittest.TestCase):
    def test_get_settings(self):
        response = client.get("/api/settings")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("track", data)
        self.assertIn("theme", data)

    def test_update_settings(self):
        payload = {"track": "Pop Culture", "theme": "cyberpunk"}
        response = client.post("/api/settings", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["track"], "Pop Culture")

    def test_get_study_items(self):
        # We assume some items exist or mock it.
        # Since logic depends on data files, this is an integration test.
        response = client.get("/api/study")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

if __name__ == '__main__':
    unittest.main()
