
import unittest
from fastapi.testclient import TestClient
from src.api import app

class TestAPISecurity(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_security_headers_present(self):
        """Test that essential security headers are present in responses."""
        response = self.client.get("/api/user")
        # Note: 404 or other errors should also have headers, but let's try a valid endpoint.
        # /api/user might require some setup, so let's use a simpler one like /api/shop which is static-ish
        response = self.client.get("/api/shop")

        # We expect these headers
        self.assertIn("X-Content-Type-Options", response.headers)
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")

        self.assertIn("X-Frame-Options", response.headers)
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")

        self.assertIn("X-XSS-Protection", response.headers)
        self.assertEqual(response.headers["X-XSS-Protection"], "1; mode=block")

        self.assertIn("Referrer-Policy", response.headers)
        self.assertEqual(response.headers["Referrer-Policy"], "strict-origin-when-cross-origin")

    def test_cors_headers(self):
        """Test that CORS headers are set correctly for allowed origins."""
        origin = "http://localhost:3000"
        response = self.client.options(
            "/api/shop",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            }
        )
        # Verify CORS headers
        self.assertIn("access-control-allow-origin", response.headers)
        self.assertEqual(response.headers["access-control-allow-origin"], origin)

if __name__ == '__main__':
    unittest.main()
