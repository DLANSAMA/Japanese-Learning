# Japanese Learning V11: Data Ingestion 📥

**Objective:** Implement data ingestion for JLPT vocabulary, Pitch Accent data, and Kanji Stroke Order.

## 1. JLPT Vocabulary Ingestion 📚
**Task:** Create a script `src/ingest.py` to download and parse JLPT vocabulary lists.
- **Source:** `Bluskyo/JLPT_Vocabulary` (GitHub) or similar JSON source.
- **Action:**
    - Download JSON for N5-N1.
    - Normalize to `Vocabulary` model format.
    - Tag entries with `jlpt-n5`, `jlpt-n4`, etc.
    - Merge into `data/vocab.json` (avoiding duplicates).

## 2. Pitch Accent Ingestion 🎵
**Task:** Ingest Pitch Accent data.
- **Source:** `mifunetoshiro/kanjium` (dictionary_pitch.json) or `wadoku-pitch-db`.
- **Action:**
    - Download Pitch Accent database.
    - Create a lookup map: `word + reading -> pitch_pattern` (e.g., "LHH").
    - Save to `data/pitch_accent.json`.
    - Optionally update existing `vocab.json` items with pitch info.

## 3. Kanji Stroke Order Ingestion 🖌️
**Task:** Ingest Kanji Stroke Order (SVG).
- **Source:** `KanjiVG` (GitHub).
- **Action:**
    - Implement a function to fetch SVG for a given Kanji character (using its hex code).
    - Save SVGs to `data/kanji/`.
    - Expose via API.

## 4. API & CLI Integration 🔌
- **CLI:** Add `ingest` command to `learn.py`.
- **API:**
    - `GET /api/pitch/{word}`: Returns pitch pattern.
    - `GET /api/kanji/{char}`: Returns SVG content.

## 5. Verification ✅
- Verify ingestion scripts work (mocked download).
- Verify data format is correct.
