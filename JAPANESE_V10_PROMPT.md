# Japanese Learning V10: FSRS & Pitch Accent 🧠🎵

**Objective:** Upgrade the memory algorithm to state-of-the-art FSRS and add Pitch Accent visualization to improve pronunciation.

## 1. Implement FSRS (Free Spaced Repetition Scheduler) 🧠
**Problem:** SM-2 (Anki's old algo) is inefficient. FSRS is the new standard.
**Task:** Replace `src/srs_engine.py` logic with the `fsrs` Python library.
- **Library:** Add `fsrs` to `requirements.txt`.
- **Model Update:** Update `Vocabulary` in `src/models.py` to store FSRS fields:
  - `fsrs_stability` (float)
  - `fsrs_difficulty` (float)
  - `fsrs_retrievability` (float, optional)
  - `fsrs_last_review` (datetime)
- **Logic:**
  - On review, calculate next interval using FSRS scheduler.
  - Map user ratings: 'Again' (1), 'Hard' (2), 'Good' (3), 'Easy' (4).

## 2. Pitch Accent Visualization 🎵
**Problem:** Japanese is a pitch-accent language. Learners need to see the "music" of the word.
**Task:**
- **Backend:** Create `src/pitch.py`.
  - For now, use a **Mock/Heuristic** provider or a small local dictionary (since full dictionaries are huge).
  - Return accent pattern: `Heiban` (0), `Atamadaka` (1), `Nakadaka` (2+), `Odaka` (-1).
  - Or better, return the binary high/low pattern: `LHHHH` (Heiban for 5 mora).
- **Frontend:**
  - Update `src/static/script.js` and `index.html`.
  - Visualizing the pitch:
    - Draw a line over High-pitch moras.
    - Drop the line for the accent downfall.
    - Example: `Taberu` (Atamadaka: HLL) -> Line over `Ta`, drop before `be`.
    - CSS: `.pitch-high { border-top: 2px solid #38bdf8; }`, `.pitch-drop { border-right: 2px solid #38bdf8; height: 10px; }` (Just an idea).

## 3. Integration 🔗
- **API:** Update `/api/quiz/vocab` to include `pitch_pattern`.
- **UI:** Show pitch accent visualization on the **Back** of the card in Study/Quiz mode.

## 4. Tests 🧪
- Test FSRS scheduling (ensure intervals increase/decrease correctly).
- Test Pitch pattern generation (mocked).
