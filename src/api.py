from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from pydantic import BaseModel
from typing import List, Optional
import random
import os
from datetime import datetime, timedelta

from .auth import verify_api_key
from .data_manager import (
    load_vocab, save_vocab, load_user_profile, save_user_profile,
    get_vocab_item, update_vocab_item, add_vocab_item, load_curriculum
)
from .models import Vocabulary, UserProfile, UserSettings
from .quiz import generate_input_question, generate_mc_question
from .gamification import add_xp, update_streak
from .srs_engine import update_card_srs, update_card_fsrs
from .study import get_new_items, mark_as_learning
from .dictionary import search
from .sentence_mining import mine_sentence
from .pitch import get_pitch_pattern

app = FastAPI(title="Japanese Learning API", version="1.0", dependencies=[Depends(verify_api_key)])

# Add CORS Middleware to allow frontend development requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development flexibility
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "testserver"]
)

# CORS Middleware
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserStats(BaseModel):
    xp: int
    level: int
    streak: int
    hearts: int
    gems: int
    total_learned: int
    next_level_progress: int

class QuizQuestionResponse(BaseModel):
    question_id: str
    type: str
    question_text: str
    options: Optional[List[str]] = None
    # New fields for frontend rendering
    word: Optional[str] = None
    kana: Optional[str] = None
    romaji: Optional[str] = None
    pitch_pattern: Optional[str] = None

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
    gems_awarded: int = 0

class SettingsModel(BaseModel):
    track: str
    theme: str
    display_mode: str = "kanji"
    show_romaji: bool = True

class StudyConfirmRequest(BaseModel):
    word: str

class DictionaryAddRequest(BaseModel):
    word: str
    kana: str
    meanings: List[str]

class StudyItemResponse(BaseModel):
    word: str
    kana: str
    romaji: str
    meaning: str
    tags: List[str]
    status: str
    example_sentence: str
    pitch_pattern: str

class ShopItem(BaseModel):
    id: str
    name: str
    description: str
    price: int
    icon: str
    type: str

