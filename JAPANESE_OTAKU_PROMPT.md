# Japanese Learning: Otaku Expansion Pack 🍥

**Objective:** Inject culturally relevant vocabulary from popular Anime/Manga to boost engagement.

## 1. The Dataset (Anime Packs) 📦
**Task:** Create `data/anime_packs/` and populate JSON files for top series.
**Target Series:**
- Naruto
- One Piece
- Demon Slayer (Kimetsu no Yaiba)
- Attack on Titan (Shingeki no Kyojin)
- Jujutsu Kaisen
- Dragon Ball
- Death Note
- My Hero Academia
- Fullmetal Alchemist
- Evangelion

**File Structure (`naruto.json`):**
```json
[
  {
    "word": "火影",
    "kana": "ほかげ",
    "meaning": "Hokage (Fire Shadow)",
    "type": "noun",
    "tags": ["naruto", "title"],
    "example": "俺は火影になる！ (Ore wa Hokage ni naru! - I will become the Hokage!)"
  },
  {
    "word": "チャクラ",
    "kana": "ちゃくら",
    "meaning": "Chakra",
    "type": "noun",
    "tags": ["naruto", "magic"]
  }
]
```

## 2. Universal Otaku Vocab ⛩️
**Task:** Create `data/anime_packs/universal.json`.
**Content:** Common tropes (Tsundere, Senpai, Isekai, Mahou, Baka, Urusai).

## 3. Integration 🔗
**File:** `src/feeder.py`
**Logic:**
- If Track == "Anime":
  - 50% chance to pull from `universal.json`.
  - 50% chance to pull from a specific Series Pack (if unlocked or selected).

## 4. Execution
- Generate at least **50 entries** per series.
- Ensure Examples are iconic quotes where possible.
