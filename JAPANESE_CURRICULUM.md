# Japanese Learning: Curriculum & Study Mode 🎓

**Goal:** Transform the app from a random quiz generator into a structured learning course.

## 1. The Core Problem 🚫
Currently, the app quizzes users on *any* word in the database.
**Issue:** Users cannot answer questions about words they haven't learned yet.

## 2. Solution: Study Mode vs. Quiz Mode ✅
We need two distinct modes:

### A. Study Mode (The Teacher) 👨‍🏫
**Purpose:** Introduce new content.
- **Action:** Select 5 words/grammar points with status `new`.
- **Display:**
  1.  **Word:** `猫 (ねこ)`
  2.  **Meaning:** Cat
  3.  **Example:** `猫が好きです (I like cats)`
  4.  **Audio (Optional):** Play TTS if available.
- **Interaction:** User presses "Next" or "Got it" to mark the word as `learning`.
- **Result:** Word moves from `new` -> `learning` (Active Queue).

### B. Quiz Mode (The Test) 📝
**Purpose:** Review learned content via SRS.
- **Constraint:** ONLY include items with status `learning` or `mastered`.
- **Never** include `new` items.

## 3. Data Model Updates 💾
**`vocab.json` / `sentences.json`:**
- Add `status` field:
  - `"new"`: Not yet seen (Default).
  - `"learning"`: Introduced in Study Mode.
  - `"mastered"`: SRS interval > 21 days.

**`user.json`:**
- Track `current_lesson_id` or `learned_count`.

## 4. Implementation Plan 🛠️
1.  **Database Migration:** Update all existing items to `status: "new"`.
2.  **Study Controller:** Create `study.py` to fetch and display new items.
3.  **Quiz Filter:** Modify `quiz.py` to filter `item.status != "new"`.
4.  **UI Update:** Add "Start Lesson" option to Main Menu.
