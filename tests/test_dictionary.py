import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.api import app
from src.dictionary import search

client = TestClient(app)

class TestDictionary(unittest.TestCase):

    @patch('src.dictionary.jam.lookup')
    def test_dictionary_search_logic(self, mock_lookup):
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

    @patch('src.api.load_vocab')
    @patch('src.api.save_vocab')
    def test_add_dictionary_item(self, mock_save, mock_load):
        # Mock load_vocab to return empty list
        mock_load.return_value = []

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

        # Verify save_vocab was called
        mock_save.assert_called_once()
        saved_list = mock_save.call_args[0][0]
        self.assertEqual(len(saved_list), 1)
        self.assertEqual(saved_list[0].word, "飲む")
        self.assertEqual(saved_list[0].meaning, "to drink")
        self.assertEqual(saved_list[0].status, "new")

    @patch('src.api.load_vocab')
    def test_add_dictionary_item_duplicate(self, mock_load):
        # Mock load_vocab to return list with existing word
        existing_item = MagicMock()
        existing_item.word = "飲む"
        mock_load.return_value = [existing_item]

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
