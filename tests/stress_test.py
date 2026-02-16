import unittest
import os
import sys
import tempfile
import threading
import time
import concurrent.futures
import shutil
import json
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import Vocabulary, UserProfile, UserSettings
import src.data_manager as dm
import src.srs_engine as srs
import src.quiz as quiz
import src.db as db

class StressTest(unittest.TestCase):
    def setUp(self):
        # Create a temp directory for data
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, 'vocab.db')
        self.user_path = os.path.join(self.test_dir, 'user.json')

        # Patch data_manager and db constants
        self.patches = [
            patch('src.data_manager.DB_FILE', self.db_path),
            patch('src.data_manager.USER_FILE', self.user_path),
            patch('src.db.DB_FILE', self.db_path)
        ]
        for p in self.patches:
            p.start()

        # Initialize DB
        # We need to manually init because the module-level init ran with original paths
        db.init_db()

        # Reset globals
        dm._VOCAB_CACHE = None
        dm._VOCAB_MAP = None

    def tearDown(self):
        for p in self.patches:
            p.stop()
        shutil.rmtree(self.test_dir)

    def test_normalization_ime(self):
        """Test Input Normalization with IME-like inputs"""
        print("\n[Stress] Testing Normalization...")
        # Full-width characters (zenkaku)
        self.assertEqual(quiz.normalize_answer("ａｒｉｇａｔｏｕ"), "arigatou")
        # Mixed width
        self.assertEqual(quiz.normalize_answer("Hello！"), "hello")
        # Trailing whitespace (common in IME)
        self.assertEqual(quiz.normalize_answer("sushi "), "sushi")
        # Japanese punctuation
        self.assertEqual(quiz.normalize_answer("はい。"), "はい")
        # Small Tsu (checking if it breaks)
        self.assertEqual(quiz.normalize_answer("ちっと"), "ちっと")

    def test_scale_10k_items(self):
        """Test performance with 10,000 items"""
        print("\n[Stress] Testing Scale (10k items)...")
        # Generate 10k items
        items = []
        for i in range(10000):
            items.append(Vocabulary(
                word=f"word{i}",
                kana=f"kana{i}",
                romaji=f"romaji{i}",
                meaning=f"meaning{i}",
                status="learning",
                due_date="2023-01-01", # Overdue
                interval=1,
                tags=["stress-test"]
            ))

        start_time = time.time()
        # Use bulk insert (save_vocab uses executemany)
        dm.save_vocab(items)
        duration = time.time() - start_time
        print(f"Time to save 10k items: {duration:.4f}s")

        # Test fetch due
        start_time = time.time()
        due = dm.get_due_vocab_items("2024-01-01")
        duration = time.time() - start_time
        print(f"Time to fetch due items (10k overdue): {duration:.4f}s")

        self.assertEqual(len(due), 10000)
        # We expect sqlite to be fast, but object creation might slow it down.
        # Relaxed assertion for CI environments
        self.assertLess(duration, 2.0, "Fetching 10k items should be reasonable")

    def test_concurrency_writes(self):
        """Test concurrent updates to the same item"""
        print("\n[Stress] Testing Concurrency...")
        # Create an item
        v = Vocabulary(word="test", kana="test", romaji="test", meaning="test", status="learning")
        dm.add_vocab_item(v)

        # Function to simulate concurrent review
        def review_item():
            # In a real API call, we:
            # 1. Load item (read)
            # 2. Update item (modify)
            # 3. Save item (write)

            # We must simulate the race: fetch, wait slightly, write.
            # Without a lock on the item/DB, the last write wins, but increments might be lost if logic depended on read.
            # Here we just test if DB locks up or errors.

            try:
                # We need a new connection per thread for sqlite in some modes,
                # but dm.get_db() context manager handles that (creates new conn).
                item = dm.get_vocab_item("test")
                if not item: return "Item not found"
                item.failure_count += 1
                # Simulate processing time
                time.sleep(0.001)
                dm.update_vocab_item(item)
            except Exception as e:
                return str(e)
            return None

        # Run 20 concurrent threads (sqlite default timeout is 5s, so high concurrency might lock)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(review_item) for _ in range(20)]
            results = [f.result() for f in futures]

        # Check for errors
        errors = [r for r in results if r is not None]
        if errors:
            print(f"Concurrency errors found: {len(errors)}")
            # SQLite might throw "database is locked"

        # Check final state
        final_item = dm.get_vocab_item("test")
        print(f"Final failure count (Threads: 20): {final_item.failure_count}")

        # If perfect locking, it should be 20. If race, < 20.
        # We assume it WILL fail to be 20, confirming the vulnerability.
        if final_item.failure_count < 20:
            print("Race condition confirmed: Lost updates occurred.")

    def test_boundary_zero_items(self):
        """Test behavior with 0 items"""
        print("\n[Stress] Testing Boundary (0 items)...")
        dm.save_vocab([])
        due = dm.get_due_vocab_items("2024-01-01")
        self.assertEqual(len(due), 0)

    def test_boundary_max_overdue(self):
        """Test item overdue by 10 years"""
        print("\n[Stress] Testing Boundary (10 years overdue)...")
        v = Vocabulary(
            word="ancient",
            kana="ancient",
            romaji="ancient",
            meaning="ancient",
            status="learning",
            due_date="2010-01-01",
            interval=1
        )
        dm.add_vocab_item(v)

        # Update via SRS (simulate correct answer)
        # srs_engine should handle the large negative delta
        srs.update_card_srs(v, 5) # Easy

        print(f"New interval after 10 years overdue: {v.interval}")
        self.assertGreater(v.interval, 1, "Interval should grow")

    def test_leech_threshold(self):
        """Test Leech Logic boundary"""
        print("\n[Stress] Testing Leech Threshold...")
        v = Vocabulary(word="leech", kana="l", romaji="l", meaning="l", status="learning", failure_count=4)
        dm.add_vocab_item(v)

        # Fail 5th time
        srs.update_card_srs(v, 0) # Fail
        self.assertTrue(v.is_leech)
        self.assertEqual(v.status, "suspended")
        self.assertEqual(v.interval, 0)

if __name__ == '__main__':
    unittest.main()
