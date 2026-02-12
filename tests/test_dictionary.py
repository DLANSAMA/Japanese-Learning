import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.api import app
from src.auth import verify_api_key
from src.dictionary import search

client = TestClient(app)

class TestDictionary(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[verify_api_key] = lambda: True

    def tearDown(self):
        app.dependency_overrides = {}

    @patch('src.dictionary.get_jam')
    def test_dictionary_search_logic(self, mock_get_jam):
        mock_jam = MagicMock()
        mock_get_jam.return_value = mock_jam
        mock_lookup = mock_jam.lookup

        # Mock Jamdict response structure
        mock_result = MagicMock()
        mock_entry = MagicMock()

        # Mock Kanji Form
        mock_kanji = MagicMock()
        mock_kanji.text = "食べる"
        mock_entry.kanji_forms = [mock_kanji]

        # Mock Kana Form
        mock_kana = MagicMock()
        mock_kana.text = "たべる"
        mock_entry.kana_forms = [mock_kana]

        # Mock Senses
        mock_sense = MagicMock()
        mock_sense.gloss = ["to eat"]
        mock_entry.senses = [mock_sense]

        mock_result.entries = [mock_entry]
        mock_lookup.return_value = mock_result

        results = search("taberu")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['word'], "食べる")
        self.assertEqual(results[0]['kana'], "たべる")
        self.assertEqual(results[0]['meanings'], ["to eat"])

    @patch('src.api.search')
    def test_search_api(self, mock_search):
        # This mocks the search function we just tested above
        mock_search.return_value = [
            {"word": "食べる", "kana": "たべる", "meanings": ["to eat"]}
        ]

        response = client.get("/api/dictionary/search?q=taberu")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["word"], "食べる")

    @patch('src.api.get_vocab_item')
    @patch('src.api.add_vocab_item')
    def test_add_dictionary_item(self, mock_add, mock_get):
        # Mock get_vocab_item to return None (not found)
        mock_get.return_value = None

        payload = {
            "word": "飲む",
            "kana": "のむ",
            "meanings": ["to drink"]
        }

        response = client.post("/api/dictionary/add", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["word"], "飲む")

        # Verify add_vocab_item was called
        mock_add.assert_called_once()
        saved_item = mock_add.call_args[0][0]
        self.assertEqual(saved_item.word, "飲む")
        self.assertEqual(saved_item.meaning, "to drink")
        self.assertEqual(saved_item.status, "new")

    @patch('src.api.get_vocab_item')
    def test_add_dictionary_item_duplicate(self, mock_get):
        # Mock get_vocab_item to return existing item
        existing_item = MagicMock()
        existing_item.word = "飲む"
        mock_get.return_value = existing_item

        payload = {
            "word": "飲む",
            "kana": "のむ",
            "meanings": ["to drink"]
        }

        response = client.post("/api/dictionary/add", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Word already in vocabulary", response.json()["detail"])

if __name__ == '__main__':
    unittest.main()
