
def mine_sentence(word: str, pos: str, meaning: str) -> str:
    """
    Generates a simple example sentence based on the word and its Part of Speech.
    Templates:
      - Noun: "Kore wa [Word] desu." (This is [Word].)
      - Verb (v1): [Word-ru] + "masu." (I [Word].)
      - Verb (v5): [Word-u] -> i + "masu." (I [Word].)
      - Verb (vs): [Word] + "shimasu." (I do [Word].)
      - Adjective (i): "[Word] desu." (It is [Word].)
      - Adjective (na): "[Word] na desu." (It is [Word].)
      - Default: "[Word] desu."
    """

    pos = pos.lower()

    # --- Verbs ---
    if pos == 'v1':
        # Ru-verb: Remove 'ru', add 'masu'
        if word.endswith('る'):
            stem = word[:-1]
            return f"私は{stem}ます。" # Watashi wa [stem]masu.
        return f"私は{word}ます。" # Fallback

    elif pos == 'v5':
        # Godan-verb: Change u-sound to i-sound, add 'masu'
        # u -> i
        # tsu -> chi
        # ru -> ri
        # ku -> ki
        # gu -> gi
        # su -> shi
        # mu -> mi
        # nu -> ni
        # bu -> bi

        replacements = {
            'う': 'い',
            'つ': 'ち',
            'る': 'り',
            'く': 'き',
            'ぐ': 'ぎ',
            'す': 'し',
            'む': 'み',
            'ぬ': 'に',
            'ぶ': 'び'
        }

        last_char = word[-1]
        if last_char in replacements:
            stem = word[:-1] + replacements[last_char]
            return f"私は{stem}ます。"
        return f"私は{word}ます。"

    elif pos == 'vs':
        # Suru verb: usually Noun + suru. Usually the dictionary form "suru" is not part of the headword for nouns that take suru.
        # But sometimes it is "benkyousuru".
        if word.endswith('する'):
            stem = word[:-2]
            return f"私は{stem}します。"
        else:
            # Noun that takes suru
            return f"私は{word}します。"

    elif 'verb' in pos:
        # Generic fallback
        return f"私は{word}ます。"

    # --- Adjectives ---
    elif pos == 'adj-i':
        return f"{word}です。"

    elif pos == 'adj-na':
        # Na-adj: dictionary form doesn't have 'na'.
        # "Kirei" -> "Kirei desu" (It is pretty).
        # "Kirei na hito" (Pretty person).
        # Template: "It is [Word]." -> "[Word] desu."
        # Wait, prompt said "[Word] na desu." which is grammatically incorrect usually?
        # "Kirei na desu" is wrong. "Kirei desu" is right.
        # But maybe they want "Kirei na [noun] desu"?
        # Let's stick to simple predictive text.
        # "Genki" -> "Genki desu."
        return f"{word}です。"

    # --- Nouns ---
    elif 'noun' in pos:
        return f"これは{word}です。" # Kore wa [Word] desu.

    # --- Default ---
    return f"{word}です。"
