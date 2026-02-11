# Japanese Learning V8.2: Dynamic Feeder (Autopilot) ✈️

**Objective:** Automatically source new vocabulary from the Dictionary based on the user's selected Track.

## 1. The Feeder Service 🏗️
**File:** `src/feeder.py`
**Task:** Implement a function that queries `jamdict` for words matching specific criteria.

```python
def fetch_recommendations(track: str, count: int = 5, existing_words: set = None):
    # Logic to query Jamdict
    # Return list of Vocabulary objects
```

## 2. Track Logic 🛤️
- **General:** Query words with `common` tag or high frequency (`news1`, `ichi1`).
- **Pop Culture:** Query words with tags: `slang`, `col`, `fam`, `manga`, `anime`.
- **Business:** Query words with tags: `son` (sonkeigo), `ken` (kenjougo), `pol` (polite).
- **Travel:** Query specific keywords: "station", "hotel", "food", "train".

## 3. Integration Hook 🎣
**File:** `src/study.py`
- In `get_new_items()`:
  - Check if `vocab.json` has enough `status="new"` items.
  - If count < 5, call `feeder.fetch_recommendations()`.
  - Save new items to `vocab.json`.
  - Return the mixed batch.

## 4. Safety Checks 🛡️
- **Deduplication:** Ensure we don't add words already in `vocab.json` (check `word` and `kana`).
- **Difficulty Filter:** Prefer words with shorter length (1-4 chars) or lower stroke count if possible (though Jamdict metadata is limited here, stick to Frequency).
