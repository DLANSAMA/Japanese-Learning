# Japanese Learning V7: The Web Dojo 🌐

**Objective:** Modernize the interface by moving from Terminal (TUI) to a Web App (Single Page Application).

## 1. Backend Upgrade (FastAPI) ⚙️
**File:** `src/api.py`
- Mount a static directory: `app.mount("/", StaticFiles(directory="src/static"), html=True)`.
- Add endpoints:
  - `GET /api/study` (Fetch new words).
  - `POST /api/study/confirm` (Mark as learned).
  - `GET /api/settings` (Get/Set Track).

## 2. Frontend (The Dojo) 🏯
**File:** `src/static/index.html`
**Stack:** HTML5 + CSS (Tailwind CDN) + Vanilla JS (or Alpine.js).
**Design:**
- **Dark Mode:** Deep blue/purple theme (Cyberpunk/Night).
- **Card View:** Center card with big Kanji. Click to flip (reveal reading/meaning).
- **Controls:**
  - [Study Mode] Button.
  - [Quiz Mode] Button.
  - [Audio] Button (using browser `speechSynthesis` or file).

## 3. Interaction Flow 🔄
1.  **Dashboard:** Shows Level, Streak, Next Review Time.
2.  **Study:**
    - Show Card 1 -> "Next" -> Card 2 -> ... -> "Finish".
3.  **Quiz:**
    - Show Card -> User inputs answer (or selects choice) -> Feedback -> Next.

## 4. Implementation Steps
1.  Create `src/static/` folder.
2.  Update `requirements.txt` (ensure `jinja2` or `aiofiles` if needed for static serving).
3.  Modify `learn.py serve` to host the web app.
