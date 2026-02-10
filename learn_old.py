#!/usr/bin/env python3
import json
import random
import os
from datetime import datetime, timedelta

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data/vocab.json')

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_due_cards(data):
    now = datetime.now()
    due = []
    for card in data:
        last_review = card.get('last_review')
        level = card.get('level', 0)

        if not last_review:
            due.append(card)
            continue

        last_date = datetime.strptime(last_review, '%Y-%m-%d')
        days_wait = 2 ** level # SRS: 1, 2, 4, 8, 16 days

        if now > last_date + timedelta(days=days_wait):
            due.append(card)

    return due

def quiz(data):
    due = get_due_cards(data)
    if not due:
        print("🎉 No cards due for review! Great job!")
        # Optional: Ask if they want to review ahead of time
        return

    random.shuffle(due)
    print(f"📚 {len(due)} cards due for review.\n")

    session_correct = 0
    for card in due:
        print(f"Question: {card['meaning']}")
        answer = input("Answer (Romaji/Kana): ").strip().lower()

        correct_answers = [card['kana'], card['romaji'].lower()]

        if answer in correct_answers:
            print("✅ Correct!")
            card['level'] = card.get('level', 0) + 1
            card['last_review'] = datetime.now().strftime('%Y-%m-%d')
            session_correct += 1
        else:
            print(f"❌ Wrong! It was {card['word']} ({card['kana']} / {card['romaji']})")
            card['level'] = max(0, card.get('level', 0) - 1)
            card['last_review'] = datetime.now().strftime('%Y-%m-%d')

        print("-" * 20)
        save_data(data) # Save after each in case of exit

    print(f"Session complete! Score: {session_correct}/{len(due)}")

def stats(data):
    total = len(data)
    mastered = sum(1 for c in data if c.get('level', 0) >= 5)
    learning = sum(1 for c in data if 0 < c.get('level', 0) < 5)
    new = sum(1 for c in data if c.get('level', 0) == 0)

    print(f"📊 Stats:")
    print(f"Total Cards: {total}")
    print(f"🟢 Mastered: {mastered}")
    print(f"🟡 Learning: {learning}")
    print(f"⚪ New: {new}")

def main():
    data = load_data()
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'stats':
            stats(data)
        elif cmd == 'quiz':
            quiz(data)
        else:
            print("Unknown command. Use 'quiz' or 'stats'.")
    else:
        quiz(data)

if __name__ == "__main__":
    main()
