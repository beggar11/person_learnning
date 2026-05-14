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
    if slug is None:
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


def update_note(db, note_id: int, title: str = None, content: str = None, slug: str = None) -> Dict:
    if title is not None:
        db.execute("UPDATE notes SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (title, note_id))
    if content is not None:
        db.execute("UPDATE notes SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (content, note_id))
    if slug is not None:
        slug = _ensure_unique_slug(db, slug, exclude_id=note_id)
        db.execute("UPDATE notes SET slug = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (slug, note_id))
    db.commit()
    return dict(db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone())


def delete_note(db, note_id: int):
    db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    db.commit()
