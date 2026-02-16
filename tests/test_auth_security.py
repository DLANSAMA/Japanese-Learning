import unittest
from fastapi.testclient import TestClient
from src.api import app
from src.auth import API_KEY

class TestAuthSecurity(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_missing_api_key(self):
        """Test that missing API key returns 401."""
        response = self.client.get("/api/user")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Missing API Key"})

    def test_invalid_api_key(self):
        """Test that invalid API key returns 401."""
        response = self.client.get("/api/user", headers={"X-API-Key": "invalid-key"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid API Key"})

    def test_valid_api_key(self):
        """Test that valid API key returns 200."""
        response = self.client.get("/api/user", headers={"X-API-Key": API_KEY})
        # Note: /api/user might fail for other reasons (like missing profile),
        # but 401 would mean auth failed.
        # If profile is missing it might return 500 or something else, but definitely not 401 if auth is passed.
        # Actually, let's use a simple endpoint if possible. /api/shop seems static.
        response = self.client.get("/api/shop", headers={"X-API-Key": API_KEY})
        self.assertNotEqual(response.status_code, 401)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
