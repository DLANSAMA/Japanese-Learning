# Japanese Learning V8: The Infinite Curriculum ♾️

**Objective:** Move beyond static JSON lists. Dynamically source vocabulary from a massive dictionary based on user interests.

## 1. The Data Source: JMdict 📖
**Task:** Integrate `JMdict` (Open Source Japanese Dictionary).
**Constraint:** DO NOT parse raw XML on every startup. It is too slow.
- **Solution:** Use `jamdict` (Python library) OR download XML and convert to **SQLite** (`data/dictionary.db`) on first run.
- **Library:** Add `jamdict` or `lxml` to requirements.

## 2. Dynamic Track Generation 🚂
**Logic:** Instead of manually curated lists, generate lessons on the fly.
- **Input:** User Track (e.g., "Pop Culture").
- **Process:**
  1.  Query JMdict for words with tags like `slang`, `manga`, `fantasy`, or high frequency words commonly found in that domain.
  2.  Filter by Difficulty (JLPT Level or Frequency).
  3.  Select 5 words not yet in `user.json`.
  4.  Add to User's `vocab.json`.

## 3. "Smart" Selection Algorithm 🧠
- **The Golden Ratio:** 70% Core / 30% Interest.
  - **Study Session (10 items):**
    - 7 items from "Core" (N5 Frequency List, Grammar).
    - 3 items from "Interest Track" (RPG, Anime, Business).
- **Core Track:** Prioritize `news1` / `ichi1` frequency flags and JLPT N5/N4 lists.
- **Interest Track:** Search for tags matching user preference.

## 4. Implementation Plan 🛠️
1.  **Download Script:** `src/download_dict.py` to fetch JMdict (or a lighter `jmdict-simplified` JSON).
2.  **Dictionary Service:** `src/dictionary.py` to query the local file efficiently.
3.  **Study Logic Update:** Modify `study.py`:
    - If `get_new_items()` returns 0 words from curated list...
    - Call `dictionary.get_recommendations(track=profile.track)`.
    - Automatically convert dictionary entries -> `Vocabulary` objects.
    - Save to `vocab.json`.

## 5. Web UI Polish (Apple Quality) 🍏
**Focus:** Abandon TUI polish. Focus on `src/static/index.html`.
**Requirements:**
- **Ruby Text:** Use HTML `<ruby>` tags for Furigana.
  - Correct: `<ruby>猫<rt>ねこ</rt></ruby>`
  - Incorrect: `猫 (ねこ)`
- **Clean Logic:** If `word == kana` (e.g. Hiragana-only words), DO NOT show Furigana.
- **Global Settings Gear:** ⚙️ (Top Right, Sticky).
  - Opens Modal.
  - Toggles:
    - **Display:** [Kanji] | [Furigana] | [Kana]
    - **Romaji:** [Show/Hide]
    - **Audio:** [Auto-Play On/Off]
  - Saves to `user.json` via API.
- **Audio:** Add a 🔈 button next to the word. Uses `tts_text` field.

## 6. Housekeeping 🧹
- **GitIgnore:** Update `.gitignore` to exclude:
  - `data/user.json` (User progress should be local only).
  - `data/*.db` (Dictionary database).
  - `data/*.xml` (Raw dictionary files).
  - `__pycache__/`
  - `venv/`
