import sys
import os
import unittest
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.srs_engine import _map_rating
from fsrs import Rating

class TestSRSEngine(unittest.TestCase):
    def test_map_rating_again(self):
        """Test mapping for 'Again' rating (<= 0)."""
        self.assertEqual(_map_rating(0), Rating.Again)
        self.assertEqual(_map_rating(-1), Rating.Again)
        self.assertEqual(_map_rating(-100), Rating.Again)

    def test_map_rating_hard(self):
        """Test mapping for 'Hard' rating (1, 2)."""
        self.assertEqual(_map_rating(1), Rating.Hard)
        self.assertEqual(_map_rating(2), Rating.Hard)

    def test_map_rating_good(self):
        """Test mapping for 'Good' rating (3, 4)."""
        self.assertEqual(_map_rating(3), Rating.Good)
        self.assertEqual(_map_rating(4), Rating.Good)

    def test_map_rating_easy(self):
        """Test mapping for 'Easy' rating (>= 5)."""
        self.assertEqual(_map_rating(5), Rating.Easy)
        self.assertEqual(_map_rating(6), Rating.Easy)
        self.assertEqual(_map_rating(100), Rating.Easy)

if __name__ == '__main__':
    unittest.main()
