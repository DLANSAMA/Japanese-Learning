from typing import List, Optional
import random
from datetime import datetime

from .models import Vocabulary
from .data_manager import load_vocab, save_vocab
from .dictionary import get_recommendations

def get_new_items(limit: int = 5, track: str = "General") -> List[Vocabulary]:
    vocab = load_vocab()
    new_items = [v for v in vocab if v.status == 'new']

    # Filter by Track
    filtered = []
    if track == "General":
        # Prioritize 'core' tags, or fallback to any
        filtered = [v for v in new_items if 'core' in v.tags]
        # If no core items, fallback to any 'new' items for General track
        if not filtered:
             filtered = new_items
    elif track == "Pop Culture":
        filtered = [v for v in new_items if any(t in v.tags for t in ['anime', 'manga', 'game', 'rpg'])]
    elif track == "Business":
        filtered = [v for v in new_items if any(t in v.tags for t in ['finance', 'business', 'office'])]
    else:
        filtered = new_items

    # If not enough items, autopilot from dictionary
    if len(filtered) < limit:
        needed = limit - len(filtered)
        # Exclude existing words to avoid duplicates
        exclude_words = [v.word for v in vocab]

        try:
            recommendations = get_recommendations(track, limit=needed, exclude_words=exclude_words)

            for rec in recommendations:
                # Convert list of meanings to string
                meaning_str = "; ".join(rec['meanings'][:3]) # Limit to top 3 meanings

                new_v = Vocabulary(
                    word=rec['word'],
                    kana=rec['kana'],
                    romaji="", # jamdict doesn't give romaji easily, keep empty
                    meaning=meaning_str,
                    status='new',
                    level=0,
                    tags=[track.lower(), 'autopilot']
                )
                vocab.append(new_v)
                filtered.append(new_v)

            # Save updated vocab
            save_vocab(vocab)

        except Exception as e:
            print(f"Autopilot failed: {e}")

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
