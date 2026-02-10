import unittest
from src.models import Vocabulary, GrammarLesson, GrammarExercise
from src.quiz import QuizSession, GrammarQuizSession, Question

class TestQuiz(unittest.TestCase):
    def setUp(self):
        self.vocab_list = [
            Vocabulary(word="A", kana="a", romaji="a", meaning="Apple"),
            Vocabulary(word="B", kana="b", romaji="b", meaning="Banana"),
            Vocabulary(word="C", kana="c", romaji="c", meaning="Cherry"),
            Vocabulary(word="D", kana="d", romaji="d", meaning="Date"),
            Vocabulary(word="E", kana="e", romaji="e", meaning="Elderberry")
        ]
        self.lesson = GrammarLesson(
            id="g1", title="Test", description="Desc", explanation="Exp", structure="Struct",
            examples=[],
            exercises=[
                GrammarExercise(question="Q1", answer="A1", type="text"),
                GrammarExercise(question="Q2", answer="A2", type="text")
            ]
        )

    def test_quiz_session_vocab(self):
        session = QuizSession(items=self.vocab_list[:2], all_vocab=self.vocab_list)
        self.assertTrue(session.has_next())

        q1 = session.next_question()
        self.assertIsInstance(q1, Question)
        self.assertTrue(q1.question_text)

        # Check answer logic
        # For input question
        if q1.type == "input":
            self.assertTrue(session.check_answer(q1, q1.correct_answers[0]))
            self.assertFalse(session.check_answer(q1, "Wrong"))
        elif q1.type == "multiple_choice":
            self.assertTrue(session.check_answer(q1, q1.correct_answers[0]))
            self.assertFalse(session.check_answer(q1, "Wrong"))

        self.assertEqual(session.score, 1)
        self.assertEqual(session.total, 2) # check_answer called twice

    def test_grammar_quiz_session(self):
        session = GrammarQuizSession(self.lesson)
        self.assertTrue(session.has_next())

        q1 = session.next_question()
        self.assertEqual(q1.question_text, "Q1")
        self.assertEqual(q1.correct_answers[0], "a1") # logic lowercases answer

        self.assertTrue(session.check_answer(q1, "A1"))
        self.assertEqual(session.score, 1)

if __name__ == '__main__':
    unittest.main()
