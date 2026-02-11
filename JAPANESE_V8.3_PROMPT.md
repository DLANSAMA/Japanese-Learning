# Japanese Learning V8.3: Sentence Mining (Zero-Shot) ⛏️

**Objective:** Generate example sentences for new vocabulary without using expensive LLM tokens.

## 1. The Template Engine 📝
**File:** `src/sentence_engine.py`
**Task:** Create a system that slots vocabulary into grammar templates based on Part of Speech (PoS).

**Data Structure:**
```json
[
  {
    "id": "tpl_request",
    "structure": "{Word} をください ({Word} o kudasai)",
    "english": "Please give me {Word}",
    "tags": ["noun", "food", "object"]
  },
  {
    "id": "tpl_location",
    "structure": "{Word} はどこですか ({Word} wa doko desu ka)",
    "english": "Where is {Word}?",
    "tags": ["place", "noun"]
  },
  {
    "id": "tpl_action",
    "structure": "私は {Word} ます (Watashi wa {Word}-masu)",
    "english": "I {Word}",
    "tags": ["verb"]
  }
]
```

## 2. Integration with Dictionary 🔗
**Logic:**
- When `fetch_recommendations` gets a word from Jamdict...
- Check its PoS (noun, verb, adj).
- Pick a matching Template.
- Generate `example` string.
- Save to `Vocabulary` object.

## 4. Quality Control (Hotfix) 🛡️
**Problem:** Autopilot is fetching garbage (e.g., "B").
**Requirement:** Update `dictionary.py` / `feeder.py` to filter results:
- **No Single ASCII chars:** Word must contain Kanji/Kana.
- **Min Length:** > 1 character (unless it's a known particle like 'e').
- **Meaning Check:** Must have a definition length > 2 chars.

## 3. Implementation Plan 🛠️
1.  Create `data/templates.json` with 20+ common N5 patterns.
2.  Implement `generate_example(word, pos)` in `sentence_engine.py`.
3.  Hook into `feeder.py` / `dictionary.py`.

**Result:** Every new word comes with a context sentence instantly.
