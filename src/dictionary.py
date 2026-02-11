import sqlite3
import random
from typing import List, Dict, Any
from jamdict import Jamdict

# Auto-loads data
jam = Jamdict()

def search(query: str):
    # Returns list of definitions
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
        # sense.gloss is usually a list of strings
        meanings = []
        for sense in entry.senses:
             # Just in case gloss is not iterable or handled differently
             glosses = getattr(sense, 'gloss', [])
             if isinstance(glosses, list):
                 meanings.extend([str(g) for g in glosses])
             else:
                 meanings.append(str(glosses))

        entries.append({
            "word": kanji,
            "kana": kana,
            "meanings": meanings
        })

    return entries

def get_recommendations(track: str = "General", limit: int = 5, exclude_words: List[str] = []) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(jam.db_file)
    cursor = conn.cursor()

    query = ""
    params = []

    # Fetch more candidates to account for exclusions
    fetch_limit = limit * 10

    if track == "General":
        # Prioritize 'news1' or 'ichi1'
        query = """
            SELECT idseq FROM (
                SELECT k.idseq
                FROM Kanji k JOIN KJP p ON k.ID = p.kid
                WHERE p.text IN ('news1', 'ichi1')
                UNION
                SELECT r.idseq
                FROM Kana r JOIN KNP p ON r.ID = p.kid
                WHERE p.text IN ('news1', 'ichi1')
            ) ORDER BY RANDOM() LIMIT ?
        """
        params = [fetch_limit]

    elif track == "Pop Culture":
        # Slang, colloquialism, anime, manga, game
        query = """
            SELECT idseq FROM (
                SELECT s.idseq
                FROM Sense s JOIN misc m ON s.ID = m.sid
                WHERE m.text IN ('slang', 'colloquialism', 'manga slang', 'anime slang', 'net slang')
                UNION
                SELECT s.idseq
                FROM Sense s JOIN field f ON s.ID = f.sid
                WHERE f.text LIKE '%manga%' OR f.text LIKE '%anime%' OR f.text LIKE '%game%'
            ) ORDER BY RANDOM() LIMIT ?
        """
        params = [fetch_limit]

    elif track == "Business":
        query = """
            SELECT DISTINCT s.idseq
            FROM Sense s JOIN field f ON s.ID = f.sid
            WHERE f.text IN ('business', 'finance', 'economics', 'law', 'marketing', 'accounting')
            ORDER BY RANDOM() LIMIT ?
        """
        params = [fetch_limit]

    elif track == "Tech":
        query = """
            SELECT DISTINCT s.idseq
            FROM Sense s JOIN field f ON s.ID = f.sid
            WHERE f.text LIKE '%computing%' OR f.text LIKE '%IT%' OR f.text IN ('mathematics', 'physics', 'engineering', 'science')
            ORDER BY RANDOM() LIMIT ?
        """
        params = [fetch_limit]

    elif track == "Food":
        query = """
            SELECT DISTINCT s.idseq
            FROM Sense s JOIN field f ON s.ID = f.sid
            WHERE f.text IN ('food', 'cooking', 'cuisine')
            ORDER BY RANDOM() LIMIT ?
        """
        params = [fetch_limit]

    else:
        # Fallback to General
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

    # Shuffle again just in case
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
            if not kanji: kanji = kana
            if not kana: kana = kanji

            # Check exclusion
            if kanji in exclude_words:
                continue

            # Collect meanings
            meanings = []
            for sense in entry.senses:
                 glosses = getattr(sense, 'gloss', [])
                 # glosses might be list of strings or objects.
                 # In jamdict, it's typically a list of strings (SenseGloss objects stringified)
                 if isinstance(glosses, list):
                     meanings.extend([str(g) for g in glosses])
                 else:
                     meanings.append(str(glosses))

            results.append({
                "word": kanji,
                "kana": kana,
                "meanings": meanings
            })
            count += 1

        except Exception as e:
            print(f"Error fetching entry {idseq}: {e}")
            continue

    return results
