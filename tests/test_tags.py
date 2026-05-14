from services.notes import upsert_tag, set_note_tags, get_note_tags, create_note

def test_upsert_tag(db):
    id1 = upsert_tag(db, "Python")
    id2 = upsert_tag(db, "Python")
    assert id1 == id2

    id3 = upsert_tag(db, "JavaScript")
    assert id3 != id1

def test_upsert_tag_empty(db):
    assert upsert_tag(db, "") is None
    assert upsert_tag(db, "  ") is None

def test_set_and_get_tags(db):
    create_note(db, title="Test")
    set_note_tags(db, 1, ["Python", "Web"])
    tags = get_note_tags(db, 1)
    assert len(tags) == 2
    assert {t["name"] for t in tags} == {"python", "web"}

def test_set_tags_replaces(db):
    create_note(db, title="Test")
    set_note_tags(db, 1, ["A", "B"])
    set_note_tags(db, 1, ["C"])
    tags = get_note_tags(db, 1)
    assert len(tags) == 1
    assert tags[0]["name"] == "c"

def test_empty_tags(db):
    create_note(db, title="Test")
    set_note_tags(db, 1, ["  ", ""])
    tags = get_note_tags(db, 1)
    assert tags == []
