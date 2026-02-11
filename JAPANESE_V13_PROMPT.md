# Japanese Learning V13: The Grand Opening (Data Injection) 🎆

**Objective:** Fill the database with a complete, verified JLPT N5 curriculum so the user starts with a rich library.

## 1. The Dataset 📦
**Task:** Create or download `data/n5_master.json`.
**Content:** ~800 words covering all N5 requirements.
- **Fields:**
  - `word`: Kanji
  - `kana`: Reading
  - `meaning`: English
  - `pitch`: Int (0-5)
  - `strokes`: SVG path data (optional, or fetch on demand)
  - `example`: Context sentence

## 2. The Ingestor 📥
**Script:** `src/seed_n5.py`
**Logic:**
- Check if `vocab.json` has < 100 items.
- If empty/low, load `n5_master.json`.
- Populate `vocab.json` with these items (Status: "new").
- **Crucial:** Assign `track` tags ("core", "n5") so they appear in the General track.

## 3. Immediate Execution ⚡
- **Run** the seed script immediately after implementation.
- Ensure the user has a full deck ready to study without waiting for Autopilot.

## 4. Final Polish 💎
- Verify `tts_text` is generated for all 800 words.
- Ensure `FSRS` fields are initialized to 0.
