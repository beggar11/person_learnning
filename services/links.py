import re

LINK_PATTERN = re.compile(r'\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]')


def extract_links(content: str) -> list[str]:
    """Extract [[target-slug]] references from Markdown content."""
    return LINK_PATTERN.findall(content)


def sync_links(db, note_id: int, content: str):
    """Rebuild links table for a note: remove old links, parse content, insert new links."""
    db.execute("DELETE FROM links WHERE source_note_id = ?", (note_id,))

    slugs = extract_links(content)
    for slug in slugs:
        target = db.execute("SELECT id FROM notes WHERE slug = ?", (slug,)).fetchone()
        if target is None:
            db.execute(
                "INSERT INTO notes (title, slug, content) VALUES (?, ?, '')",
                (slug, slug)
            )
            target_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        else:
            target_id = target["id"]

        db.execute(
            "INSERT OR IGNORE INTO links (source_note_id, target_note_id) VALUES (?, ?)",
            (note_id, target_id)
        )
    db.commit()


def get_backlinks(db, note_id: int) -> list[dict]:
    """Get all notes that link to this note."""
    rows = db.execute("""
        SELECT n.id, n.title, n.slug FROM notes n
        JOIN links l ON l.source_note_id = n.id
        WHERE l.target_note_id = ?
        ORDER BY n.updated_at DESC
    """, (note_id,)).fetchall()
    return [dict(r) for r in rows]


def get_all_links(db) -> list[dict]:
    """Get all links as source/target pairs for graph rendering."""
    rows = db.execute("""
        SELECT n1.slug AS source, n2.slug AS target
        FROM links l
        JOIN notes n1 ON n1.id = l.source_note_id
        JOIN notes n2 ON n2.id = l.target_note_id
    """).fetchall()
    return [dict(r) for r in rows]
