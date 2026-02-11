# Japanese Learning V12: Project Kizuna (React Rewrite) ⛩️

**Objective:** Rewrite the frontend using React + Tailwind to match the "Kizuna" design specification.

## 1. Architecture Shift 🏗️
**Current:** `src/static/index.html` (Vanilla JS).
**New:** `frontend/` (Vite + React + Tailwind).
**Build Step:** `npm run build` -> Output to `src/static/`.

## 2. Design System (The "Kizuna" Look) 🎨
**Colors:**
- Background: `#FAF7F2` (Cream/Paper)
- Primary: `#BC002D` (Crimson)
- Text: `#2D2A26` (Charcoal)
- Borders: `#E8E1D5`

**Typography:**
- Headers: `Inter` (Black/Italic/Uppercase).
- Body: `Noto Sans JP`.

**Components (Port from React Prototype):**
- **Sidebar (Desktop):** Left vertical nav with "Kizuna" logo.
- **Bottom Nav (Mobile):** Floating bar with Map/Library/Dojo icons.
- **The Map:** Vertical spine with alternating "Tatami" square nodes.
- **Mission Modal:** Slide-up sheet (Mobile) / Centered Card (Desktop).

## 3. Features to Migrate 📦
- **Dictionary Search:** Re-implement the search bar using React state.
- **Study Mode:** Swipeable cards for new words.
- **Quiz Mode:** FSRS feedback buttons (Easy/Hard).
- **Pitch Accent:** Render SVG curves on the card back.

## 4. Implementation Plan 🛠️
1.  Initialize `frontend` folder with Vite.
2.  Install `lucide-react`, `framer-motion` (for animations).
3.  Configure `tailwind.config.js` with the Kizuna palette.
4.  Build `App.jsx` based on the provided `Web-UI-Test.txt` layout.
5.  Connect to `api.py` endpoints (`fetch('/api/...')`).
