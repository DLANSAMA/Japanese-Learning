# Japanese Learning V8.1: Dictionary Search (Simplified) 🔍

**Objective:** Implement dictionary search using the `jamdict` library. Do NOT manually parse XML files.

## 1. Install Jamdict 📦
**Task:** Add `jamdict` and `jamdict-data` to `requirements.txt`.
- `jamdict` provides the code.
- `jamdict-data` provides the SQLite database (no downloading required!).

## 2. Create Dictionary Service 🧱
**File:** `src/dictionary.py`
**Code:**
```python
from jamdict import Jamdict
jam = Jamdict() # Auto-loads data

def search(query: str):
    # Returns list of definitions
    result = jam.lookup(query)
    return [
        {
            "word": entry.kanji,
            "kana": entry.kana,
            "meanings": [s.gloss for s in entry.senses]
        }
        for entry in result.entries
    ]
```

## 3. Add API Endpoint 🌐
**File:** `src/api.py`
- `GET /api/dictionary/search?q={query}`
- Returns JSON list.

## 4. Add UI Search Bar 🖥️
**File:** `src/static/index.html`
- Add a text input "Search Dictionary".
- On Enter, fetch results and display them in a modal.
- Add an "Add to Study" button next to each result.

**Goal:** Allow the user to find and add any word in the Japanese language.
