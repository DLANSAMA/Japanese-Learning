# Japanese Learning V4: The Agent Sensei Upgrade 🥋

**Objective:** Enable full "Teacher Mode" for AI agents by exposing study features via CLI and expanding the content library.

## 1. Feature: Headless Study Mode 👨‍🏫
**Problem:** Agents can quiz users but cannot introduce new material.
**Requirement:** Add `--study` flag to `headless.py`.

**Behavior:**
- Command: `python3 learn.py --headless --study`
- **Output (JSON):** Returns 3-5 *new* items from the database (status="new").
  ```json
  {
    "type": "study_session",
    "items": [
      {
        "id": "vocab:猫",
        "word": "猫",
        "kana": "ねこ",
        "meaning": "Cat",
        "example": "猫が好きです (I like cats)",
        "tts_text": "ねこ" 
      },
      ...
    ]
  }
  ```
- **Action:** Marks these items as `status="learning"` immediately upon fetching (or requires a confirmation POST if using API, but for CLI, fetching = starting).

## 2. Feature: Audio Support 🗣️
**Problem:** Agents don't know what string to send to their TTS engine.
**Requirement:** Add `tts_text` field to ALL headless outputs (Quiz & Study).
- For Vocab: The Kana reading (e.g., "ねこ").
- For Sentences: The full Japanese sentence (e.g., "わたしはすしをたべます").

## 3. Content Expansion: N5 Sentences 📚
**Problem:** Only 3 sentences exist. We need volume.
**Requirement:** Populate `data/sentences.json` with **50+ N5-level sentences**.
- **Categories:**
  - **Greetings:** "Hajimemashite", "Genki desu ka"
  - **RPG/Combat:** "Kougeki shimasu" (I attack), "Nigeru!" (Run!)
  - **Daily Life:** "Gohan o taberu", "Mizu o nomu"
  - **Travel:** "Eki wa doko desu ka", "Kore wa ikura desu ka"

## 4. Refinement: Headless Input Handling 🛠️
- Ensure `sys.stdin.readline()` doesn't block indefinitely if the agent sends a newline immediately.
- Support a `--get-stats` flag for agents to check user progress (`xp`, `level`, `streak`) without running a quiz.

## Implementation Checklist
1. [ ] Update `src/headless.py` to handle `--study` and `--get-stats`.
2. [ ] Modify `src/models.py` / `to_dict` methods to include `tts_text`.
3. [ ] Bulk generate 50 sentences in `data/sentences.json`.
4. [ ] Verify `python3 learn.py --headless --study` outputs valid JSON.
