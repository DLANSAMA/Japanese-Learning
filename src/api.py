from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import random
import os
from datetime import datetime, timedelta

from .data_manager import load_vocab, save_vocab, load_user_profile, save_user_profile
from .models import Vocabulary, UserProfile, UserSettings
from .quiz import generate_input_question, generate_mc_question
from .gamification import add_xp, update_streak
from .srs_engine import update_card_srs
from .study import get_new_items, mark_as_learning
from .dictionary import search

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
    # New fields for frontend rendering
    word: Optional[str] = None
    kana: Optional[str] = None
    romaji: Optional[str] = None

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

class SettingsModel(BaseModel):
    track: str
    theme: str

class StudyConfirmRequest(BaseModel):
    word: str

class DictionaryAddRequest(BaseModel):
    word: str
    kana: str
    meanings: List[str]

def get_due_vocab():
    vocab = load_vocab()
    now = datetime.now()
    today_str = now.strftime('%Y-%m-%d')
    due = []

    sorted_vocab = sorted(vocab, key=lambda v: v.due_date if v.due_date else "0000-00-00")

    for card in sorted_vocab:
        if card.status == 'new':
            continue

        if not card.due_date:
            due.append(card)
        elif card.due_date <= today_str:
            due.append(card)
    return due, vocab

@app.get("/api/user", response_model=UserStats)
def get_user_stats():
    profile = load_user_profile()
    return UserStats(
        xp=profile.xp,
        level=profile.level,
        streak=profile.streak,
        hearts=profile.hearts
    )

@app.get("/api/quiz/vocab", response_model=QuizQuestionResponse)
def get_vocab_question():
    due, all_vocab = get_due_vocab()
    learned_vocab = [v for v in all_vocab if v.status != 'new']

    if not due:
        # Fallback to random review if nothing due
        if not learned_vocab:
             raise HTTPException(status_code=404, detail="No learned vocabulary available. Use Study Mode first.")
        item = random.choice(learned_vocab)
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
        options=q.options,
        word=item.word,
        kana=item.kana,
        romaji=item.romaji
    )

@app.post("/api/quiz/answer", response_model=AnswerResponse)
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
    correct_answers = [item.meaning.lower()]
    user_ans = payload.answer.strip().lower()
    is_correct = user_ans in correct_answers

    xp_gained = 0
    if is_correct:
        item.level += 1
        item.last_review = datetime.now().strftime('%Y-%m-%d')
        xp_gained = 10
        add_xp(profile, xp_gained)
        update_card_srs(item, 5)
    else:
        item.level = max(0, item.level - 1)
        item.last_review = datetime.now().strftime('%Y-%m-%d')
        update_card_srs(item, 0)

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

@app.get("/api/study")
def get_study_items():
    profile = load_user_profile()
    items = get_new_items(limit=5, track=profile.selected_track)
    return items

@app.post("/api/study/confirm")
def confirm_study_item(payload: StudyConfirmRequest):
    vocab = load_vocab()
    item = next((v for v in vocab if v.word == payload.word), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    mark_as_learning(item)
    save_vocab(vocab)
    return {"status": "success", "word": item.word}

@app.get("/api/settings", response_model=SettingsModel)
def get_settings():
    profile = load_user_profile()
    return SettingsModel(track=profile.selected_track, theme=profile.settings.theme)

@app.post("/api/settings")
def update_settings(payload: SettingsModel):
    profile = load_user_profile()
    profile.selected_track = payload.track
    profile.settings.theme = payload.theme
    save_user_profile(profile)
    return {"status": "updated", "track": payload.track, "theme": payload.theme}

@app.get("/api/dictionary/search")
def search_dictionary(q: str):
    return search(q)

@app.post("/api/dictionary/add")
def add_dictionary_item(payload: DictionaryAddRequest):
    vocab = load_vocab()

    # Check if word already exists
    if any(v.word == payload.word for v in vocab):
        raise HTTPException(status_code=400, detail="Word already in vocabulary")

    # Create new Vocabulary item
    # Joining meanings with "; " for storage as string
    meaning_str = "; ".join(payload.meanings)

    new_item = Vocabulary(
        word=payload.word,
        kana=payload.kana,
        romaji="", # romaji not provided by jamdict
        meaning=meaning_str,
        status="new",
        level=0,
        tags=["dictionary-add"]
    )

    vocab.append(new_item)
    save_vocab(vocab)

    return {"status": "success", "word": new_item.word}

# Mount Static Files (Catch-all must be last)
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
