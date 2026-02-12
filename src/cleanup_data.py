import json
import os
from .data_manager import load_vocab, save_vocab
from .models import Vocabulary

def cleanup():
    # Load from DB via data_manager
    data = load_vocab()
    print(f"Loaded {len(data)} items.")

    # 1. Deduplication
    unique_items = {}
    duplicates = 0

    for item in data:
        # Key by word and kana
        word = item.word
        kana = item.kana
        key = (word, kana)

        if key in unique_items:
            duplicates += 1
            existing = unique_items[key]

            # Merge logic: prioritize progress
            existing_status = existing.status
            new_status = item.status

            should_replace = False

            # Priority: mastered > learning > new
            # If both same, higher stability wins

            # Simple status check
            status_rank = {"new": 0, "learning": 1, "mastered": 2}

            if status_rank.get(new_status, 0) > status_rank.get(existing_status, 0):
                should_replace = True
            elif new_status == existing_status:
                # Tie-break with FSRS stability
                # Using 0.0 as default
                if item.fsrs_stability > existing.fsrs_stability:
                    should_replace = True

            if should_replace:
                unique_items[key] = item
        else:
            unique_items[key] = item

    print(f"Found {duplicates} duplicates.")

    cleaned_data = list(unique_items.values())

    # 2. Sanitize FSRS fields
    sanitized_count = 0
    for item in cleaned_data:
        # Ensure non-negative stability
        if item.fsrs_stability < 0:
            item.fsrs_stability = 0.0
            sanitized_count += 1

        # Ensure non-negative difficulty
        if item.fsrs_difficulty < 0:
            item.fsrs_difficulty = 0.0
            sanitized_count += 1

        # Ensure retrievability is between 0 and 1 if present
        if item.fsrs_retrievability is not None:
             if item.fsrs_retrievability < 0:
                 item.fsrs_retrievability = 0.0
                 sanitized_count += 1
             elif item.fsrs_retrievability > 1:
                 item.fsrs_retrievability = 1.0
                 sanitized_count += 1

    if sanitized_count > 0:
        print(f"Sanitized FSRS fields for {sanitized_count} items/fields.")

    # Save back to DB
    save_vocab(cleaned_data)

    print(f"Saved {len(cleaned_data)} items.")

if __name__ == "__main__":
    cleanup()
