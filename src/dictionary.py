import sqlite3
import random
import threading
from typing import List, Dict, Any
from jamdict import Jamdict

# Use thread-local storage for Jamdict connection
_local = threading.local()

def get_jam():
    if not hasattr(_local, "jam"):
        _local.jam = Jamdict()
    return _local.jam

def _extract_pos(entry) -> str:
    """Extracts a simplified Part of Speech from the entry."""
    # Priority: Verb > Adjective > Noun
    # Check all senses
    all_pos = []
    for sense in entry.senses:
        # sense.pos is a list of strings
        if hasattr(sense, 'pos'):
            all_pos.extend([str(p).lower() for p in sense.pos])

    # Check for Verbs
    if any('verb' in p for p in all_pos):
        if any('ichidan' in p for p in all_pos): return 'v1'
        if any('godan' in p for p in all_pos): return 'v5'
        if any('suru' in p for p in all_pos): return 'vs'
        return 'verb'

    # Check for Adjectives
    if any('adjective' in p for p in all_pos):
        if any('keiyoushi' in p for p in all_pos): return 'adj-i'
        if any('keiyodoshi' in p for p in all_pos): return 'adj-na'
        return 'adj'

    # Check for Nouns
    if any('noun' in p for p in all_pos):
        return 'noun'

    return 'unknown'

def search(query: str):
    # Returns list of definitions
    jam = get_jam()
    result = jam.lookup(query)
    entries = []

    for entry in result.entries:
        # Get first kanji form, or fallback to first kana form
        kanji = entry.kanji_forms[0].text if entry.kanji_forms else ""
        kana = entry.kana_forms[0].text if entry.kana_forms else ""

        if not kanji:
            kanji = kana

        if not kana:
             # Should be very rare for Japanese dict entry to have no kana
             kana = kanji

        # Collect glosses
        meanings = []
        for sense in entry.senses:
             glosses = getattr(sense, 'gloss', [])
             if isinstance(glosses, list):
                 meanings.extend([str(g) for g in glosses])
             else:
                 meanings.append(str(glosses))

        pos = _extract_pos(entry)

        entries.append({
            "word": kanji,
            "kana": kana,
            "meanings": meanings,
            "pos": pos
        })

    return entries

def get_recommendations(track: str = "General", limit: int = 5, exclude_words: List[str] = []) -> List[Dict[str, Any]]:
    jam = get_jam()
    conn = sqlite3.connect(jam.db_file)
    cursor = conn.cursor()

    query = ""
    params = []

    # Fetch more candidates to account for exclusions and filtering
    fetch_limit = limit * 20

    base_exclusion = """
        AND idseq NOT IN (
            SELECT DISTINCT s.idseq
            FROM Sense s JOIN misc m ON s.ID = m.sid
            WHERE m.text IN ('archaic', 'obsolete', 'obscure', 'rare', 'out-dated or obsolete kana usage')
        )
    """

    if track == "General":
        # Prioritize 'news1' or 'ichi1'
        query = f"""
            SELECT idseq FROM (
                SELECT k.idseq
                FROM Kanji k JOIN KJP p ON k.ID = p.kid
                WHERE p.text IN ('news1', 'ichi1')
                UNION
                SELECT r.idseq
                FROM Kana r JOIN KNP p ON r.ID = p.kid
                WHERE p.text IN ('news1', 'ichi1')
            )
            WHERE 1=1 {base_exclusion}
            ORDER BY RANDOM() LIMIT ?
        """
        params = [fetch_limit]

    elif track == "Pop Culture":
        query = f"""
            SELECT idseq FROM (
                SELECT s.idseq
                FROM Sense s JOIN misc m ON s.ID = m.sid
                WHERE m.text IN ('slang', 'colloquialism', 'manga slang', 'anime slang', 'net slang')
                UNION
                SELECT s.idseq
                FROM Sense s JOIN field f ON s.ID = f.sid
                WHERE f.text LIKE '%manga%' OR f.text LIKE '%anime%' OR f.text LIKE '%game%'
            )
            WHERE 1=1 {base_exclusion}
            ORDER BY RANDOM() LIMIT ?
        """
        params = [fetch_limit]

    elif track == "Business":
        query = f"""
            SELECT DISTINCT s.idseq
            FROM Sense s JOIN field f ON s.ID = f.sid
            WHERE f.text IN ('business', 'finance', 'economics', 'law', 'marketing', 'accounting')
            {base_exclusion}
            ORDER BY RANDOM() LIMIT ?
        """
        params = [fetch_limit]

    elif track == "Tech":
        query = f"""
            SELECT DISTINCT s.idseq
            FROM Sense s JOIN field f ON s.ID = f.sid
            WHERE f.text LIKE '%computing%' OR f.text LIKE '%IT%' OR f.text IN ('mathematics', 'physics', 'engineering', 'science')
            {base_exclusion}
            ORDER BY RANDOM() LIMIT ?
        """
        params = [fetch_limit]

    elif track == "Food":
        query = f"""
            SELECT DISTINCT s.idseq
            FROM Sense s JOIN field f ON s.ID = f.sid
            WHERE f.text IN ('food', 'cooking', 'cuisine')
            {base_exclusion}
            ORDER BY RANDOM() LIMIT ?
        """
        params = [fetch_limit]

    else:
        return get_recommendations("General", limit, exclude_words)

    try:
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        idseqs = [row[0] for row in rows]
    except Exception as e:
        print(f"Error executing query: {e}")
        conn.close()
        return []

    conn.close()

    random.shuffle(idseqs)

    results = []
    count = 0

    for idseq in idseqs:
        if count >= limit:
            break

        try:
            entry = jam.jmdict.get_entry(idseq)
            if not entry:
                continue

            kanji = entry.kanji_forms[0].text if entry.kanji_forms else ""
            kana = entry.kana_forms[0].text if entry.kana_forms else ""

            # QC: Length Check (Max 5 chars)
            check_text = kanji if kanji else kana
            if len(check_text) > 5:
                continue

            # QC: Kanji Check
            has_kanji = bool(entry.kanji_forms)

            if not has_kanji:
                pass
            else:
                pass

            if not kanji: kanji = kana
            if not kana: kana = kanji

            if kanji in exclude_words:
                continue

            meanings = []
            for sense in entry.senses:
                 glosses = getattr(sense, 'gloss', [])
                 if isinstance(glosses, list):
                     meanings.extend([str(g) for g in glosses])
                 else:
                     meanings.append(str(glosses))

            pos = _extract_pos(entry)

            results.append({
                "word": kanji,
                "kana": kana,
                "meanings": meanings,
                "pos": pos
            })
            count += 1

        except Exception as e:
            print(f"Error fetching entry {idseq}: {e}")
            continue

    return results
