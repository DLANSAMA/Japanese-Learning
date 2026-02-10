# Japanese Learning V5: Content Explosion 💥

**Objective:** Scale the database from "Demo" to "Full Course". Aim for JLPT N5 coverage.

## 1. Vocabulary Expansion (Target: 500 Words) 📚
**Task:** Populate `data/vocab.json` with the essential N5 dataset.
**Categories:**
- **Time:** Today, Tomorrow, Morning, Night, Week, Month, Year.
- **Family:** Mother, Father, Sibling, Friend.
- **Places:** Station, School, Park, Store, Hospital.
- **Verbs:** Go, Come, Eat, Drink, Sleep, Wake, Watch, Listen.
- **Adjectives:** Big/Small, Hot/Cold, Good/Bad, Expensive/Cheap.

**Requirement:** Ensure `tags` are set correctly (e.g., `["core", "n5", "time"]`).

## 2. Grammar Engine ⚙️
**Task:** Flesh out `data/grammar.json` (Currently only has 2 lessons).
**MISSING LESSONS (High Priority):**
- **Lesson 2:** Object Marker (を - O).
- **Lesson 3:** Direction/Destination (に/へ - Ni/He).
- **Lesson 4:** Context/Tool (で - De).
- **Lesson 5:** Question Particle (か - Ka).

## 3. Sentence Library (Target: 100 Sentences) 🧱
**Task:** Populate `data/sentences.json`.
- Combine new vocab with grammar points.
- **Examples:**
  - "I go to school." (Watashi wa gakkou ni ikimasu).
  - "I eat an apple." (Ringo o tabemasu).
  - "Is this water?" (Kore wa mizu desu ka?).

## 4. Audio Prep 🎧
- Ensure all new entries have the `tts_text` field populated with Kana reading.

## Execution
- Use a script (`src/seed_data.py`) or manually update the JSON files.
- Ensure existing user progress (`user.json`) is not overwritten/corrupted.

## 5. Feature: Dictionary / Search Mode 🔍
**Problem:** User cannot look up a word they forgot.
**Requirement:** Add `python3 learn.py search "cat"` command.
- **Output:** JSON list of matches (Word, Meaning, Kana).
- **Headless:** Add `--search <query>` flag.
