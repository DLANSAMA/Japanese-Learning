import unittest
from dataclasses import asdict, fields
from src.models import UserProfile, UserSettings

class TestModels(unittest.TestCase):
    def test_default_initialization(self):
        """Test default initialization of UserProfile."""
        p = UserProfile()
        self.assertIsInstance(p.settings, UserSettings)
        self.assertEqual(p.settings.theme, "default")
        self.assertEqual(p.settings.max_jlpt_level, 5)
        self.assertEqual(p.xp, 0)
        self.assertEqual(p.level, 1)
        self.assertEqual(p.completed_lessons, [])

    def test_settings_dict_conversion(self):
        """Test conversion of settings dict to UserSettings object."""
        settings_dict = {
            "theme": "dark",
            "show_furigana": False
        }
        p = UserProfile(settings=settings_dict)
        self.assertIsInstance(p.settings, UserSettings)
        self.assertEqual(p.settings.theme, "dark")
        self.assertFalse(p.settings.show_furigana)
        # Check defaults for missing keys
        self.assertEqual(p.settings.max_jlpt_level, 5)

    def test_settings_object_preservation(self):
        """Test that passing a UserSettings object works correctly."""
        s = UserSettings(theme="cyberpunk", max_jlpt_level=3)
        p = UserProfile(settings=s)
        self.assertIsInstance(p.settings, UserSettings)
        self.assertEqual(p.settings.theme, "cyberpunk")
        self.assertEqual(p.settings.max_jlpt_level, 3)

    def test_partial_settings_dict(self):
        """Test initializing with partial settings dict."""
        settings_dict = {"display_mode": "kana"}
        p = UserProfile(settings=settings_dict)
        self.assertIsInstance(p.settings, UserSettings)
        self.assertEqual(p.settings.display_mode, "kana")
        # Other fields should have defaults
        self.assertEqual(p.settings.theme, "default")

    def test_extra_keys_in_settings(self):
        """Test that extra keys in settings dict are ignored (robustness)."""
        settings_dict = {
            "theme": "edo",
            "non_existent_key": "some_value"
        }
        # This currently raises TypeError, but we want to modify UserProfile to handle it gracefully.
        # So we assert it doesn't raise, and the valid key is set.
        try:
            p = UserProfile(settings=settings_dict)
        except TypeError:
            self.fail("UserProfile initialization failed with extra keys in settings dict")

        self.assertIsInstance(p.settings, UserSettings)
        self.assertEqual(p.settings.theme, "edo")
        # Ensure the extra key didn't break anything (not strictly necessary since UserSettings wouldn't have it)
        # But we can check it's not present if we were inspecting __dict__, but UserSettings is a dataclass.
        self.assertFalse(hasattr(p.settings, "non_existent_key"))

if __name__ == '__main__':
    unittest.main()
