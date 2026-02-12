from fastapi.testclient import TestClient
from src.api import app
import unittest

client = TestClient(app)

class TestSecurityAPI(unittest.TestCase):
    def test_search_long_string(self):
        # Should now return 422
        long_str = "a" * 10000
        response = client.get(f"/api/dictionary/search?q={long_str}")
        self.assertEqual(response.status_code, 422)

    def test_search_empty(self):
        # Should now return 422
        response = client.get("/api/dictionary/search?q=")
        self.assertEqual(response.status_code, 422)

    def test_search_valid(self):
        # Should return 200
        response = client.get("/api/dictionary/search?q=test")
        self.assertEqual(response.status_code, 200)

    def test_add_dictionary_item_long(self):
        # Should return 422
        payload = {
            "word": "a" * 100,
            "kana": "a" * 100,
            "meanings": ["meaning"]
        }
        response = client.post("/api/dictionary/add", json=payload)
        self.assertEqual(response.status_code, 422)
