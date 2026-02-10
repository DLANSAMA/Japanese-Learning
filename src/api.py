from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import random
from datetime import datetime, timedelta

from .data_manager import load_vocab, save_vocab, load_user_profile, save_user_profile
from .models import Vocabulary, UserProfile
from .quiz import generate_input_question, generate_mc_question
from .gamification import add_xp, update_streak

app = FastAPI(title="Japanese Learning API", version="1.0")

class UserStats(BaseModel):
    xp: int
    level: int
    streak: int
    hearts: int

class QuizQuestionResponse(BaseModel):
    question_id: str
    type: str
    question_text: str
    options: Optional[List[str]] = None

class AnswerRequest(BaseModel):
    question_id: str
    answer: str

class AnswerResponse(BaseModel):
    correct: bool
    correct_answers: List[str]
    explanation: Optional[str] = None
    xp_gained: int = 0
    new_level: int
    new_xp: int

def get_due_vocab():
    vocab = load_vocab()
    now = datetime.now()
    due = []
    for card in vocab:
        if not card.last_review:
            due.append(card)
            continue
        last_date = datetime.strptime(card.last_review, '%Y-%m-%d')
        days_wait = 2 ** card.level
        if now > last_date + timedelta(days=days_wait):
            due.append(card)
    return due, vocab

@app.get("/user", response_model=UserStats)
def get_user_stats():
    profile = load_user_profile()
    return UserStats(
        xp=profile.xp,
        level=profile.level,
        streak=profile.streak,
        hearts=profile.hearts
    )

@app.get("/quiz/vocab", response_model=QuizQuestionResponse)
def get_vocab_question():
    due, all_vocab = get_due_vocab()
    if not due:
        # Fallback to random review if nothing due
        if not all_vocab:
             raise HTTPException(status_code=404, detail="No vocabulary available")
        item = random.choice(all_vocab)
    else:
        item = random.choice(due)

    # Generate ID: "vocab:{word}"
    qid = f"vocab:{item.word}"

    # Generate Question
    if len(all_vocab) >= 4 and random.random() > 0.5:
        q = generate_mc_question(item, all_vocab)
    else:
        q = generate_input_question(item)

    return QuizQuestionResponse(
        question_id=qid,
        type=q.type,
        question_text=q.question_text,
        options=q.options
    )

@app.post("/quiz/answer", response_model=AnswerResponse)
def submit_answer(payload: AnswerRequest):
    vocab = load_vocab()
    profile = load_user_profile()

    # Parse ID
    if not payload.question_id.startswith("vocab:"):
        raise HTTPException(status_code=400, detail="Invalid question ID format")

    word = payload.question_id.split("vocab:", 1)[1]
    item = next((v for v in vocab if v.word == word), None)

    if not item:
        raise HTTPException(status_code=404, detail="Word not found")

    # Check Answer
    # We need to recreate the check logic. The simple check is against meaning.
    correct_answers = [item.meaning.lower()]
    user_ans = payload.answer.strip().lower()
    is_correct = user_ans in correct_answers

    xp_gained = 0
    if is_correct:
        item.level += 1
        item.last_review = datetime.now().strftime('%Y-%m-%d')
        xp_gained = 10
        add_xp(profile, xp_gained)
    else:
        item.level = max(0, item.level - 1)
        item.last_review = datetime.now().strftime('%Y-%m-%d')

    save_vocab(vocab)
    save_user_profile(profile)

    return AnswerResponse(
        correct=is_correct,
        correct_answers=[item.meaning],
        explanation=f"{item.word} ({item.kana}) means '{item.meaning}'",
        xp_gained=xp_gained,
        new_level=profile.level,
        new_xp=profile.xp
    )
