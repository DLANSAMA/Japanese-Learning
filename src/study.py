from typing import List, Optional
import random
from datetime import datetime

from .models import Vocabulary
from .data_manager import load_vocab, save_vocab

def get_new_items(limit: int = 5, track: str = "General") -> List[Vocabulary]:
    vocab = load_vocab()
    new_items = [v for v in vocab if v.status == 'new']

    # Filter by Track
    if track == "General":
        # Prioritize 'core' tags, or fallback to any
        # Let's say General means anything OR specific core
        filtered = [v for v in new_items if 'core' in v.tags]
        if not filtered:
             # Fallback if no core items left
             filtered = new_items
    elif track == "Pop Culture":
        filtered = [v for v in new_items if any(t in v.tags for t in ['anime', 'manga', 'game', 'rpg'])]
    elif track == "Business":
        filtered = [v for v in new_items if any(t in v.tags for t in ['finance', 'business', 'office'])]
    else:
        filtered = new_items

    return filtered[:limit]

def mark_as_learning(item: Vocabulary):
    item.status = 'learning'
    item.level = 0
    item.interval = 1
    item.ease_factor = 2.5
    now = datetime.now()
    item.last_review = now.strftime('%Y-%m-%d')
    item.due_date = now.strftime('%Y-%m-%d')

    return item

def save_study_progress(vocab_list: List[Vocabulary]):
    save_vocab(vocab_list)
