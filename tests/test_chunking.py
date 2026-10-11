import pytest

from src.notebooklm_clone.text_utils import chunk_text, clean_text


def test_clean_text_normalizes_whitespace():
    assert clean_text("Hello   world\n\n\nagain") == "Hello world\n\nagain"


def test_chunking_preserves_content_and_overlap():
    text = " ".join(f"word{i}" for i in range(200))
    chunks = chunk_text(text, chunk_size=120, overlap=20)
    assert len(chunks) > 2
    assert all(chunks)
    assert chunks[0].startswith("word0")


def test_invalid_chunk_settings():
    with pytest.raises(ValueError):
        chunk_text("content", chunk_size=100, overlap=100)

