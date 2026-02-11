# Japanese Learning V11: The Gold Mine (Data Ingestion) 🪙

**Objective:** Replace scraped/generated data with high-quality, verified datasets for N5-N3.

## 1. Vocabulary & Sentences (The Core) 📚
**Source:** JLPT N5-N3 Verified CSVs (e.g., Jisho.org exports or Tanaka Corpus).
**Task:**
- Create `src/ingest.py`.
- Download/Parse provided JSON/CSV files containing:
  - Word, Kana, Meaning.
  - **Context Sentence:** Natural usage (not AI generated).
  - **Audio Ref:** Filename or ID for native audio.

## 2. Pitch Accent Data 🎵
**Source:** `accents.json` (Mecab/NHK derived).
**Task:**
- Add `pitch_pattern` field to `Vocabulary` model (Int: 0=Heiban, 1=Atamadaka, etc).
- Render pitch bars in Web UI (`src/static/index.html`).

## 3. Kanji Stroke Order (SVG) 🖌️
**Source:** KanjiVG (GitHub).
**Task:**
- Download `kanjivg` repository (submodule or zip).
- Expose endpoint `GET /api/kanji/{char}` returning SVG data.
- Render animated strokes in Web UI.

## 4. Implementation Steps
1.  Add `src/ingest.py` script.
2.  Update `Vocabulary` model with `pitch`, `audio_url`, `strokes`.
3.  Update `api.py` to serve SVGs.
