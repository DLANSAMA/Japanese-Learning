# Japanese Learning V13: The Grand Opening (Data Injection) 🎆

**Objective:** Fill the database with a complete, verified JLPT N5 curriculum so the user starts with a rich library.

## 1. The Dataset (Genki I + JLPT N5) 📦
**Task:** Create `data/genki_master.json`.
**Content:** ~500 words strictly following **Genki Textbook Lesson 1-12**.
**Source:** Find a Genki vocab CSV or JSON online (GitHub).
- **Structure:**
  - `Lesson 1`: Greetings, Numbers, Time.
  - `Lesson 2`: Shopping, Things.
- **Fields:**
  - `word`: Kanji
  - `kana`: Reading
  - `meaning`: English
  - `genki_chapter`: 1

## 2. The Ingestor 📥
**Script:** `src/seed_genki.py`
**Logic:**
- Wipe existing `vocab.json` (except user progress).
- Load `genki_master.json`.
- Populate `vocab.json` grouped by Chapter.
- **Crucial:** Assign `tags` -> `["core", "genki", "ch1"]`.

## 3. Immediate Execution ⚡
- **Run** the seed script immediately after implementation.
- Ensure the user has a full deck ready to study without waiting for Autopilot.

## 4. Final Polish 💎
- Verify `tts_text` is generated for all 800 words.
- Ensure `FSRS` fields are initialized to 0.
