import unittest
import os
import importlib
from unittest.mock import patch

class TestAPISecurity(unittest.TestCase):
    def test_docs_disabled_in_production(self):
        """Test that docs are disabled when ENVIRONMENT is production"""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            import src.api
            importlib.reload(src.api)
            self.assertIsNone(src.api.app.docs_url)
            self.assertIsNone(src.api.app.redoc_url)
            self.assertIsNone(src.api.app.openapi_url)

    def test_docs_enabled_in_development(self):
        """Test that docs are enabled when ENVIRONMENT is development"""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            import src.api
            importlib.reload(src.api)
            self.assertEqual(src.api.app.docs_url, "/docs")
            self.assertEqual(src.api.app.redoc_url, "/redoc")
            self.assertEqual(src.api.app.openapi_url, "/openapi.json")

    def tearDown(self):
        # Restore default state (development) to avoid affecting other tests
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            import src.api
            importlib.reload(src.api)

if __name__ == '__main__':
    unittest.main()
