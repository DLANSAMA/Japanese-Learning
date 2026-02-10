from typing import List, Dict, Any
from .models import Vocabulary

def search_vocab(query: str, vocab_list: List[Vocabulary]) -> List[Dict[str, Any]]:
    """
    Search for vocabulary items matching the query.

    Args:
        query: The search string.
        vocab_list: The list of Vocabulary objects to search.

    Returns:
        A list of dictionaries representing the matching vocabulary items.
    """
    query = query.lower().strip()
    results = []

    for item in vocab_list:
        # Check word (Kanji), Kana, Romaji, and Meaning
        if (query in item.word.lower() or
            query in item.kana.lower() or
            query in item.romaji.lower() or
            query in item.meaning.lower()):

            results.append({
                "word": item.word,
                "kana": item.kana,
                "meaning": item.meaning,
                "romaji": item.romaji,
                "tags": item.tags
            })

    return results
