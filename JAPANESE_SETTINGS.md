# Japanese Learning: Settings & Accessibility ⚙️

**Goal:** Make the app accessible for beginners who know Hiragana/Katakana but not Kanji yet.

## 1. Furigana / Reading Support 📖
**Problem:** Raw Kanji is unreadable for N5 students.
**Solution:**
- **Always Show Kana:** When displaying a word with Kanji, include the Kana reading.
  - *Example:* Instead of `猫`, show `猫 (ねこ)` or `猫 [neko]`.
- **Toggle:** Add a setting `show_furigana` (true/false).
  - If true: Display `Word (Kana)` format.
  - If false: Display `Word` only (Hard Mode).

## 2. Difficulty Filter 📶
**Problem:** Random words from N1 (Advanced) appear too early.
**Solution:**
- **Level Gating:** Only show words <= User Level + 1.
- **Settings:** Allow user to set `max_jlpt_level` (N5, N4, etc.).

## 3. CLI "Headless" Mode 🤖
**Problem:** Running a full API server is heavy for simple agent interactions.
**Solution:**
- **Add Flag:** `python3 learn.py --headless`
- **Behavior:**
  1. Output a JSON object with a question.
  2. Wait for JSON input (answer).
  3. Output JSON result.
  4. Exit.
- **Benefit:** Allows Pip (the agent) to run quizzes inside Discord chat without managing a background process.

## Action Plan
1.  Update `UserProfile` model to include `settings` dict.
2.  Modify `quiz.py` to check `show_furigana` setting before generating question text.
3.  Add `--headless` argument to `learn.py` for one-shot JSON interaction.
