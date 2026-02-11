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
