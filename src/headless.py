import json
import sys
import random
from dataclasses import asdict
from datetime import datetime

from src.data_manager import load_vocab, save_vocab, load_user_profile, save_user_profile
from src.srs_engine import update_card_srs
from src.quiz import generate_input_question, generate_sentence_question
from src.models import Vocabulary
from src.sentence_builder import check_sentence_answer, Sentence, load_sentences, get_random_sentence

def get_due_vocab(vocab_list):
    today = datetime.now().strftime('%Y-%m-%d')
    due = []
    # Sort vocab by due date to prioritize overdue items
    # If no due date (new item), treat as due now
    sorted_vocab = sorted(vocab_list, key=lambda v: v.due_date if v.due_date else "0000-00-00")

    for card in sorted_vocab:
        # Exclude new items
        if card.status == 'new':
            continue

        if not card.due_date:
            due.append(card)
        elif card.due_date <= today:
            due.append(card)
    return due

def run_headless(args):
    vocab = load_vocab()
    profile = load_user_profile()

    if args.study:
        # Study Mode: Fetch new items
        new_items = [v for v in vocab if v.status == 'new'][:5]

        study_data = []
        for item in new_items:
            # Mark as learning
            item.status = 'learning'
            item.interval = 1
            item.ease_factor = 2.5
            item.due_date = datetime.now().strftime('%Y-%m-%d')

            study_data.append({
                "id": f"vocab:{item.word}",
                "word": item.word,
                "kana": item.kana,
                "meaning": item.meaning,
                "example": "",
                "tts_text": item.kana
            })

        if new_items:
            save_vocab(vocab)

        print(json.dumps({
            "type": "study_session",
            "items": study_data
        }))
        return

    if args.get_stats:
        # Stats Mode
        stats = {
            "type": "stats",
            "xp": profile.xp,
            "level": profile.level,
            "streak": profile.streak
        }
        print(json.dumps(stats))
        return

    # Simple Question Selection Logic
    # 20% Chance of Sentence if sentences exist
    q_type = "vocab"
    q_data = {}
    context = None

    # Try Sentence
    if random.random() < 0.2:
        s = get_random_sentence(profile.settings.max_jlpt_level)
        if s:
            q_type = "sentence"
            context = s
            # Prepare question payload
            q_data = {
                "type": "sentence",
                "question": f"Translate: {s.english}",
                "hint": s.broken_down,
                "id": f"sentence:{s.english[:10]}",
                "tts_text": s.japanese
            }

    # Fallback to Vocab
    if q_type == "vocab":
        if not vocab:
            print(json.dumps({"error": "No vocabulary data found"}))
            return

        # Pick a due item
        due_items = get_due_vocab(vocab)
        if due_items:
             item = random.choice(due_items)
        else:
             # Fallback to random review if nothing due, BUT avoid 'new' items
             learned_items = [v for v in vocab if v.status != 'new']
             if learned_items:
                 item = random.choice(learned_items)
             else:
                 # If everything is new, we can't quiz. Suggest study mode.
                 print(json.dumps({"error": "No learned vocabulary. Please use Study Mode first."}))
                 return

        context = item

        show_furi = profile.settings.show_furigana
        display = f"{item.word} ({item.kana})" if show_furi else item.word

        q_data = {
            "type": "vocab",
            "question": f"Meaning of: {display}",
            "id": f"vocab:{item.word}",
            "tts_text": item.kana
        }

    # 1. Output Question JSON
    print(json.dumps(q_data))
    sys.stdout.flush()

    # 2. Wait for Input JSON
    try:
        # Read a single line
        raw_input = sys.stdin.readline()
        if not raw_input:
            return

        # Handle empty lines or whitespace-only lines as empty answer
        if not raw_input.strip():
            user_input = {"answer": ""}
        else:
            user_input = json.loads(raw_input)

        answer = user_input.get("answer", "")
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON input", "correct": False}))
        return

    # 3. Validation Logic
    is_correct = False
    correct_ans_str = ""

    if q_type == "sentence":
        is_correct = check_sentence_answer(context, answer)
        correct_ans_str = context.romaji
        if is_correct:
            profile.xp += 20
    else:
        # Vocab
        is_correct = answer.strip().lower() == context.meaning.lower()
        correct_ans_str = context.meaning

        # SRS Update
        rating = 5 if is_correct else 0
        update_card_srs(context, rating)
        save_vocab(vocab)

        if is_correct:
            profile.xp += 10
            # Simple streak update
            profile.streak += 1

    save_user_profile(profile)

    # 4. Output Result JSON
    result = {
        "correct": is_correct,
        "correct_answer": correct_ans_str,
        "xp_gained": 20 if (is_correct and q_type == "sentence") else (10 if is_correct else 0),
        "new_xp": profile.xp,
        "new_level": profile.level
    }
    print(json.dumps(result))
