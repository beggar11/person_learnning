from services.notes import create_note, get_note_by_slug, get_all_notes, update_note, slugify


def test_slugify():
    assert slugify("Hello World") == "hello-world"
    assert slugify("机器学习") == "ji-qi-xue-xi"
    assert slugify("A/B Test") == "a-b-test"


def test_create_and_get_note(db):
    note = create_note(db, title="Test Note", content="# Hello")
    assert note["id"] == 1
    assert note["slug"] == "test-note"
    assert note["title"] == "Test Note"

    fetched = get_note_by_slug(db, "test-note")
    assert fetched is not None
    assert fetched["content"] == "# Hello"


def test_create_note_auto_slug_suffix(db):
    create_note(db, title="Same")
    create_note(db, title="Same")
    slugs = [row["slug"] for row in db.execute("SELECT slug FROM notes")]
    assert "same" in slugs
    assert "same-2" in slugs


def test_update_note(db):
    create_note(db, title="Old", content="old content", slug="old-slug")
    updated = update_note(db, note_id=1, title="New", content="new content")
    assert updated["title"] == "New"
    assert updated["content"] == "new content"


def test_get_all_notes(db):
    create_note(db, title="First")
    create_note(db, title="Second")
    notes = get_all_notes(db)
    assert len(notes) == 2
    assert notes[0]["title"] == "Second"  # most recent first
