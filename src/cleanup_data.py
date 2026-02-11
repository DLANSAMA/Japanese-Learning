import json
import os

DATA_FILE = "data/vocab.json"

def cleanup():
    if not os.path.exists(DATA_FILE):
        print(f"Data file {DATA_FILE} not found.")
        return

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error decoding {DATA_FILE}.")
        return

    print(f"Loaded {len(data)} items.")

    # 1. Deduplication
    unique_items = {}
    duplicates = 0

    for item in data:
        # Key by word and kana
        # Handle cases where word might be missing (shouldn't happen but defensive)
        word = item.get("word", "")
        kana = item.get("kana", "")
        key = (word, kana)

        if key in unique_items:
            duplicates += 1
            existing = unique_items[key]

            # Merge logic: prioritize progress
            existing_status = existing.get("status", "new")
            new_status = item.get("status", "new")

            should_replace = False

            if new_status in ["learning", "mastered"] and existing_status == "new":
                should_replace = True
            elif new_status == existing_status:
                # Tie-break with FSRS stability
                if item.get("fsrs_stability", 0) > existing.get("fsrs_stability", 0):
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
        stability = item.get("fsrs_stability")
        if stability is not None and stability < 0:
            item["fsrs_stability"] = 0.0
            sanitized_count += 1

        # Ensure non-negative difficulty
        difficulty = item.get("fsrs_difficulty")
        if difficulty is not None and difficulty < 0:
            item["fsrs_difficulty"] = 0.0
            sanitized_count += 1

        # Ensure retrievability is between 0 and 1 if present
        retrievability = item.get("fsrs_retrievability")
        if retrievability is not None:
             if retrievability < 0:
                 item["fsrs_retrievability"] = 0.0
                 sanitized_count += 1
             elif retrievability > 1:
                 item["fsrs_retrievability"] = 1.0
                 sanitized_count += 1

    if sanitized_count > 0:
        print(f"Sanitized FSRS fields for {sanitized_count} items/fields.")

    # Save
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(cleaned_data)} items to {DATA_FILE}.")

if __name__ == "__main__":
    cleanup()
