
import os
import unittest
import sqlite3
import json
from src.db import init_db, get_db, DB_FILE

class TestDB(unittest.TestCase):
    def setUp(self):
        # Use a temporary DB for testing
        self.original_db_file = DB_FILE
        self.test_db_file = self.original_db_file + '.test'

        # Monkey patch DB_FILE inside src.db
        import src.db
        src.db.DB_FILE = self.test_db_file

        if os.path.exists(self.test_db_file):
            os.remove(self.test_db_file)

        init_db()

    def tearDown(self):
        if os.path.exists(self.test_db_file):
            os.remove(self.test_db_file)
        # Restore
        import src.db
        src.db.DB_FILE = self.original_db_file

    def test_init_db(self):
        self.assertTrue(os.path.exists(self.test_db_file))

        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vocabulary'")
            result = c.fetchone()
            self.assertIsNotNone(result)

    def test_insert_select(self):
        with get_db() as conn:
            c = conn.cursor()
            tags = json.dumps(["tag1", "tag2"])
            c.execute("""
                INSERT INTO vocabulary (word, kana, romaji, meaning, level, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("testword", "testkana", "testromaji", "testmeaning", 1, tags))
            conn.commit()

            c.execute("SELECT * FROM vocabulary WHERE word=?", ("testword",))
            row = c.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row['word'], "testword")
            self.assertEqual(row['level'], 1)
            self.assertEqual(json.loads(row['tags']), ["tag1", "tag2"])

if __name__ == '__main__':
    unittest.main()
