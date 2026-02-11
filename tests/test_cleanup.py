import pytest
import json
import os
from unittest.mock import patch, MagicMock
from src.cleanup_data import cleanup
from src.dictionary import get_recommendations

TEST_DATA_FILE = "data/test_vocab_cleanup.json"

@pytest.fixture
def cleanup_data_file():
    # Create a test file
    data = [
        # Duplicate
        {"word": "猫", "kana": "ねこ", "status": "new", "fsrs_stability": 1.0},
        {"word": "猫", "kana": "ねこ", "status": "learning", "fsrs_stability": 2.0},
        # Invalid FSRS
        {"word": "犬", "kana": "いぬ", "status": "new", "fsrs_stability": -1.0, "fsrs_retrievability": 1.5},
        # Normal
        {"word": "鳥", "kana": "とり", "status": "new", "fsrs_stability": 0.0}
    ]
    if not os.path.exists("data"):
        os.makedirs("data")
    with open(TEST_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    yield TEST_DATA_FILE

    # Cleanup
    if os.path.exists(TEST_DATA_FILE):
        os.remove(TEST_DATA_FILE)

def test_cleanup_logic(cleanup_data_file):
    # Patch the DATA_FILE in src.cleanup_data
    with patch("src.cleanup_data.DATA_FILE", cleanup_data_file):
        cleanup()

    with open(cleanup_data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Check duplicates removed
    neko = [item for item in data if item["word"] == "猫"]
    assert len(neko) == 1
    # Check priority: should be "learning" one
    assert neko[0]["status"] == "learning"
    assert neko[0]["fsrs_stability"] == 2.0

    # Check invalid FSRS fixed
    inu = [item for item in data if item["word"] == "犬"][0]
    assert inu["fsrs_stability"] == 0.0
    assert inu["fsrs_retrievability"] == 1.0 # Clamped to 1.0

    # Check normal preserved
    tori = [item for item in data if item["word"] == "鳥"][0]
    assert tori["status"] == "new"

@patch('src.dictionary.get_jam')
@patch('sqlite3.connect')
def test_dictionary_filters(mock_connect, mock_get_jam):
    # Mock SQLite response (idseqs)
    mock_cursor = MagicMock()
    mock_connect.return_value.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [(1,), (2,), (3,), (4,), (5,)]

    # Mock Jamdict entries
    mock_jam = mock_get_jam.return_value

    # Entry 1: Valid
    entry1 = MagicMock()
    entry1.kanji_forms = [MagicMock(text="猫")]
    entry1.kana_forms = [MagicMock(text="ねこ")]
    entry1.senses = []

    # Entry 2: Symbol
    entry2 = MagicMock()
    entry2.kanji_forms = [MagicMock(text="猫！")]
    entry2.kana_forms = [MagicMock(text="ねこ")]

    # Entry 3: 1-char Kana (not particle)
    entry3 = MagicMock()
    entry3.kanji_forms = []
    entry3.kana_forms = [MagicMock(text="あ")]

    # Entry 4: 1-char Particle (valid)
    entry4 = MagicMock()
    entry4.kanji_forms = []
    entry4.kana_forms = [MagicMock(text="の")]

    # Entry 5: 1-char Kanji (valid)
    entry5 = MagicMock()
    entry5.kanji_forms = [MagicMock(text="目")]
    entry5.kana_forms = [MagicMock(text="め")]

    def get_entry_side_effect(idseq):
        if idseq == 1: return entry1
        if idseq == 2: return entry2
        if idseq == 3: return entry3
        if idseq == 4: return entry4
        if idseq == 5: return entry5
        return None

    mock_jam.jmdict.get_entry.side_effect = get_entry_side_effect

    results = get_recommendations(limit=10)

    words = [r["word"] for r in results]

    assert "猫" in words
    assert "猫！" not in words
    assert "あ" not in words
    assert "の" in words
    assert "目" in words
