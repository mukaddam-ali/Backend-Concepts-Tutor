from ingest import chunk_text


def test_chunk_text_groups_two_paragraphs_per_chunk():
    text = "Para one.\n\nPara two.\n\nPara three.\n\nPara four."
    chunks = chunk_text(text, source="doc")
    assert chunks == ["Para one.\n\nPara two.", "Para three.\n\nPara four."]


def test_chunk_text_handles_trailing_odd_paragraph():
    text = "Para one.\n\nPara two.\n\nPara three."
    chunks = chunk_text(text, source="doc")
    assert chunks == ["Para one.\n\nPara two.", "Para three."]


def test_chunk_text_ignores_blank_paragraphs():
    text = "Para one.\n\n\n\nPara two.\n\n   \n\nPara three."
    chunks = chunk_text(text, source="doc")
    assert chunks == ["Para one.\n\nPara two.", "Para three."]


def test_chunk_text_empty_input_returns_no_chunks():
    assert chunk_text("", source="doc") == []
    assert chunk_text("   \n\n  ", source="doc") == []
