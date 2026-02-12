import unittest
from src.quiz import QuizSession, generate_input_question
from src.models import Vocabulary, UserSettings

class TestSettings(unittest.TestCase):
    def test_furigana_setting(self):
        v = Vocabulary(word="猫", kana="ねこ", romaji="neko", meaning="cat")

        # 1. Furigana ON
        q1 = generate_input_question(v, display_mode="furigana")
        self.assertIn("ねこ", q1.question_text)

        # 2. Kanji Only
        q2 = generate_input_question(v, display_mode="kanji")
        self.assertNotIn("ねこ", q2.question_text)
        self.assertIn("猫", q2.question_text)

    def test_session_settings(self):
        v = Vocabulary(word="A", kana="a", romaji="a", meaning="a")
        settings = UserSettings(display_mode="kanji")
        session = QuizSession(items=[v], all_vocab=[v], settings=settings)

        q = session.next_question()
        # Should not show kana 'a' in parens if kanji mode
        # but here kana is 'a' and word is 'A', so display is just 'A'
        self.assertNotIn("(a)", q.question_text)

if __name__ == '__main__':
    unittest.main()
