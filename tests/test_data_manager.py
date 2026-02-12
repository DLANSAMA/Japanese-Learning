
import unittest
import os
import json
import sqlite3
import shutil
from dataclasses import asdict
from src.models import Vocabulary

# Need to set up environment before importing src.data_manager to avoid side effects?
# No, we can monkeypatch after import, but migration runs on import.
# So we should import, then patch, then run migration manually or test functions.

class TestDataManager(unittest.TestCase):
    def setUp(self):
        # Setup temp directory
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_data_manager_dir')
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)

        self.db_file = os.path.join(self.test_dir, 'vocab.db')
        self.vocab_json = os.path.join(self.test_dir, 'vocab.json')

        # Import modules
        import src.db
        import src.data_manager

        # Patch paths
        self.original_db_file = src.db.DB_FILE
        src.db.DB_FILE = self.db_file

        self.original_vocab_file = src.data_manager.VOCAB_FILE
        src.data_manager.VOCAB_FILE = self.vocab_json

        # Initialize DB in test location
        src.db.init_db()

        # Reload modules? No, just use patched variables.
        # But we need to clear any existing connection or state if any.

    def tearDown(self):
        import src.db
        import src.data_manager
        src.db.DB_FILE = self.original_db_file
        src.data_manager.VOCAB_FILE = self.original_vocab_file

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_add_and_get_item(self):
        from src.data_manager import add_vocab_item, get_vocab_item

        item = Vocabulary(word="test", meaning="test meaning", kana="te-su-to", romaji="test")
        add_vocab_item(item)

        fetched = get_vocab_item("test")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.word, "test")
        self.assertEqual(fetched.meaning, "test meaning")

    def test_update_item(self):
        from src.data_manager import add_vocab_item, update_vocab_item, get_vocab_item

        item = Vocabulary(word="update_test", meaning="original", kana="u", romaji="u")
        add_vocab_item(item)

        item.meaning = "updated"
        update_vocab_item(item)

        fetched = get_vocab_item("update_test")
        self.assertEqual(fetched.meaning, "updated")

    def test_load_all(self):
        from src.data_manager import add_vocab_item, load_vocab

        item1 = Vocabulary(word="one", meaning="1", kana="1", romaji="1")
        item2 = Vocabulary(word="two", meaning="2", kana="2", romaji="2")
        add_vocab_item(item1)
        add_vocab_item(item2)

        vocab_list = load_vocab()
        self.assertEqual(len(vocab_list), 2)
        words = sorted([v.word for v in vocab_list])
        self.assertEqual(words, ["one", "two"])

    def test_migration(self):
        # Create a json file
        data = [
            asdict(Vocabulary(word="migrated", meaning="m", kana="m", romaji="m"))
        ]
        with open(self.vocab_json, 'w') as f:
            json.dump(data, f)

        # Run migration manually since import already happened
        from src.data_manager import _migrate_json_to_db, get_vocab_item

        # Ensure DB is empty first (setUp inits empty DB)

        _migrate_json_to_db()

        fetched = get_vocab_item("migrated")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.word, "migrated")

if __name__ == '__main__':
    unittest.main()
