# Japanese Learning V10: The Scholar (Deep Learning) 🎓

**Objective:** Implement advanced pedagogical features (FSRS, Pitch Accent) to rival top-tier apps like Bunpro/Migaku.

## 1. FSRS Algorithm (Memory Engine) 🧠
**Problem:** SM-2 is outdated. FSRS (Free Spaced Repetition Scheduler) is the new gold standard.
**Task:** Replace `src/srs_engine.py` with FSRS logic.
- **Inputs:** Difficulty, Stability, Retrievability.
- **Logic:**
  - `Stability_new = Stability_old * (1 + Factor * Difficulty_Modifier)`
- **Library:** Use `fsrs-optimizer` or implement the math directly.

## 2. Pitch Accent Visualizer 🎵
**Problem:** Users learn words with "flat" intonation (Foreigner Accent).
**Solution:**
- **Data:** Integrate a Pitch Accent Dictionary (e.g., `NHK Accent DB` or `Mecab`).
- **UI:** Render a "Pitch Curve" SVG above the word.
  - Low-High-Low (Nakadaka) vs Low-High-High (Heiban).
- **Display:** Toggleable in Settings (Default: On).

## 3. Kana Bootcamp (Unit 0) 🖌️
**Problem:** App assumes Kana knowledge.
**Solution:**
- **New Mode:** "Kana Trace".
- **Interaction:** SVG Stroke Order Animation (using KanjiVG logic).
- **Quiz:** "Which character is 'Ka'?" (Grid Selection).

## 4. Implementation Plan 🛠️
1.  **Refactor SRS:** Update `src/srs_engine.py`.
2.  **Ingest Pitch Data:** Download `pitch_accents.json`.
3.  **Update UI:** Modify `index.html` to render SVGs for pitch.
4.  **Create Bootcamp:** Add `src/bootcamp.py`.
