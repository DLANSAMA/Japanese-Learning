# Japanese Learning V9: The Gamification Upgrade 🎮

**Objective:** Transform the "Study Tool" into a "Game" to increase user retention.

## 1. The Unit Map 🗺️
**Problem:** Random study sessions lack a sense of completion.
**Solution:**
- **Structure:** Define a linear path in `data/curriculum.json`.
  - `Unit 1: The Basics` (Greetings, Numbers, Wa/Desu).
  - `Unit 2: Daily Life` (Food, Drink, O/De).
  - `Unit 3: Travel` (Train, Hotel, Ni/He).
- **UI:** A vertical scrolling map (like Duolingo/Candy Crush).
  - Nodes: "Lesson 1", "Lesson 2", "Boss Quiz".
  - State: Locked (Gray) / Active (Color) / Gold (Mastered).

## 2. Bubble Sentence Builder 🫧
**Problem:** Typing full sentences is tedious on mobile/casual use.
**Solution:**
- **Quiz Type:** "Assemble" (replaces some "Input" questions).
- **UI:**
  - Question: "Translate: I eat sushi."
  - Pool: [Sushi] [o] [Tabemasu] [Watashi] [wa] [Desu] [Ka] (Distractors included).
  - Interaction: Click bubbles to move them to the Answer Line.

## 3. The Shop & Currency 💎
**Problem:** XP is just a number. Make it valuable.
**Solution:**
- **Currency:** `Gems` (Earned via Streaks/Level Ups).
- **Shop UI:**
  - **Themes:** "Cyberpunk" (500 Gems), "Edo" (1000 Gems).
  - **Streak Freeze:** Equip to survive 1 missed day (200 Gems).
- **Backend:** Update `UserProfile` to track `gems` and `inventory`.

## 4. Stats & Heatmap 🔥
- **Profile Page:**
  - GitHub-style Contribution Graph (Days studied).
  - "Words Learned" Counter.
  - "Current League" (Bronze/Silver/Gold).

## Implementation Steps
1.  Create `data/curriculum.json` (Defining the Map).
2.  Build `src/static/map.html` (The new Home Screen).
3.  Implement Bubble Logic in `script.js`.
4.  Add Shop Logic to `api.py`.
