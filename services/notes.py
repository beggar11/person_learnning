import re
from typing import Optional, List, Dict
from pypinyin import lazy_pinyin


def slugify(text: str) -> str:
    text = text.strip().lower()
    result = []
    for ch in text:
        if '一' <= ch <= '鿿':
            result.append(''.join(lazy_pinyin(ch)))
            result.append('-')
        elif ch.isalnum():
            result.append(ch)
        elif ch in ' -/\\':
            result.append('-')
    slug = ''.join(result)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug or 'untitled'


def _ensure_unique_slug(db, slug: str, exclude_id: int = None) -> str:
    original = slug
    counter = 2
    while True:
        row = db.execute("SELECT id FROM notes WHERE slug = ?", (slug,)).fetchone()
        if row is None or (exclude_id and row["id"] == exclude_id):
            return slug
        slug = f"{original}-{counter}"
        counter += 1


def create_note(db, title: str, content: str = "", slug: str = None) -> Dict:
    if slug is not None:
        slug = slugify(slug)
    else:
        slug = slugify(title)
    slug = _ensure_unique_slug(db, slug)
    db.execute(
        "INSERT INTO notes (title, slug, content) VALUES (?, ?, ?)",
        (title, slug, content)
    )
    db.commit()
    return dict(db.execute("SELECT * FROM notes WHERE id = last_insert_rowid()").fetchone())


def get_note_by_slug(db, slug: str) -> Optional[Dict]:
    row = db.execute("SELECT * FROM notes WHERE slug = ?", (slug,)).fetchone()
    return dict(row) if row else None


def get_note_by_id(db, note_id: int) -> Optional[Dict]:
    row = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    return dict(row) if row else None


def get_all_notes(db, tag: str = None) -> List[Dict]:
    if tag:
        rows = db.execute("""
            SELECT n.* FROM notes n
            JOIN note_tags nt ON n.id = nt.note_id
            JOIN tags t ON t.id = nt.tag_id
            WHERE t.slug = ?
            ORDER BY n.updated_at DESC, n.id DESC
        """, (tag,)).fetchall()
    else:
        rows = db.execute("SELECT * FROM notes ORDER BY updated_at DESC, id DESC").fetchall()
    return [dict(r) for r in rows]


def update_note(db, note_id: int, title: str = None, content: str = None, slug: str = None) -> Optional[Dict]:
    # Check if the note exists
    existing = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if existing is None:
        return None

    # Auto-regenerate slug when title changes and slug not provided
    if title is not None and slug is None:
        slug = slugify(title)

    # Sanitize explicit slug
    if slug is not None:
        slug = slugify(slug)

    # Build a single consolidated UPDATE with only the provided fields
    set_parts = ["updated_at = CURRENT_TIMESTAMP"]
    params = []

    if title is not None:
        set_parts.append("title = ?")
        params.append(title)
    if content is not None:
        set_parts.append("content = ?")
        params.append(content)
    if slug is not None:
        slug = _ensure_unique_slug(db, slug, exclude_id=note_id)
        set_parts.append("slug = ?")
        params.append(slug)

    params.append(note_id)
    db.execute(f"UPDATE notes SET {', '.join(set_parts)} WHERE id = ?", params)
    db.commit()
    return dict(db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone())


def delete_note(db, note_id: int) -> bool:
    cursor = db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    db.commit()
    return cursor.rowcount > 0


def set_note_tags(db, note_id: int, tag_names: list[str]):
    """Replace all tags on a note with the given list of tag names."""
    db.execute("DELETE FROM note_tags WHERE note_id = ?", (note_id,))

    for name in tag_names:
        name = name.strip().lower()
        if not name:
            continue
        tag_slug = slugify(name)

        tag = db.execute("SELECT id FROM tags WHERE slug = ?", (tag_slug,)).fetchone()
        if tag is None:
            db.execute("INSERT INTO tags (name, slug) VALUES (?, ?)", (name, tag_slug))
            tag_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        else:
            tag_id = tag["id"]

        db.execute(
            "INSERT OR IGNORE INTO note_tags (note_id, tag_id) VALUES (?, ?)",
            (note_id, tag_id)
        )

    db.commit()


def get_note_tags(db, note_id: int) -> list[dict]:
    """Get all tags for a note."""
    rows = db.execute("""
        SELECT t.* FROM tags t
        JOIN note_tags nt ON t.id = nt.tag_id
        WHERE nt.note_id = ?
        ORDER BY t.name
    """, (note_id,)).fetchall()
    return [dict(r) for r in rows]


import mistune as _mistune
_md = _mistune.create_markdown()


def render_markdown(content: str) -> str:
    """Convert Markdown to HTML, turning [[wiki-links]] into proper <a> tags."""
    def replace_link(match):
        slug = match.group(1)
        return f'<a href="/note/{slug}" class="internal-link">{slug}</a>'
    processed = re.sub(r'\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]', replace_link, content)
    return _md(processed)


def upsert_tag(db, name: str) -> int:
    """Get or create a tag by name. Returns the tag's id."""
    name = name.strip()
    if not name:
        return None
    slug = slugify(name)
    row = db.execute("SELECT id FROM tags WHERE slug = ?", (slug,)).fetchone()
    if row:
        return row["id"]
    db.execute("INSERT INTO tags (name, slug) VALUES (?, ?)", (name, slug))
    db.commit()
    return db.execute("SELECT last_insert_rowid()").fetchone()[0]
