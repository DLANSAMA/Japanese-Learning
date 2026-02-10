from typing import List, Optional
import random
from datetime import datetime

from .models import Vocabulary
from .data_manager import load_vocab, save_vocab

def get_new_items(limit: int = 5) -> List[Vocabulary]:
    vocab = load_vocab()
    new_items = [v for v in vocab if v.status == 'new']
    return new_items[:limit]

def mark_as_learning(item: Vocabulary):
    item.status = 'learning'
    item.level = 0
    item.interval = 1
    item.ease_factor = 2.5
    # Do not set due_date yet? Or set it to today?
    # Usually "learning" means we just saw it, so it might be due tomorrow or immediately for a quiz.
    # Prompt says "Word moves from new -> learning (Active Queue)".
    # Let's set it due immediately for the first quiz run? Or tomorrow?
    # Typically you study then quiz immediately.
    # We'll set last_review to now, and due_date to tomorrow (interval 1).
    now = datetime.now()
    item.last_review = now.strftime('%Y-%m-%d')
    # If we want to quiz immediately, we might not set due_date, or set it to today.
    # But get_due_cards checks <= today.
    # Let's set due_date to today so it appears in the quiz queue immediately if the user goes to quiz.
    item.due_date = now.strftime('%Y-%m-%d')

    # We need to save the change to the persistent store.
    # This function modifies the object in memory. The caller (UI loop) needs to save the list.
    return item

def save_study_progress(vocab_list: List[Vocabulary]):
    save_vocab(vocab_list)
