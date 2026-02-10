import json
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.models import Vocabulary
from src.data_manager import load_vocab, save_vocab, VOCAB_FILE

def migrate():
    print("Starting migration...")

    if not os.path.exists(VOCAB_FILE):
        print("No vocab file found.")
        return

    # Load raw JSON to check fields without default values interfering
    with open(VOCAB_FILE, 'r') as f:
        raw_data = json.load(f)

    migrated_count = 0
    updated_data = []

    needs_update = False

    for item in raw_data:
        # Determine status
        status = item.get('status')

        if not status:
            needs_update = True
            # If item has review history (level > 0 or last_review set), mark as 'learning'
            level = item.get('level', 0)
            last_review = item.get('last_review')
            interval = item.get('interval', 0)

            if level >= 5 and interval > 21:
                status = 'mastered'
            elif level > 0 or last_review:
                status = 'learning'
            else:
                status = 'new'

            item['status'] = status
            migrated_count += 1

        updated_data.append(item)

    if needs_update:
        # Save back
        with open(VOCAB_FILE, 'w') as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)
        print(f"Migration complete. Updated {migrated_count} items.")
    else:
        print("No migration needed.")

if __name__ == "__main__":
    migrate()
