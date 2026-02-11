import datetime
from fsrs import Scheduler, Card, Rating
from .models import Vocabulary

# Initialize Global FSRS Scheduler
scheduler = Scheduler()

def _get_now():
    return datetime.datetime.now(datetime.timezone.utc)

def _map_rating(performance_rating: int) -> Rating:
    """
    Maps legacy performance rating (0-5) to FSRS Rating.
    0 -> Again (1)
    1, 2 -> Hard (2) (Unused in current legacy logic but mapping just in case)
    3, 4 -> Good (3)
    5 -> Easy (4)
    """
    if performance_rating <= 0:
        return Rating.Again
    elif performance_rating <= 2:
        return Rating.Hard
    elif performance_rating <= 4:
        return Rating.Good
    else:
        return Rating.Easy

def update_card_fsrs(vocab_item: Vocabulary, performance_rating: int):
    """
    Updates a Vocabulary item using FSRS logic.
    """
    rating = _map_rating(performance_rating)
    now = _get_now()

    # Create FSRS Card from Vocabulary data
    card = Card()

    # If this item has FSRS history, load it
    if vocab_item.fsrs_last_review:
        card.stability = vocab_item.fsrs_stability
        card.difficulty = vocab_item.fsrs_difficulty

        # Calculate elapsed days since last review
        last_review_date = datetime.datetime.fromisoformat(vocab_item.fsrs_last_review)
        if last_review_date.tzinfo is None:
             last_review_date = last_review_date.replace(tzinfo=datetime.timezone.utc)

        card.last_review = last_review_date

        if vocab_item.due_date:
             # Basic conversion
             due_dt = datetime.datetime.strptime(vocab_item.due_date, '%Y-%m-%d').replace(tzinfo=datetime.timezone.utc)
             card.due = due_dt
        else:
             card.due = now

        if vocab_item.interval > 0:
            card.state = 2 # Review
        else:
            card.state = 0 # New

    # Perform Review
    card, review_log = scheduler.review_card(card, rating, review_datetime=now)

    # Update Vocabulary item
    vocab_item.fsrs_stability = card.stability
    vocab_item.fsrs_difficulty = card.difficulty
    vocab_item.fsrs_last_review = now.isoformat()

    vocab_item.due_date = card.due.strftime('%Y-%m-%d')

    delta = card.due - now
    vocab_item.interval = max(1, delta.days)

    if rating != Rating.Again:
        vocab_item.level += 1
    else:
        vocab_item.level = max(0, vocab_item.level - 1)

# Backward compatibility alias
update_card_srs = update_card_fsrs
