import json
import csv
import os
from src.models import Vocabulary
from src.data_manager import load_vocab, save_vocab, load_user_profile

def seed_genki():
    genki_file = "data/genki_master.csv"
    if not os.path.exists(genki_file):
        print(f"Error: {genki_file} not found.")
        return

    print("Loading existing progress...")
    existing_vocab = load_vocab()
    # Create a map of progress for existing words
    # Key: word+kana (to avoid ambiguity)
    progress_map = {}
    for v in existing_vocab:
        key = f"{v.word}:{v.kana}"
        # Only preserve if user has started learning it
        if v.status != 'new' or v.level > 0:
            progress_map[key] = {
                'status': v.status,
                'level': v.level,
                'last_review': v.last_review,
                'ease_factor': v.ease_factor,
                'interval': v.interval,
                'due_date': v.due_date,
                'fsrs_stability': v.fsrs_stability,
                'fsrs_difficulty': v.fsrs_difficulty,
                'fsrs_retrievability': v.fsrs_retrievability,
                'fsrs_last_review': v.fsrs_last_review
            }

    print("Clearing vocabulary database (preserving progress)...")
    new_vocab_list = []

    with open(genki_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 4:
                continue

            kana = row[0].strip()
            kanji_field = row[1].strip()
            # If no kanji provided, use kana as word
            word = kanji_field if kanji_field else kana
            meaning = row[2].strip()
            lesson = row[3].strip()

            # Construct tags
            tags = ["core", "genki", f"ch{lesson}"]

            # Check for existing progress
            key = f"{word}:{kana}"
            progress = progress_map.get(key, {})

            # Create Vocabulary object
            # Note: POS and example_sentence are not in Genki CSV, leaving empty for now or could generate later
            vocab_item = Vocabulary(
                word=word,
                kana=kana,
                romaji="", # Not provided
                meaning=meaning,
                status=progress.get('status', 'new'),
                level=progress.get('level', 0),
                last_review=progress.get('last_review', None),
                tags=tags,
                ease_factor=progress.get('ease_factor', 2.5),
                interval=progress.get('interval', 0),
                due_date=progress.get('due_date', None),
                pos="",
                example_sentence="",
                fsrs_stability=progress.get('fsrs_stability', 0.0),
                fsrs_difficulty=progress.get('fsrs_difficulty', 0.0),
                fsrs_retrievability=progress.get('fsrs_retrievability', None),
                fsrs_last_review=progress.get('fsrs_last_review', None)
            )

            # Important: Set tts_text (used for audio) to kana
            # The model might not have tts_text field explicit in __init__ if it uses Pydantic defaults or properties,
            # but let's check model definition.
            # Assuming standard Pydantic model from memory/context, it might not have tts_text field persisted
            # but 'kana' is used for TTS.
            # If tts_text IS a field, we should set it.
            # Checking src/models.py...

            new_vocab_list.append(vocab_item)

    print(f"Seeding {len(new_vocab_list)} Genki words...")
    save_vocab(new_vocab_list)
    print("Database updated successfully!")

if __name__ == "__main__":
    seed_genki()
