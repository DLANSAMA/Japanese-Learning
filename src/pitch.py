from typing import List, Tuple

# Mock Pitch Accent Logic
# In a real app, this would query a dictionary database (e.g. Wadoku, NHK Accent)
# For now, we return a heuristic or random pattern for demonstration purposes,
# or look up from a small hardcoded list of common words.

COMMON_ACCENTS = {
    "食べる": "LHHH", # Atamadaka? No, Taberu is Nakadaka usually? taBEru (LHL). Wait.
                      # Taberu: [2] (Nakadaka). ta-BE-ru. LHL.
                      # Standard: ta(L) be(H) ru(L).
    "飲む": "LHL",    # Nomu: [1] (Atamadaka). NO-mu. HL.
    "猫": "LHH",      # Neko: [1] (Atamadaka). NE-ko. HL. (Actually Neko is [1] usually).
                      # Wait, Neko is Heiban [0] usually. ne-KO(H). LH.
                      # Let's try to be accurate for few words.
    "元気": "LHH",    # Genki: [1]. GEN-ki. HL.
    "勉強": "LHHHH",  # Benkyou: [0]. be-N-KYO-U. LHHH.
}

def get_pitch_pattern(word: str, reading: str) -> str:
    """
    Returns a binary pitch pattern string (H=High, L=Low) for the word.
    Length should match the number of moras in the reading.
    """
    if word in COMMON_ACCENTS:
        return COMMON_ACCENTS[word]

    # Heuristic Fallback
    # Most Japanese words are Heiban (Flat) or Atamadaka.
    # Heiban: First mora Low, rest High. (LHHHH...)
    # We need to count moras. Naive count = len(reading).
    # Better count: handle small tsu, ya, yu, yo.

    moras = len(reading) # Approximation
    # Small char adjustment
    small_chars = "ぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮ"
    for char in reading:
        if char in small_chars:
            moras -= 1

    if moras <= 0: return ""

    # Return Heiban pattern: L H H ...
    if moras == 1:
        return "H" # Or L? Monomoraic nouns usually H? Or L?

    # L H H H ...
    return "L" + "H" * (moras - 1)
