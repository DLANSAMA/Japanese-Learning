import unittest
from unittest.mock import patch, MagicMock
from src.quiz import generate_sentence_question, Question
from src.sentence_builder import Sentence

class TestQuizGeneration(unittest.TestCase):
    @patch('src.quiz.get_random_sentence')
    def test_generate_sentence_question_success(self, mock_get_random_sentence):
        # Create a mock sentence
        mock_sentence = Sentence(
            japanese="私は寿司が好きです。",
            romaji="watashi wa sushi ga suki desu",
            english="I like sushi.",
            broken_down=["watashi", "wa", "sushi", "ga", "suki", "desu"],
            level=5
        )
        mock_get_random_sentence.return_value = mock_sentence

        # Call the function
        question = generate_sentence_question(level=5)

        # Assertions
        self.assertIsNotNone(question)
        self.assertIsInstance(question, Question)
        self.assertEqual(question.type, "sentence")
        self.assertIn("I like sushi.", question.question_text)
        self.assertIn("Hint:", question.question_text)
        self.assertEqual(question.correct_answers, ["watashi wa sushi ga suki desu"])
        self.assertEqual(question.context, mock_sentence)

        # Verify hint contains shuffled components
        # Note: Since shuffle is random, we can just check if all components exist in the hint string
        hint_part = question.question_text.split("Hint: ")[1]
        for part in mock_sentence.broken_down:
            self.assertIn(part, hint_part)

    @patch('src.quiz.get_random_sentence')
    def test_generate_sentence_question_none(self, mock_get_random_sentence):
        # Mock returning None (no sentence found)
        mock_get_random_sentence.return_value = None

        # Call the function
        question = generate_sentence_question(level=5)

        # Assertions
        self.assertIsNone(question)

if __name__ == '__main__':
    unittest.main()
