import pytest
from unittest.mock import patch, MagicMock
import os
import json
from src.ingest import fetch_jlpt, fetch_pitch, fetch_kanji

# Helpers
def create_mock_response(json_data=None, text_data=None, status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    if json_data:
        mock.json.return_value = json_data
    if text_data:
        mock.text = text_data
    mock.raise_for_status = MagicMock()
    return mock

@patch("httpx.get")
@patch("src.ingest.cleanup")
def test_fetch_jlpt(mock_cleanup, mock_get, tmp_path):
    # Setup mock
    mock_data = [
        {"kanji": "猫", "kana": "ねこ", "meaning": "Cat"},
        {"word": "犬", "reading": "いぬ", "meaning": "Dog"} # Alternate format
    ]
    mock_get.return_value = create_mock_response(json_data=mock_data)

    # Patch VOCAB_FILE in src.ingest
    # Note: We verify the file creation at the patched location
    vocab_file = tmp_path / "vocab.json"
    with patch("src.ingest.VOCAB_FILE", str(vocab_file)):
        fetch_jlpt("n5")

    # Verify file created
    assert vocab_file.exists()
    with open(vocab_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 2
    assert data[0]["word"] == "猫"
    assert "jlpt-n5" in data[0]["tags"]
    assert data[1]["word"] == "犬"
    assert "jlpt-n5" in data[1]["tags"]

@patch("httpx.get")
def test_fetch_pitch(mock_get, tmp_path):
    # Kanjium format
    mock_data = [
        {"headword": "猫", "reading": "ねこ", "pitch": [{"pattern": "L H"}]},
        {"headword": "雨", "reading": "あめ", "pitch": "L H"}
    ]
    mock_get.return_value = create_mock_response(json_data=mock_data)

    pitch_file = tmp_path / "pitch_accent.json"
    with patch("src.ingest.PITCH_FILE", str(pitch_file)):
        fetch_pitch()

    assert pitch_file.exists()
    with open(pitch_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["猫:ねこ"] == [{"pattern": "L H"}]
    assert data["雨:あめ"] == "L H"

@patch("httpx.get")
def test_fetch_kanji(mock_get, tmp_path):
    mock_svg = "<svg>...</svg>"
    mock_get.return_value = create_mock_response(text_data=mock_svg)

    kanji_dir = tmp_path / "kanji"

    with patch("src.ingest.KANJI_DIR", str(kanji_dir)):
        fetch_kanji("猫")

    assert (kanji_dir / "猫.svg").exists()
    with open(kanji_dir / "猫.svg", "r", encoding="utf-8") as f:
        content = f.read()
    assert content == mock_svg
