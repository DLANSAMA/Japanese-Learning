import unittest
from datetime import datetime
from unittest.mock import patch
from src.models import UserProfile
from src.gamification import add_xp, update_streak, XP_PER_LEVEL

class TestGamificationLogic(unittest.TestCase):
    def setUp(self):
        self.profile = UserProfile()
        self.profile.xp = 0
        self.profile.level = 1
        self.profile.streak = 0
        self.profile.last_login = ""

    def test_add_xp_normal(self):
        """Test adding XP without leveling up."""
        add_xp(self.profile, 50)
        self.assertEqual(self.profile.xp, 50)
        self.assertEqual(self.profile.level, 1)

    def test_add_xp_exact_level_up(self):
        """Test adding XP that exactly reaches the level threshold."""
        # Level 1 threshold is 1 * 100 = 100
        add_xp(self.profile, 100)
        self.assertEqual(self.profile.xp, 0)
        self.assertEqual(self.profile.level, 2)

    def test_add_xp_overflow_level_up(self):
        """Test adding XP that exceeds the level threshold."""
        # Level 1 threshold is 100. Adding 150 -> Level 2 with 50 XP.
        add_xp(self.profile, 150)
        self.assertEqual(self.profile.xp, 50)
        self.assertEqual(self.profile.level, 2)

    def test_add_xp_multi_level_up(self):
        """Test adding enough XP for multiple levels."""
        # Level 1 threshold: 100. Level 2 threshold: 200. Total for 2 levels: 300.
        # Adding 400 -> Level 1 (100) -> Level 2 (200) -> Level 3 with 100 remaining?
        # Trace:
        # xp=400, level=1. 400 >= 100. xp-=100 (300), level=2.
        # xp=300, level=2. 300 >= 200. xp-=200 (100), level=3.
        # xp=100, level=3. 100 < 300 (3*100). Stop.
        # Result: Level 3, XP 100.
        add_xp(self.profile, 400)
        self.assertEqual(self.profile.level, 3)
        self.assertEqual(self.profile.xp, 100)

    @patch('src.gamification.datetime')
    def test_streak_first_login(self, mock_datetime):
        """Test streak initialization on first login."""
        mock_datetime.now.return_value = datetime(2023, 1, 1)
        mock_datetime.strptime.side_effect = datetime.strptime

        update_streak(self.profile)
        self.assertEqual(self.profile.streak, 1)
        self.assertEqual(self.profile.last_login, '2023-01-01')

    @patch('src.gamification.datetime')
    def test_streak_same_day(self, mock_datetime):
        """Test streak on same day login."""
        self.profile.last_login = '2023-01-01'
        self.profile.streak = 5

        mock_datetime.now.return_value = datetime(2023, 1, 1)
        mock_datetime.strptime.side_effect = datetime.strptime

        update_streak(self.profile)
        self.assertEqual(self.profile.streak, 5) # Should not change

    @patch('src.gamification.datetime')
    def test_streak_consecutive_day(self, mock_datetime):
        """Test streak increment on consecutive day."""
        self.profile.last_login = '2023-01-01'
        self.profile.streak = 5

        mock_datetime.now.return_value = datetime(2023, 1, 2)
        mock_datetime.strptime.side_effect = datetime.strptime

        update_streak(self.profile)
        self.assertEqual(self.profile.streak, 6)
        self.assertEqual(self.profile.last_login, '2023-01-02')

    @patch('src.gamification.datetime')
    def test_streak_broken(self, mock_datetime):
        """Test streak reset on missed day."""
        self.profile.last_login = '2023-01-01'
        self.profile.streak = 5

        mock_datetime.now.return_value = datetime(2023, 1, 3) # Skipped Jan 2
        mock_datetime.strptime.side_effect = datetime.strptime

        update_streak(self.profile)
        self.assertEqual(self.profile.streak, 1)
        self.assertEqual(self.profile.last_login, '2023-01-03')

if __name__ == '__main__':
    unittest.main()
