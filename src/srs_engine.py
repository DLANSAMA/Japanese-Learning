import datetime

def update_card_srs(card, performance_rating: int):
    """
    Updates a Vocabulary card's SRS fields in place.
    performance_rating:
      5 - Perfect response (Easy)
      3 - Correct response but struggled (Hard)
      0 - Incorrect response (Fail)
    """
    # 1. Update Interval
    if performance_rating < 3:
        # Failed review -> Reset Interval to 1 day.
        card.interval = 1
        # Reduce ease factor slightly on fail (standard SRS logic)
        card.ease_factor = max(1.3, card.ease_factor - 0.2)
    else:
        # Correct review
        if card.interval == 0:
            card.interval = 1
        else:
            # Prompt: "If Correct (Easy) -> Interval * 2.5", "If Correct (Hard) -> Interval * 1.5"
            multiplier = 2.5 if performance_rating >= 5 else 1.5
            card.interval = int(card.interval * multiplier)

        # Update Ease Factor (standard SM-2 adjustment)
        q = performance_rating
        card.ease_factor = card.ease_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        if card.ease_factor < 1.3:
            card.ease_factor = 1.3

    # 2. Calculate Due Date
    now = datetime.datetime.now()
    due = now + datetime.timedelta(days=card.interval)
    card.due_date = due.strftime('%Y-%m-%d')
    card.last_review = now.strftime('%Y-%m-%d')

    # Update legacy level for UI compatibility
    if performance_rating >= 3:
        card.level += 1
    else:
        card.level = max(0, card.level - 1)
