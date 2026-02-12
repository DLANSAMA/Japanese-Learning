# Japanese Learning V12.2: Themes & Display Settings 🎨

**Objective:** Fix broken themes and implement granular display controls.

## 1. Fix Theme Switching 🌗
**File:** `frontend/src/components/SettingsModal.jsx` & `frontend/src/App.jsx`
- **Logic:** When theme changes, update `document.documentElement.className`.
- **Themes:**
  - `default`: `#FAF7F2` (Cream)
  - `dark`: `#1A1A1A` (Ink)
  - `cyberpunk`: `#0d0221` (Neon)
  - `edo`: `#d6c6af` (Parchment)
- **Tailwind:** Update `tailwind.config.js` to use CSS variables for colors.

## 2. Display Settings (Kanji/Kana/Romaji) 👓
**File:** `frontend/src/context/SettingsContext.jsx` (Create if missing)
- **State:**
  - `displayMode`: "kanji" | "furigana" | "kana"
  - `showRomaji`: boolean
- **UI:** Add toggles in Settings Modal.

## 3. Apply to Cards 🃏
**File:** `frontend/src/components/StudyCard.jsx`
- Consume `SettingsContext`.
- **Logic:**
  - If `displayMode === 'kana'`, hide Kanji.
  - If `showRomaji === true`, render Romaji line below Japanese.
