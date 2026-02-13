import sqlite3
import random
import threading
import string
from typing import List, Dict, Any
from jamdict import Jamdict

# Use thread-local storage for Jamdict connection
_local = threading.local()

def get_jam():
    if not hasattr(_local, "jam"):
        _local.jam = Jamdict()
    return _local.jam

def get_db_conn(db_file):
    if not hasattr(_local, "conn"):
        _local.conn = sqlite3.connect(db_file)
    return _local.conn

def _extract_pos(entry) -> str:
    """Extracts a simplified Part of Speech from the entry."""
    # Priority: Verb > Adjective > Noun
    all_pos = []
    for sense in entry.senses:
        # Check if 'pos' attribute exists and is iterable
        if hasattr(sense, 'pos'):
            pos_val = sense.pos
            # jamdict might return a list of strings or objects depending on version
            if isinstance(pos_val, list):
                all_pos.extend([str(p).lower() for p in pos_val])
            else:
                all_pos.append(str(pos_val).lower())

    if any('verb' in p for p in all_pos):
        if any('ichidan' in p for p in all_pos): return 'v1'
        if any('godan' in p for p in all_pos): return 'v5'
        if any('suru' in p for p in all_pos): return 'vs'
        return 'verb'

    if any('adjective' in p for p in all_pos):
        if any('keiyoushi' in p for p in all_pos): return 'adj-i'
        if any('keiyodoshi' in p for p in all_pos): return 'adj-na'
        return 'adj'

    if any('noun' in p for p in all_pos):
        return 'noun'

    return 'unknown'

def search(query: str):
    jam = get_jam()
    try:
        result = jam.lookup(query)
    except Exception as e:
        print(f"Jamdict lookup error: {e}")
        return []

    entries = []
    for entry in result.entries:
        kanji = entry.kanji_forms[0].text if entry.kanji_forms else ""
        kana = entry.kana_forms[0].text if entry.kana_forms else ""

        if not kanji: kanji = kana
        if not kana: kana = kanji

        meanings = []
        for sense in entry.senses:
             glosses = getattr(sense, 'gloss', [])
             for g in glosses:
                 meanings.append(str(g))

        pos = _extract_pos(entry)

        entries.append({
            "word": kanji,
            "kana": kana,
            "meanings": meanings,
            "pos": pos
        })

    return entries

def get_recommendations(track: str = "General", limit: int = 5, exclude_words: List[str] = [], user_level: int = 1) -> List[Dict[str, Any]]:
    jam = get_jam()

    # We fetch a larger pool of random IDs to filter in Python
    fetch_limit = limit * 40 # Increased fetch limit to find enough candidates

    try:
        conn = get_db_conn(jam.db_file)
        cursor = conn.cursor()
        # Fetch random entry IDs
        cursor.execute("SELECT idseq FROM entry ORDER BY RANDOM() LIMIT ?", (fetch_limit,))
        rows = cursor.fetchall()
        idseqs = [r[0] for r in rows]
        # Connection is persistent, do not close
    except Exception as e:
        print(f"DB Error: {e}")
        return []

    results = []
    count = 0

    for idseq in idseqs:
        if count >= limit: break

        try:
            # Lookup by ID using the correct method for this jamdict version
            # jam.lookup(idseq=...) seems broken or deprecated in this version based on error log
            # Use jam.jmdict.get_entry(idseq) instead
            entry = jam.jmdict.get_entry(idseq)
            if not entry: continue

            # Extract Text
            k_forms = entry.kanji_forms
            r_forms = entry.kana_forms

            kanji = k_forms[0].text if k_forms else ""
            kana = r_forms[0].text if r_forms else ""

            # Use kanji as main word if available, else kana
            word = kanji if kanji else kana

            if not word: continue
            if word in exclude_words: continue

            # --- DIFFICULTY FILTERING ---
            is_common = False

            # Check priority tags in Kanji forms
            for form in k_forms:
                # in jamdict 0.1a, pri is a list of strings like ['news1']
                if hasattr(form, 'pri') and form.pri:
                    if any(p in ['news1', 'ichi1', 'spec1', 'gai1'] for p in form.pri):
                        is_common = True
                        break

            # If not found in Kanji, check Kana forms
            if not is_common:
                for form in r_forms:
                    if hasattr(form, 'pri') and form.pri:
                        if any(p in ['news1', 'ichi1', 'spec1', 'gai1'] for p in form.pri):
                            is_common = True
                            break

            # Autopilot Logic: If user is beginner (< Level 10), enforce common words only
            if user_level < 10 and not is_common:
                continue
            # -----------------------------

            # --- TRACK FILTERING ---
            # Collect all glosses to check for keywords
            all_gloss = []
            for s in entry.senses:
                for g in getattr(s, 'gloss', []):
                    all_gloss.append(str(g).lower())

            # Simple keyword matching for tracks
            if track == "Pop Culture":
                if not any(k in g for k in ['slang', 'anime', 'manga', 'game', 'internet', 'net'] for g in all_gloss):
                    # stricter: 95% chance to skip if not relevant
                    if random.random() > 0.05: continue
            elif track == "Business":
                if not any(k in g for k in ['business', 'company', 'finance', 'economy', 'money', 'office', 'corporate'] for g in all_gloss):
                    if random.random() > 0.05: continue
            elif track == "Travel":
                if not any(k in g for k in ['travel', 'trip', 'hotel', 'train', 'station', 'airport', 'ticket', 'reservation'] for g in all_gloss):
                    if random.random() > 0.05: continue
            # -----------------------

            # QC Checks
            # Skip very long words (compounds) for beginners
            if len(word) > 6 and user_level < 10: continue

            # Skip words with punctuation
            if any(c in string.punctuation for c in word): continue
            if any(c in "！？。、～・" for c in word): continue

            # Skip single characters unless they are common words (like 目, 手, etc.) which are handled by is_common check above.
            # But let's be stricter for single chars: must be hiragana/katakana common particles OR common kanji.
            if len(word) == 1:
                # If it's kana, only allow specific particles
                is_kana_only = all('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in word)
                if is_kana_only:
                    if word not in ['は', 'が', 'に', 'で', 'を', 'も', 'へ', 'と', 'や', 'の', 'ね', 'よ', 'わ']:
                        continue
                # If it's kanji, 'is_common' check handles it (most common 1-char kanji have pri tags)

            pos = _extract_pos(entry)

            results.append({
                "word": word,
                "kana": kana,
                "meanings": all_gloss[:3], # Top 3 meanings
                "pos": pos
            })
            count += 1

        except Exception as e:
            # print(f"Error processing entry {idseq}: {e}")
            continue

    return results
