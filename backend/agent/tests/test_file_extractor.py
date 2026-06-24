import pytest

from agent.tools.file_extractor import extract_text_from_bytes


def test_extracts_plain_text_file():
    result = extract_text_from_bytes("notes.txt", b"hello world")
    assert result["extracted_text"] == "hello world"
    assert result["content_type"] == ".txt"


def test_extracts_json_file():
    payload = b'{"name": "Kyvo"}'
    result = extract_text_from_bytes("data.json", payload)
    assert result["extracted_text"] == '{"name": "Kyvo"}'


def test_extracts_tsv_file():
    result = extract_text_from_bytes("table.tsv", b"a\tb\nc\td")
    assert "a\tb" in result["extracted_text"]
    assert "c\td" in result["extracted_text"]


def test_rejects_unsupported_extension():
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text_from_bytes("archive.zip", b"binary")
