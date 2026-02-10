# Japanese Learning V6: Tracks & Polish ✨

**Objective:** Personalized learning paths and a slicker experience.

## 1. Feature: Learning Tracks 🛤️
**Problem:** "One size fits all" vocab lists are inefficient.
**Solution:**
- **Onboarding:** On first run (or Settings), ask user for their goal.
- **Tracks:**
  1.  **General / Daily Life** (Default)
  2.  **Pop Culture** (Anime, Manga, Games, Slang)
  3.  **Travel / Tourism** (Survival phrases, Directions)
  4.  **Business** (Formal Keigo, Office terms)
- **Mechanism:**
  - Tag vocab items in `vocab.json` (e.g., `["core", "anime"]`).
  - Study Mode prioritizes items matching the user's selected track.

## 2. Feature: Audio Integration 🎧
**Problem:** Silent learning is hard.
**Solution:**
- **Dependencies:** Add `playsound` or `simpleaudio` to requirements.
- **Assets:** Create `assets/audio/` directory.
- **Logic:**
  - If audio file exists (`assets/audio/{word_id}.mp3`), play it when word is shown.
  - Add "Play Audio" button/hotkey (e.g., 'P').

## 3. UI Polish 🎨
- **Themes:** Add color themes to `ui.py` (Cyberpunk, Zen, Terminal).
- **Mascot:** Add a simple ASCII mascot that greets/encourages the user.

## Implementation Steps
1.  Update `UserProfile` to store `selected_track`.
2.  Update `study.py` to filter `get_new_items` based on track tags.
3.  Add Audio playback logic to `ui.py`.
4.  (Optional) Batch generate placeholders for audio files.
