
import unittest
import os
import json
from fastapi.testclient import TestClient
from src.api import app
import src.data_manager
from unittest.mock import patch

client = TestClient(app)

class TestCurriculum(unittest.TestCase):
    def test_get_curriculum_endpoint(self):
        """Test the /api/curriculum endpoint returns valid JSON structure."""
        response = client.get("/api/curriculum")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("units", data)
        self.assertIsInstance(data["units"], list)
        if len(data["units"]) > 0:
            unit = data["units"][0]
            self.assertIn("id", unit)
            self.assertIn("title", unit)

    def test_load_curriculum_missing_file(self):
        """Test load_curriculum returns default structure if file is missing."""
        original_file = src.data_manager.CURRICULUM_FILE
        # Use a non-existent file path
        src.data_manager.CURRICULUM_FILE = "non_existent_curriculum.json"
        try:
            result = src.data_manager.load_curriculum()
            self.assertEqual(result, {"units": []})
        finally:
            src.data_manager.CURRICULUM_FILE = original_file

    def test_load_curriculum_success(self):
        """Test load_curriculum returns content if file exists."""
        # Using the real file which we know exists
        result = src.data_manager.load_curriculum()
        self.assertIn("units", result)

if __name__ == '__main__':
    unittest.main()
