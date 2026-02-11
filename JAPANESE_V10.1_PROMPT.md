# Japanese Learning V10.1: Data Hygiene & Cleanup 🧹

**Objective:** Clean up the data directory and ensure we don't commit large dictionary files or user data.

## 1. Data Filtering Logic 🛡️
**Problem:** The dictionary contains many "junk" words (symbols, purely obsolete terms) that Autopilot sometimes picks up despite previous filters.
**Task:** Enhance `src/dictionary.py`.
- **Additional Filters:**
  - Exclude words containing any characters from this block: `!"#$%&'()*+,-./:;<=>?@[\]^_{|}~` (Symbols).
  - Exclude words where `reading` is only 1 character long (unless it's a very common particle/word like "he", "e", "te", "me", "ka", "wa", "ga", "ni", "no", "to", "de", "mo", "ya", "yo").
  - Strictly force `jlpt-n5` or `jlpt-n4` tag for "General" track if available in Jamdict data (check `tags` or `misc`).

## 2. Ignore Dictionary Artifacts 🚫
**Problem:** `jamdict-data` might have been installed or cached in a way that generates large files in the workspace.
**Task:**
- Verify `.gitignore` includes:
  - `*.db`
  - `*.xml`
  - `data/user.json` (User progress)
  - `data/dictionary.db` (if we were using a local one)
  - `__pycache__`
  - `venv/`
  - `server.log`

## 3. Clean  🧼
**Problem:** The current `data/vocab.json` might contain test junk or duplicates.
**Task:** Create a script `src/cleanup_data.py`:
- Load `vocab.json`.
- Remove duplicates (by word + kana).
- Reset FSRS fields if they look corrupted (e.g. negative stability).
- Save clean version.

## 4. Execution 🏃
- Run the cleanup script once.
- Update the code to apply filters.
