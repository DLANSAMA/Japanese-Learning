# Japanese Learning V10.1: Quality Control & Cleanup 🧹

**Objective:** Purge garbage data (e.g., "b") and enforce strict validation for new vocabulary.

## 1. The Filter (Dictionary) 🛡️
**File:** `src/dictionary.py`
**Requirement:** Update `get_recommendations` to strictly reject:
- Words with NO Japanese characters (Kanji/Hiragana/Katakana).
- Single-character words that are purely ASCII/Romaji.
- **Regex:** `[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]` (Must contain at least one).

## 2. The Purge (Database) 🗑️
**File:** `src/cleanup.py` (One-off script)
**Task:**
- Load `data/vocab.json`.
- Iterate and remove any entry where `word` does not match the Japanese Regex.
- Save clean list back to `vocab.json`.

## 3. Fallback Generation 🛡️
**File:** `src/study.py`
**Task:** Ensure `example_sentence` is populated.
- If `mine_sentence` returns empty...
- Use a default template: `これは [Word] です。` (This is [Word]).

## 4. Execution
- Run `cleanup.py` once on startup or via command line.
