# Japanese Learning V3: The Fluency Engine 🇯🇵

**Objective:** Transform the current vocabulary quiz tool into a structured language acquisition system (comparable to Anki/Duolingo mechanics).

## 1. Core Feature: Spaced Repetition System (SRS) 🧠
**Goal:** Optimize review intervals based on user performance.
- **Algorithm:** Implement a standard SRS algorithm (e.g., SM-2 or a simplified Leitner system).
- **Data Model:**
  - Update `user.json` or `progress.json` to track:
    - `streak`: Current daily streak.
    - `ease_factor`: How easy the word is (determines next interval).
    - `interval`: Days until next review.
    - `due_date`: Specific date/time for the next review.
- **Logic:**
  - If Correct (Easy) -> Interval * 2.5
  - If Correct (Hard) -> Interval * 1.5
  - If Wrong -> Reset Interval to 1 day.

## 2. Core Feature: Sentence Construction 🧱
**Goal:** Move beyond isolated words to grammar application.
- **New Data:** Create `data/sentences.json`.
  - Structure: `{ "japanese": "私は寿司を食べます", "romaji": "Watashi wa sushi o tabemasu", "english": "I eat sushi", "broken_down": ["Watashi", "wa", "sushi", "o", "tabemasu"] }`
- **Quiz Type:** "Assemble the Sentence" or "Translate to Japanese".
  - **Input:** User types the sentence (Romaji or Kana accepted).
  - **Validation:** Fuzzy matching or exact match with feedback.

## 3. Core Feature: Headless / Agent API 🤖
**Goal:** Allow external agents (Pip) to interface with the learning logic without the TUI blocking input.
- **Flag:** Add `--api` or `--headless` mode.
- **Output:** JSON format to `stdout`.
  - Example: `python3 learn.py --api --get-question` -> `{ "id": 12, "type": "vocab", "question": "Cat", "answer": "Neko" }`
  - Example: `python3 learn.py --api --submit-answer 12 "Neko"` -> `{ "correct": true, "new_interval": 3 }`
- **Why:** This allows Pip to run quizzes directly in Discord chat without screen-scraping the TUI.

## Implementation Steps
1.  **Refactor `models.py`** to support SRS fields (`due_date`, `interval`).
2.  **Create `srs_engine.py`** to handle the scheduling logic.
3.  **Create `sentence_builder.py`** for the new quiz type.
4.  **Update `main.py`** to handle the `--api` flag for agent integration.
