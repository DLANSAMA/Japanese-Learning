import json
import os
import httpx
from typing import List, Dict, Optional
from .models import Vocabulary
from .cleanup_data import cleanup

# Default URLs (Best Guess based on repo structure)
# Bluskyo/JLPT_Vocabulary seems to use "json/n5.json" in main branch?
# If not, users can override with --url
JLPT_URL_TEMPLATE = "https://raw.githubusercontent.com/Bluskyo/JLPT_Vocabulary/main/json/n{level}.json"
PITCH_URL = "https://raw.githubusercontent.com/mifunetoshiro/kanjium/master/data/source_files/dictionary_pitch.json"
KANJI_VG_URL_TEMPLATE = "https://raw.githubusercontent.com/KanjiVG/kanjivg/master/kanji/{hex_code}.svg"

DATA_DIR = "data"
KANJI_DIR = os.path.join(DATA_DIR, "kanji")
PITCH_FILE = os.path.join(DATA_DIR, "pitch_accent.json")
VOCAB_FILE = os.path.join(DATA_DIR, "vocab.json")

def ensure_dirs():
    if not os.path.exists(KANJI_DIR):
        os.makedirs(KANJI_DIR)

def fetch_jlpt(level: str, url: Optional[str] = None):
    target_url = url if url else JLPT_URL_TEMPLATE.format(level=level.lower().replace("n", ""))
    print(f"Fetching JLPT {level} from {target_url}...")

    try:
        response = httpx.get(target_url, follow_redirects=True)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching JLPT data: {e}")
        # Try local fallback
        local_path = os.path.join("data", "source_files", f"jlpt_{level}.json")
        if os.path.exists(local_path):
            print(f"Using local fallback: {local_path}")
            with open(local_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            print("No data found.")
            return

    # Normalize and merge
    if not os.path.exists(VOCAB_FILE):
        existing_vocab = []
    else:
        with open(VOCAB_FILE, "r", encoding="utf-8") as f:
            existing_vocab = json.load(f)

    # Create a map of existing words to avoid duplicates
    existing_map = {(v.get("word"), v.get("kana")): v for v in existing_vocab}

    added_count = 0
    for item in data:
        # Bluskyo format: {"kanji": "...", "kana": "...", "meaning": "...", ...}
        # Or Tanos format
        # We need to adapt based on structure. Assuming generic list of dicts.

        word = item.get("kanji", item.get("word", ""))
        kana = item.get("kana", item.get("reading", ""))
        meaning = item.get("meaning", item.get("english", ""))

        if not word and not kana:
            continue

        if not word:
            word = kana # Kana-only word

        key = (word, kana)

        if key in existing_map:
            # Update tags if needed
            entry = existing_map[key]
            if "tags" not in entry:
                entry["tags"] = []
            tag = f"jlpt-{level.lower()}"
            if tag not in entry["tags"]:
                entry["tags"].append(tag)
        else:
            # Create new
            new_entry = {
                "word": word,
                "kana": kana,
                "romaji": "", # Todo: generate romaji?
                "meaning": meaning,
                "level": 0,
                "tags": [f"jlpt-{level.lower()}"],
                "status": "new",
                "ease_factor": 2.5,
                "interval": 0,
                "due_date": None
            }
            existing_vocab.append(new_entry)
            existing_map[key] = new_entry
            added_count += 1

    # Save
    with open(VOCAB_FILE, "w", encoding="utf-8") as f:
        json.dump(existing_vocab, f, ensure_ascii=False, indent=2)

    print(f"Ingested {added_count} new words for {level}.")

    # Run cleanup to ensure hygiene
    cleanup()

def fetch_pitch(url: Optional[str] = None):
    target_url = url if url else PITCH_URL
    print(f"Fetching Pitch Accent data from {target_url}...")

    try:
        response = httpx.get(target_url, follow_redirects=True)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching Pitch data: {e}")
        # Try local fallback
        local_path = os.path.join("data", "source_files", "pitch.json")
        if os.path.exists(local_path):
             with open(local_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            return

    # Process Kanjium format
    # Expecting list of entries. We want to map word+reading -> pitch_pattern
    # Kanjium structure: [ { "headword": "...", "reading": "...", "pitch": [...] } ]

    pitch_map = {}

    for entry in data:
        headword = entry.get("headword")
        reading = entry.get("reading")
        pitch = entry.get("pitch") # format?

        # If pitch is a list of patterns, take the first one?
        # Kanjium pitch is often a list of dictionaries or strings.
        # Let's assume generic structure and just save the map for now.

        if headword and reading:
            key = f"{headword}:{reading}"
            pitch_map[key] = pitch

    with open(PITCH_FILE, "w", encoding="utf-8") as f:
        json.dump(pitch_map, f, ensure_ascii=False, indent=2)

    print(f"Saved pitch data for {len(pitch_map)} entries.")

def fetch_kanji(char: str):
    ensure_dirs()
    hex_code = hex(ord(char))[2:].zfill(5).lower()
    url = KANJI_VG_URL_TEMPLATE.format(hex_code=hex_code)
    path = os.path.join(KANJI_DIR, f"{char}.svg")

    if os.path.exists(path):
        print(f"Kanji {char} already exists.")
        return

    print(f"Fetching Kanji {char} (hex: {hex_code}) from {url}...")

    try:
        response = httpx.get(url, follow_redirects=True)
        response.raise_for_status()
        with open(path, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"Saved {path}")
    except Exception as e:
        print(f"Error fetching Kanji {char}: {e}")
