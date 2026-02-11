import unittest
from unittest.mock import patch, MagicMock
from src.study import get_new_items
from src.models import Vocabulary

class TestAutopilot(unittest.TestCase):

    @patch('src.study.load_vocab')
    @patch('src.study.save_vocab')
    @patch('src.study.get_recommendations')
    def test_autopilot_fallback(self, mock_get_recs, mock_save, mock_load):
        # Scenario: No new items available in vocab
        mock_load.return_value = []

        # Mock recommendations
        mock_get_recs.return_value = [
            {"word": "TestWord", "kana": "testkana", "meanings": ["meaning1", "meaning2"]}
        ]

        # Call get_new_items
        new_items = get_new_items(limit=5, track="General")

        # Assertions
        self.assertEqual(len(new_items), 1)
        self.assertEqual(new_items[0].word, "TestWord")
        self.assertEqual(new_items[0].status, "new")
        self.assertIn("autopilot", new_items[0].tags)

        # Verify save_vocab was called with the new item
        mock_save.assert_called_once()
        saved_list = mock_save.call_args[0][0]
        self.assertEqual(len(saved_list), 1)
        self.assertEqual(saved_list[0].word, "TestWord")

    @patch('src.study.load_vocab')
    @patch('src.study.save_vocab')
    @patch('src.study.get_recommendations')
    def test_autopilot_limit(self, mock_get_recs, mock_save, mock_load):
        # Scenario: 2 existing new items, limit 5. Need 3 more.
        existing = [
            Vocabulary(word="Old1", kana="k1", romaji="r1", meaning="m1", status="new", tags=["core"]),
            Vocabulary(word="Old2", kana="k2", romaji="r2", meaning="m2", status="new", tags=["core"])
        ]
        # Make sure they pass the "General" track filter (check for 'core' tag in study.py)
        # study.py: filtered = [v for v in new_items if 'core' in v.tags]

        mock_load.return_value = list(existing) # Return copy

        mock_get_recs.return_value = [
            {"word": "New1", "kana": "nk1", "meanings": ["nm1"]},
            {"word": "New2", "kana": "nk2", "meanings": ["nm2"]},
            {"word": "New3", "kana": "nk3", "meanings": ["nm3"]}
        ]

        # Call get_new_items
        items = get_new_items(limit=5, track="General")

        # Assertions
        self.assertEqual(len(items), 5)
        # First 2 should be existing
        self.assertEqual(items[0].word, "Old1")
        self.assertEqual(items[1].word, "Old2")
        # Next 3 should be new
        self.assertEqual(items[2].word, "New1")

        # Verify save_vocab saved ALL (existing + new)
        mock_save.assert_called_once()
        saved_list = mock_save.call_args[0][0]
        self.assertEqual(len(saved_list), 5)

    @patch('src.dictionary.sqlite3')
    @patch('src.dictionary.jam') # Mock jamdict instance
    def test_get_recommendations_logic(self, mock_jam, mock_sqlite):
        from src.dictionary import get_recommendations

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_sqlite.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock fetchall to return some idseqs
        mock_cursor.fetchall.return_value = [(100,), (101,)]

        # Mock jam.jmdict.get_entry
        mock_entry = MagicMock()
        # Mock kanji forms list items to have .text attribute
        mock_kanji = MagicMock()
        mock_kanji.text = "Word"
        mock_entry.kanji_forms = [mock_kanji]

        mock_kana = MagicMock()
        mock_kana.text = "Kana"
        mock_entry.kana_forms = [mock_kana]

        mock_sense = MagicMock()
        mock_sense.gloss = ["Meaning"]
        mock_entry.senses = [mock_sense]

        mock_jam.jmdict.get_entry.return_value = mock_entry

        # Call
        recs = get_recommendations("General", limit=2)

        # Verify
        self.assertEqual(len(recs), 2)
        self.assertEqual(recs[0]['word'], "Word")
        mock_cursor.execute.assert_called() # SQL was executed

if __name__ == '__main__':
    unittest.main()