class BuyRequest(BaseModel):
    item_id: str

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
    vocab = load_vocab()

    # Calculate learned (non-new)
    learned_count = len([v for v in vocab if v.status != 'new'])

    # Calculate progress (Level N requires N * 100 XP)
    xp_required = profile.level * 100
    progress = int((profile.xp / xp_required) * 100) if xp_required > 0 else 0
    progress = min(100, progress)

    return UserStats(
        xp=profile.xp,
        level=profile.level,
        streak=profile.streak,
        hearts=profile.hearts,
        gems=profile.gems,
        total_learned=learned_count,
        next_level_progress=progress
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

    # Get pitch accent
    pitch = get_pitch_pattern(item.word, item.kana)

    return QuizQuestionResponse(
        question_id=qid,
        type=q.type,
        question_text=q.question_text,
        options=q.options,
        word=item.word,
        kana=item.kana,
        romaji=item.romaji,
        pitch_pattern=pitch
    )

@app.post("/api/quiz/answer", response_model=AnswerResponse)
def submit_answer(payload: AnswerRequest):
    profile = load_user_profile()

    # Parse ID
    if not payload.question_id.startswith("vocab:"):
        raise HTTPException(status_code=400, detail="Invalid question ID format")

    word = payload.question_id.split("vocab:", 1)[1]
    item = get_vocab_item(word)

    if not item:
        raise HTTPException(status_code=404, detail="Word not found")

    # Check Answer
    correct_answers = [item.meaning.lower()]
    user_ans = payload.answer.strip().lower()
    is_correct = user_ans in correct_answers

    xp_gained = 0
    gems_awarded = 0
    if is_correct:
        item.level += 1
        item.last_review = datetime.now().strftime('%Y-%m-%d')
        xp_gained = 10

        # Award Gems logic: 1 gem per correct answer (can be tweaked)
        # Or random chance? Let's do 1 gem.
        profile.gems += 1
        gems_awarded = 1

        add_xp(profile, xp_gained)
        # 5 = Easy/Perfect. FSRS will map this to 4 (Easy).
        # Since we don't have finer grain buttons yet, we use max score for Correct.
        update_card_fsrs(item, 5)
    else:
        item.level = max(0, item.level - 1)
        item.last_review = datetime.now().strftime('%Y-%m-%d')
        # 0 = Fail. FSRS maps to 1 (Again).
        update_card_fsrs(item, 0)

    update_vocab_item(item)
    save_user_profile(profile)

    return AnswerResponse(
        correct=is_correct,
        correct_answers=[item.meaning],
        explanation=f"{item.word} ({item.kana}) means '{item.meaning}'",
        xp_gained=xp_gained,
        new_level=profile.level,
        new_xp=profile.xp,
        gems_awarded=gems_awarded
    )

@app.get("/api/study", response_model=List[StudyItemResponse])
def get_study_items():
    profile = load_user_profile()
    items = get_new_items(limit=5, track=profile.selected_track)
    response_items = []
    for item in items:
        pitch = get_pitch_pattern(item.word, item.kana)
        response_items.append(StudyItemResponse(
            word=item.word,
            kana=item.kana,
            romaji=item.romaji,
            meaning=item.meaning,
            tags=item.tags,
            status=item.status,
            example_sentence=item.example_sentence,
            pitch_pattern=pitch
        ))
    return response_items

@app.post("/api/study/confirm")
def confirm_study_item(payload: StudyConfirmRequest):
    item = get_vocab_item(payload.word)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    mark_as_learning(item)
    update_vocab_item(item)
    return {"status": "success", "word": item.word}

@app.get("/api/settings", response_model=SettingsModel)
def get_settings():
    profile = load_user_profile()
    return SettingsModel(
        track=profile.selected_track,
        theme=profile.settings.theme,
        display_mode=getattr(profile.settings, "display_mode", "kanji"),
        show_romaji=getattr(profile.settings, "show_romaji", True)
    )

@app.post("/api/settings")
def update_settings(payload: SettingsModel):
    profile = load_user_profile()
    profile.selected_track = payload.track
    profile.settings.theme = payload.theme
    profile.settings.display_mode = payload.display_mode
    profile.settings.show_romaji = payload.show_romaji
    save_user_profile(profile)
    return {"status": "updated", "track": payload.track, "theme": payload.theme}

@app.get("/api/dictionary/search")
def search_dictionary(q: str):
    return search(q)

@app.post("/api/dictionary/add")
def add_dictionary_item(payload: DictionaryAddRequest):
    # Check if word already exists
    if get_vocab_item(payload.word):
        raise HTTPException(status_code=400, detail="Word already in vocabulary")

    # Create new Vocabulary item
    # Joining meanings with "; " for storage as string
    meaning_str = "; ".join(payload.meanings)

    # Lookup POS to generate sentence
    # We re-search because payload doesn't have POS yet
    # Assuming exact match search is reasonably fast
    results = search(payload.word)
    pos = ""
    if results:
        # Try to find matching entry (kana match too)
        for r in results:
             if r['word'] == payload.word and r['kana'] == payload.kana:
                 pos = r.get('pos', '')
                 break
        if not pos and results:
             pos = results[0].get('pos', '')

    sentence = mine_sentence(payload.word, pos, meaning_str)

    new_item = Vocabulary(
        word=payload.word,
        kana=payload.kana,
        romaji="", # romaji not provided by jamdict
        meaning=meaning_str,
        status="new",
        level=0,
        tags=["dictionary-add"],
        pos=pos,
        example_sentence=sentence
    )

    add_vocab_item(new_item)

    return {"status": "success", "word": new_item.word}

@app.get("/api/curriculum")
def get_curriculum():
    return load_curriculum()

@app.get("/api/shop", response_model=List[ShopItem])
def get_shop_items():
    return [
        ShopItem(id="theme_cyberpunk", name="Cyberpunk Theme", description="Neon lights and dark mode.", price=500, icon="🌆", type="theme"),
        ShopItem(id="theme_edo", name="Edo Period Theme", description="Traditional Japanese aesthetic.", price=1000, icon="🏯", type="theme"),
        ShopItem(id="freeze", name="Streak Freeze", description="Protect your streak for one day.", price=200, icon="🧊", type="powerup")
    ]

@app.get("/api/word_of_the_day", response_model=StudyItemResponse)
def get_word_of_the_day():
    vocab = load_vocab()
    # Filter for N5 (Level 1-5 or similar). Let's just pick any non-new if available, or any.
    # Logic: Prioritize words that are simple.
    # Assuming 'level' field maps to difficulty or jlpt? In models.py level is mastery level.
    # We don't have explicit JLPT field in Vocabulary yet, but tags might have it.

    candidates = [v for v in vocab]
    if not candidates:
        raise HTTPException(status_code=404, detail="No vocabulary available")

    # Use today's date as seed
    seed = datetime.now().strftime('%Y%m%d')
    random.seed(seed)

    item = random.choice(candidates)

    # Reset seed
    random.seed()

    pitch = get_pitch_pattern(item.word, item.kana)
    return StudyItemResponse(
        word=item.word,
        kana=item.kana,
        romaji=item.romaji,
        meaning=item.meaning,
        tags=item.tags,
        status=item.status,
        example_sentence=item.example_sentence,
        pitch_pattern=pitch
    )

@app.post("/api/shop/buy")
def buy_item(payload: BuyRequest):
    profile = load_user_profile()
    items = get_shop_items()
    item = next((i for i in items if i.id == payload.item_id), None)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if payload.item_id in profile.inventory and item.type != "powerup":
        raise HTTPException(status_code=400, detail="Item already owned")

    if profile.gems < item.price:
        raise HTTPException(status_code=400, detail="Not enough gems")

    profile.gems -= item.price

    if item.type == "theme":
        profile.inventory.append(item.id)
        # Auto-equip theme? Or just unlock? Let's just unlock.
    elif item.type == "powerup":
        # logic for powerup
        pass

    save_user_profile(profile)
    return {"status": "success", "gems": profile.gems, "inventory": profile.inventory}

# Mount Static Files (Catch-all must be last)
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
