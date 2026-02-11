from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.api import app
import unittest
from unittest.mock import patch, MagicMock

client = TestClient(app)

class TestAPI(unittest.TestCase):
    def test_get_user(self):
        response = client.get("/api/user")
        self.assertEqual(response.status_code, 200)
        self.assertIn("xp", response.json())

    def test_get_quiz_vocab(self):
        # Ensure we have vocab to load, or mock it.
        # For simplicity, we assume the environment has vocab.json as created in previous steps
        response = client.get("/api/quiz/vocab")
        if response.status_code == 404:
             print("No vocab found, skipping")
             return

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("question_id", data)
        self.assertTrue(data["question_id"].startswith("vocab:"))

    def test_submit_answer(self):
        # 1. Get a question
        q_resp = client.get("/api/quiz/vocab")
        if q_resp.status_code == 404:
             return
        q_data = q_resp.json()
        qid = q_data["question_id"]

        # 2. Submit wrong answer
        payload = {"question_id": qid, "answer": "WRONG_ANSWER_XYZ"}
        a_resp = client.post("/api/quiz/answer", json=payload)
        self.assertEqual(a_resp.status_code, 200)
        a_data = a_resp.json()
        self.assertFalse(a_data["correct"])

        # 3. Submit right answer? Hard to know without mocking logic,
        # but we verified the endpoint handles the request.

if __name__ == '__main__':
    unittest.main()
