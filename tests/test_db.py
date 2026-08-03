import db


def test_init_db_creates_empty_chunks_table(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.init_db()
    assert db.count_chunks() == 0
    assert db.get_all_chunks() == []


def test_insert_and_retrieve_chunk(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.init_db()

    db.insert_chunk(source="caching", content="Caching stores data.", embedding=[0.1, 0.2, 0.3])

    chunks = db.get_all_chunks()
    assert len(chunks) == 1
    assert chunks[0]["source"] == "caching"
    assert chunks[0]["content"] == "Caching stores data."
    assert chunks[0]["embedding"] == [0.1, 0.2, 0.3]
    assert db.count_chunks() == 1


def test_clear_chunks_removes_all_rows(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.init_db()

    db.insert_chunk(source="a", content="content a", embedding=[1.0])
    db.insert_chunk(source="b", content="content b", embedding=[2.0])
    assert db.count_chunks() == 2

    db.clear_chunks()
    assert db.count_chunks() == 0
