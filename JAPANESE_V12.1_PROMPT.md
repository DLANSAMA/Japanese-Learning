# Japanese Learning V12.1: Polish & Bug Fixes 🛠️

**Objective:** Fix UI/UX issues before adding new content. Focus on Furigana rendering, Map interactions, and Gamification logic.

## 1. Furigana Logic (Critical) 👓
**File:** `frontend/src/components/StudyCard.jsx`
- **Issue:** Showing redundant readings (e.g., `Katakana (Katakana)`).
- **Fix:**
  ```javascript
  if (word === kana) {
      // It's pure Kana. Do NOT show Furigana line.
      return <div className="text-4xl">{word}</div>;
  }
  // Use Ruby for Kanji
  return (
      <ruby className="text-4xl">
          {word}<rt className="text-sm text-gray-500">{kana}</rt>
      </ruby>
  );
  ```

## 6. Study Card Layout 🃏
- **Back of Card:** MUST show the Japanese Word again (top), then Meaning, then Sentence.
- **Settings Toggle:**
  - `Display Mode`: [Kanji] | [Furigana] | [Kana]
  - `Romaji`: [Show] | [Hide]
  - **Implementation:** React state in `App.jsx` passed down to `StudyCard.jsx`.

## 2. Map & Curriculum Structure 🗺️
**File:** `data/curriculum.json` & `frontend/src/components/Map.jsx`
- **Issue:** Map nodes act as generic "Study" buttons.
- **Fix:**
  - Define `units` array in `curriculum.json`.
  - Clicking a Node opens a **Unit Detail Modal**:
    - List of Lessons (e.g., "Greetings 1", "Numbers").
    - "Start" button launches `study?unit_id=X`.

## 3. Settings & Themes 🎨
**File:** `frontend/src/components/SettingsModal.jsx`
- **Fix:** Ensure Theme selection actually changes CSS variables or Tailwind classes on the `<body>` tag.
  - `data-theme="cyberpunk"`
  - `data-theme="edo"`

## 4. Search Bar Repair 🔍
**File:** `frontend/src/components/Dictionary.jsx`
- **Fix:** Ensure the Search Input calls `GET /api/dictionary/search` and renders results.
- Add "Add to Study" button to results.

## 5. Gem Economy 💎
**File:** `src/api.py` (Quiz Endpoint)
- **Fix:** Ensure `user.gems` increments by 1 on correct answers (or 10 on lesson complete).
- Return new gem count in API response.
