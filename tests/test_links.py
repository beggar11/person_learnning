from services.links import extract_links, sync_links, get_backlinks


def test_extract_links():
    content = "See [[python]] and [[machine-learning]] for details."
    slugs = extract_links(content)
    assert slugs == ["python", "machine-learning"]


def test_extract_links_with_aliases():
    content = "See [[python|Python Language]] for details."
    slugs = extract_links(content)
    assert slugs == ["python"]


def test_extract_links_no_links():
    content = "Just plain text with [not a link](url)"
    assert extract_links(content) == []


def test_sync_links_creates_placeholders(db):
    from services.notes import create_note
    create_note(db, title="Source", content="Link to [[target-slug]]")
    sync_links(db, note_id=1, content="Link to [[target-slug]]")
    target = db.execute("SELECT * FROM notes WHERE slug = ?", ("target-slug",)).fetchone()
    assert target is not None
    assert target["title"] == "target-slug"

    link_row = db.execute(
        "SELECT * FROM links WHERE source_note_id = ? AND target_note_id = ?",
        (1, target["id"])
    ).fetchone()
    assert link_row is not None


def test_sync_links_removes_stale_links(db):
    from services.notes import create_note
    create_note(db, title="Source", content="[[a]] [[b]]")
    sync_links(db, note_id=1, content="[[a]] [[b]]")
    assert len(db.execute("SELECT * FROM links WHERE source_note_id = 1").fetchall()) == 2

    sync_links(db, note_id=1, content="[[a]]")
    rows = db.execute("SELECT * FROM links WHERE source_note_id = 1").fetchall()
    assert len(rows) == 1


def test_get_backlinks(db):
    from services.notes import create_note
    create_note(db, title="A", slug="a")
    create_note(db, title="B", content="ref [[a]]")
    sync_links(db, note_id=2, content="ref [[a]]")

    backlinks = get_backlinks(db, note_id=1)
    assert len(backlinks) == 1
    assert backlinks[0]["title"] == "B"
