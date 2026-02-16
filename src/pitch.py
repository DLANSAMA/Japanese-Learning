import threading
import logging
from typing import List, Optional
import MeCab
import unidic_lite

logger = logging.getLogger(__name__)

# Thread-local storage for MeCab tagger to ensure thread safety
_local = threading.local()

def get_tagger():
    """Returns a thread-local MeCab Tagger instance."""
    if not hasattr(_local, "tagger"):
        try:
            # Initialize MeCab with unidic-lite dictionary
            _local.tagger = MeCab.Tagger(f'-d "{unidic_lite.DICDIR}"')
        except Exception as e:
            logger.error(f"Failed to initialize MeCab: {e}")
            return None
    return _local.tagger

def get_moras(kana: str) -> List[str]:
    """
    Splits kana string into moras.
    Handles small kana (e.g., ゃ, ゅ, ょ) by attaching them to the previous character.
    'っ' (sokuon) and 'ー' (choonpu) constitute their own moras.
    """
    moras = []
    # Small kana that combine with the preceding character
    small_chars = "ぁぃぅぇぉゃゅょゎァィゥェォャュョヮ"

    for char in kana:
        if char in small_chars and moras:
            moras[-1] += char
        else:
            moras.append(char)
    return moras

def get_pitch_from_kernel(kernel: int, num_moras: int) -> str:
    """
    Generates L/H pattern for a given accent kernel and number of moras.
    kernel=0: Heiban (L H H H ...)
    kernel=1: Atamadaka (H L L L ...)
    kernel=k: Nakadaka/Odaka (L H ... H (at k) L ...)
    """
    if num_moras <= 0: return ""

    pattern = []
    for i in range(1, num_moras + 1):
        if kernel == 0:
            # Heiban: First mora Low, rest High.
            # (Note: Monomoraic Heiban is technically Low, but particles attach High.
            #  In isolation, it's often perceived as High relative to nothing, but strictly it starts Low).
            val = 'L' if i == 1 else 'H'
        elif kernel == 1:
            # Atamadaka: First mora High, rest Low.
            val = 'H' if i == 1 else 'L'
        else:
            # Nakadaka/Odaka: Low start, High until kernel, then Low.
            if i == 1:
                val = 'L'
            elif i <= kernel:
                val = 'H'
            else:
                val = 'L'
        pattern.append(val)

    return "".join(pattern)

def _find_accent_kernel(features: List[str]) -> Optional[int]:
    """
    Attempts to find the accent kernel (aType) in the MeCab features list.
    Prioritizes index 23 (standard for unidic-lite v1.0.8), but adaptively checks other
    indices (17, 21, 22, 24) if 23 is not a valid integer.
    """
    # Priority order: 23 (unidic-lite default), 24 (often pronunciation), 22 (sometimes), 17 (standard UniDic), 21
    # We validate by ensuring the value is a digit and within reasonable bounds (0-20).
    search_indices = [23, 24, 22, 17, 21]

    for idx in search_indices:
        if idx < len(features):
            val = features[idx]
            # Must be a digit.
            if val.isdigit():
                kernel = int(val)
                # Sanity check: accent kernel shouldn't be excessively large (e.g. > 20 is suspicious unless it's a code).
                if 0 <= kernel <= 20:
                    return kernel
    return None

def get_pitch_pattern(word: str, reading: str) -> str:
    """
    Returns a binary pitch pattern string (H=High, L=Low) for the word.
    The output length matches len(reading) (character count), ensuring that
    characters within the same mora share the same pitch value.
    """
    if not reading:
        return ""

    moras = get_moras(reading)
    num_moras = len(moras)

    kernel = 0 # Default to Heiban if MeCab fails or no accent found

    tagger = get_tagger()
    if tagger:
        try:
            # Parse the word to find the accent kernel.
            # We assume the first significant token holds the relevant accent for the word.
            node = tagger.parseToNode(word)
            found = False

            while node:
                features = node.feature.split(',')
                # Skip BOS/EOS or empty features
                if len(features) < 1 or features[0] == "BOS/EOS":
                    node = node.next
                    continue

                # Check POS to skip irrelevant tokens (e.g. '接頭辞' prefix might not carry accent?)
                # Actually, usually the main word is the first significant token.

                found_kernel = _find_accent_kernel(features)
                if found_kernel is not None:
                    kernel = found_kernel
                    found = True
                    break # Stop after finding the first valid accent

                # If valid word surface but no accent found, check next token?
                # Usually compound words have their own rules, but simple lookup should match head.
                if node.surface:
                    # If we found a surface but failed to find accent, maybe it's just missing.
                    # We continue only if surface is empty (which shouldn't happen here).
                    break

                node = node.next

        except Exception as e:
            logger.error(f"MeCab parsing error for {word}: {e}")
            # Fallback to kernel=0 (Heiban)

    # Generate mora-based pattern
    mora_pattern = get_pitch_from_kernel(kernel, num_moras)

    # Expand to character-based pattern
    # Mapping: Mora 1 -> Chars of Mora 1 get Mora 1's pitch.
    full_pattern = ""
    for i, mora_str in enumerate(moras):
        if i < len(mora_pattern):
            pitch = mora_pattern[i]
            full_pattern += pitch * len(mora_str)
        else:
            # Should not happen given logic above
            full_pattern += "L" * len(mora_str)

    return full_pattern
