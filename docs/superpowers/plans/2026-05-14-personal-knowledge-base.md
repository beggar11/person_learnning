# Personal Knowledge Base Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a personal knowledge base web app with Markdown editing, `[[wiki-links]]`, knowledge graph, and full-text search.

**Architecture:** Python FastAPI server renders Jinja2 templates; client-side JS (EasyMDE, D3.js) enhances editor and graph pages. SQLite + FTS5 for storage and search. Single-file database, zero external dependencies beyond Python packages.

**Tech Stack:** FastAPI, uvicorn, Jinja2, sqlite3 (stdlib), mistune, jieba, EasyMDE (CDN), D3.js (CDN)

---

## File Structure

```
cc/
├── main.py                 # FastAPI app, startup, shutdown
├── config.py               # DB path, settings
├── database.py             # Connection pool, schema init
├── routes/
│   ├── __init__.py
│   ├── pages.py            # GET routes returning HTML
│   └── api.py              # POST/GET routes returning JSON
├── services/
│   ├── __init__.py
│   ├── notes.py            # Note CRUD
│   ├── links.py            # [[wiki-link]] parsing, link table
│   ├── search.py           # FTS5 search
│   └── graph.py            # Graph data assembly
├── templates/
│   ├── base.html           # Layout shell (nav, styles)
│   ├── index.html          # Home: note list + tag cloud
│   ├── note_detail.html    # Rendered note + backlinks
│   ├── note_edit.html      # Editor page
│   ├── search_results.html # FTS search results
│   ├── graph.html          # Knowledge graph page
│   └── tag.html            # Notes by tag
├── static/
│   └── js/
│       ├── editor.js       # EasyMDE init, save handling
│       └── graph.js        # D3-force graph rendering
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Test fixtures (app, db)
│   ├── test_notes.py
│   ├── test_links.py
│   ├── test_search.py
│   └── test_routes.py
├── requirements.txt
└── Dockerfile
```

---

### Task 1: Project Scaffold

**Files:**
- Create: `requirements.txt`
- Create: `config.py`
- Create: `database.py`
- Create: `main.py`
- Create: `routes/__init__.py`
- Create: `services/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Write requirements.txt**

```
fastapi>=0.100.0
uvicorn>=0.23.0
jinja2>=3.1.0
mistune>=3.0.0
jieba>=0.42.0
pytest>=7.0.0
httpx>=0.24.0
```

- [ ] **Step 2: Write config.py**

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "kb.db"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
```

- [ ] **Step 3: Write database.py**

```python
import sqlite3
from config import DB_PATH

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            content TEXT NOT NULL DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_note_id INTEGER NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
            target_note_id INTEGER NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
            UNIQUE(source_note_id, target_note_id)
        );
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS note_tags (
            note_id INTEGER NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
            tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
            PRIMARY KEY (note_id, tag_id)
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
            title, content, content=notes, content_rowid=id
        );
        CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN
            INSERT INTO notes_fts(rowid, title, content) VALUES (new.id, new.title, new.content);
        END;
        CREATE TRIGGER IF NOT EXISTS notes_ad AFTER DELETE ON notes BEGIN
            INSERT INTO notes_fts(notes_fts, rowid, title, content) VALUES ('delete', old.id, old.title, old.content);
        END;
        CREATE TRIGGER IF NOT EXISTS notes_au AFTER UPDATE ON notes BEGIN
            INSERT INTO notes_fts(notes_fts, rowid, title, content) VALUES ('delete', old.id, old.title, old.content);
            INSERT INTO notes_fts(rowid, title, content) VALUES (new.id, new.title, new.content);
        END;
    """)
    conn.commit()
    conn.close()
```

- [ ] **Step 4: Write main.py**

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from config import STATIC_DIR
from database import init_db
from routes import pages, api

app = FastAPI(title="Knowledge Base")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.include_router(pages.router)
app.include_router(api.router)

@app.on_event("startup")
def startup():
    init_db()
```

- [ ] **Step 5: Write tests/conftest.py**

```python
import pytest
from fastapi.testclient import TestClient
from config import DB_PATH, BASE_DIR
from database import init_db, get_db

@pytest.fixture
def app():
    import os
    import main
    test_db = BASE_DIR / "test_kb.db"
    import config
    config.DB_PATH = test_db
    from database import init_db
    init_db()
    yield main.app
    if test_db.exists():
        test_db.unlink()

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture
def db(app):
    from database import get_db
    conn = get_db()
    yield conn
    conn.close()
```

- [ ] **Step 6: Install deps and verify app starts**

```bash
cd /Users/mymac/cc && pip install -r requirements.txt && python -c "from main import app; print('OK')"
```

Expected: prints "OK"

- [ ] **Step 7: Run pytest to verify test setup**

```bash
cd /Users/mymac/cc && python -m pytest tests/ -v
```

Expected: 0 tests collected (no tests yet), no errors

- [ ] **Step 8: Commit**

```bash
git add requirements.txt config.py database.py main.py routes/ services/ tests/
git commit -m "feat: project scaffold with FastAPI + SQLite setup"
```

---

### Task 2: Note Service (CRUD)

**Files:**
- Create: `services/notes.py`
- Create: `tests/test_notes.py`

- [ ] **Step 1: Write failing tests in tests/test_notes.py**

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/mymac/cc && python -m pytest tests/test_notes.py -v
```

Expected: all fail with ModuleNotFoundError

- [ ] **Step 3: Write services/notes.py**

```python
import re
from pypinyin import lazy_pinyin

def slugify(text: str) -> str:
    text = text.strip().lower()
    # Convert Chinese characters to pinyin
    result = []
    for ch in text:
        if '一' <= ch <= '鿿':
            result.extend(lazy_pinyin(ch))
        elif ch.isalnum() or ch in ' -':
            result.append(ch)
    slug = ''.join(result)
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug or 'untitled'

def _ensure_unique_slug(db, slug: str, exclude_id: int = None) -> str:
    original = slug
    counter = 2
    while True:
        query = "SELECT id FROM notes WHERE slug = ?"
        params = [slug]
        row = db.execute(query, params).fetchone()
        if row is None or (exclude_id and row["id"] == exclude_id):
            return slug
        slug = f"{original}-{counter}"
        counter += 1

def create_note(db, title: str, content: str = "", slug: str = None) -> dict:
    if slug is None:
        slug = slugify(title)
    slug = _ensure_unique_slug(db, slug)
    db.execute(
        "INSERT INTO notes (title, slug, content) VALUES (?, ?, ?)",
        (title, slug, content)
    )
    db.commit()
    return dict(db.execute("SELECT * FROM notes WHERE id = last_insert_rowid()").fetchone())

def get_note_by_slug(db, slug: str) -> dict | None:
    row = db.execute("SELECT * FROM notes WHERE slug = ?", (slug,)).fetchone()
    return dict(row) if row else None

def get_note_by_id(db, note_id: int) -> dict | None:
    row = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    return dict(row) if row else None

def get_all_notes(db, tag: str = None) -> list[dict]:
    if tag:
        rows = db.execute("""
            SELECT n.* FROM notes n
            JOIN note_tags nt ON n.id = nt.note_id
            JOIN tags t ON t.id = nt.tag_id
            WHERE t.slug = ?
            ORDER BY n.updated_at DESC
        """, (tag,)).fetchall()
    else:
        rows = db.execute("SELECT * FROM notes ORDER BY updated_at DESC").fetchall()
    return [dict(r) for r in rows]

def update_note(db, note_id: int, title: str = None, content: str = None, slug: str = None) -> dict:
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /Users/mymac/cc && python -m pytest tests/test_notes.py -v
```

Expected: all 5 tests pass

- [ ] **Step 5: Add pypinyin to requirements.txt**

Edit `requirements.txt` and add `pypinyin>=0.49.0`, then:

```bash
pip install pypinyin
```

- [ ] **Step 6: Commit**

```bash
git add services/notes.py tests/test_notes.py requirements.txt
git commit -m "feat: note CRUD service with slug generation"
```

---

### Task 3: Link Service (Wiki-Link Parsing)

**Files:**
- Create: `services/links.py`
- Create: `tests/test_links.py`

- [ ] **Step 1: Write failing tests in tests/test_links.py**

```python
from services.links import extract_links, sync_links, get_backlinks, get_broken_links

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

def test_get_broken_links(db):
    from services.notes import create_note
    create_note(db, title="Source", content="[[exists]] [[missing]]")
    create_note(db, title="Exists", slug="exists")
    sync_links(db, note_id=1, content="[[exists]] [[missing]]")

    broken = get_broken_links(db, note_id=1)
    assert len(broken) == 1
    assert broken[0] == "missing"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/mymac/cc && python -m pytest tests/test_links.py -v
```

Expected: all fail

- [ ] **Step 3: Write services/links.py**

```python
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
            db.commit()
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /Users/mymac/cc && python -m pytest tests/test_links.py -v
```

Expected: all 6 tests pass

- [ ] **Step 5: Commit**

```bash
git add services/links.py tests/test_links.py
git commit -m "feat: wiki-link parsing and sync service"
```

---

### Task 4: Search Service (FTS5)

**Files:**
- Create: `services/search.py`
- Create: `tests/test_search.py`

- [ ] **Step 1: Write failing tests in tests/test_search.py**

```python
from services.search import index_note, search_notes

def test_search_finds_by_title(db):
    from services.notes import create_note
    create_note(db, title="Python 入门", content="这是一篇教程")
    create_note(db, title="JavaScript 基础", content="前端必学")

    results = search_notes(db, "python")
    assert len(results) == 1
    assert results[0]["title"] == "Python 入门"

def test_search_finds_by_content(db):
    from services.notes import create_note
    create_note(db, title="Note A", content="深度学习基础")
    results = search_notes(db, "深度")
    assert len(results) == 1

def test_search_no_results(db):
    results = search_notes(db, "nonexistent")
    assert results == []

def test_search_chinese(db):
    from services.notes import create_note
    create_note(db, title="机器学习", content="监督学习和无监督学习")
    results = search_notes(db, "监督")
    assert len(results) == 1
    results2 = search_notes(db, "机器学习")
    assert len(results2) >= 1
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/mymac/cc && python -m pytest tests/test_search.py -v
```

Expected: all fail

- [ ] **Step 3: Write services/search.py**

```python
import jieba

def _tokenize(text: str) -> str:
    """Tokenize text for FTS5. Jieba cuts Chinese words; plain ASCII passes through."""
    if not text:
        return ""
    tokens = list(jieba.cut(text))
    return " ".join(t.strip() for t in tokens if t.strip())

def index_note(db, note_id: int, title: str, content: str):
    """Manually update FTS5 index for a note (used when FTS triggers aren't sufficient)."""
    tokenized_title = _tokenize(title)
    tokenized_content = _tokenize(content)
    # FTS triggers handle the actual insert/update/delete via content sync
    # But we can force a re-index by updating the note row
    db.execute("UPDATE notes SET content = ? WHERE id = ?", (content, note_id))
    db.commit()

def search_notes(db, query: str, limit: int = 20) -> list[dict]:
    """Full-text search notes by title and content."""
    tokenized = _tokenize(query)
    if not tokenized.strip():
        return []

    rows = db.execute("""
        SELECT n.id, n.title, n.slug,
               snippet(notes_fts, 1, '<mark>', '</mark>', '...', 32) AS title_hl,
               snippet(notes_fts, 2, '<mark>', '</mark>', '...', 64) AS content_hl
        FROM notes_fts f
        JOIN notes n ON n.id = f.rowid
        WHERE notes_fts MATCH ?
        ORDER BY bm25(notes_fts, 0.0, 10.0, 5.0)
        LIMIT ?
    """, (tokenized, limit)).fetchall()
    return [dict(r) for r in rows]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /Users/mymac/cc && python -m pytest tests/test_search.py -v
```

Expected: all 4 tests pass

- [ ] **Step 5: Commit**

```bash
git add services/search.py tests/test_search.py
git commit -m "feat: FTS5 search with jieba tokenization"
```

---

### Task 5: Graph Service & API Routes

**Files:**
- Create: `services/graph.py`
- Create: `routes/api.py`

- [ ] **Step 1: Write services/graph.py**

```python
def get_graph_data(db, limit: int = 200) -> dict:
    """Return {nodes, edges} for knowledge graph visualization."""
    nodes = db.execute("""
        SELECT n.slug, n.title, COUNT(l2.id) AS degree
        FROM notes n
        LEFT JOIN links l2 ON l2.target_note_id = n.id OR l2.source_note_id = n.id
        WHERE n.content != ''
        GROUP BY n.id
        ORDER BY degree DESC
        LIMIT ?
    """, (limit,)).fetchall()

    node_slugs = {row["slug"] for row in nodes}
    if not node_slugs:
        return {"nodes": [], "edges": []}

    placeholders = ",".join("?" * len(node_slugs))
    edges = db.execute(f"""
        SELECT n1.slug AS source, n2.slug AS target
        FROM links l
        JOIN notes n1 ON n1.id = l.source_note_id
        JOIN notes n2 ON n2.id = l.target_note_id
        WHERE n1.slug IN ({placeholders}) AND n2.slug IN ({placeholders})
    """, list(node_slugs) + list(node_slugs)).fetchall()

    return {
        "nodes": [{"slug": r["slug"], "title": r["title"], "degree": r["degree"]} for r in nodes],
        "edges": [{"source": r["source"], "target": r["target"]} for r in edges],
    }
```

- [ ] **Step 2: Write routes/api.py**

```python
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from database import get_db
from services.notes import create_note, get_note_by_slug, get_note_by_id, get_all_notes, update_note, delete_note
from services.links import sync_links, get_backlinks
from services.search import search_notes
from services.graph import get_graph_data

router = APIRouter(prefix="/api")

@router.post("/notes")
def api_save_note(request: Request, title: str = Form(...), content: str = Form(""), slug: str = Form(None), note_id: int = Form(None), tags: str = Form("")):
    db = get_db()
    if note_id:
        note = get_note_by_id(db, note_id)
        if note is None:
            raise HTTPException(status_code=404, detail="Note not found")
        note = update_note(db, note_id=note_id, title=title, content=content)
    else:
        note = create_note(db, title=title, content=content, slug=slug)
    sync_links(db, note["id"], content)
    tag_names = [t.strip() for t in tags.split(",") if t.strip()]
    if tag_names:
        from services.notes import set_note_tags
        set_note_tags(db, note["id"], tag_names)
    return {"status": "ok", "slug": note["slug"], "id": note["id"]}

@router.get("/notes")
def api_list_notes(tag: str = None):
    db = get_db()
    notes = get_all_notes(db, tag=tag)
    return {"notes": notes}

@router.get("/graph")
def api_graph(limit: int = 200):
    db = get_db()
    return get_graph_data(db, limit=limit)

@router.post("/notes/{note_id}/delete")
def api_delete(note_id: int):
    db = get_db()
    delete_note(db, note_id)
    return {"status": "ok"}
```

- [ ] **Step 3: Commit**

```bash
git add services/graph.py routes/api.py
git commit -m "feat: graph data service and JSON API routes"
```

---

### Task 6: Base Template & Static Assets

**Files:**
- Create: `templates/base.html`
- Create: `static/css/style.css`
- Create: `static/js/editor.js`
- Create: `static/js/graph.js`

- [ ] **Step 1: Write templates/base.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Knowledge Base{% endblock %}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.css">
    <script src="https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <nav class="nav">
        <div class="nav-inner">
            <a href="/" class="nav-brand">KB</a>
            <div class="nav-links">
                <a href="/graph">图谱</a>
                <a href="/note/new">+ 新建</a>
                <form action="/search" method="get" class="nav-search">
                    <input type="text" name="q" placeholder="搜索..." value="{{ query or '' }}">
                </form>
            </div>
        </div>
    </nav>

    <main class="main">
        {% block content %}{% endblock %}
    </main>

    {% block scripts %}{% endblock %}
</body>
</html>
```

- [ ] **Step 2: Write static/css/style.css**

```css
:root {
    --bg: #fafaf9;
    --bg-card: #ffffff;
    --text: #1c1917;
    --text-muted: #78716c;
    --border: #e7e5e4;
    --accent: #2563eb;
    --accent-hover: #1d4ed8;
    --radius: 8px;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
}

.nav {
    background: var(--bg-card);
    border-bottom: 1px solid var(--border);
    position: sticky; top: 0; z-index: 100;
}
.nav-inner {
    max-width: 960px; margin: 0 auto;
    display: flex; align-items: center; gap: 24px; padding: 0 20px; height: 52px;
}
.nav-brand { font-weight: 700; font-size: 18px; text-decoration: none; color: var(--text); }
.nav-links { display: flex; align-items: center; gap: 16px; margin-left: auto; }
.nav-links a { text-decoration: none; color: var(--text-muted); font-size: 14px; }
.nav-links a:hover { color: var(--text); }
.nav-search input {
    padding: 6px 12px; border: 1px solid var(--border); border-radius: var(--radius);
    font-size: 14px; width: 180px; background: var(--bg);
}

.main { max-width: 960px; margin: 0 auto; padding: 32px 20px; }

.note-list { display: flex; flex-direction: column; gap: 8px; }
.note-item {
    display: block; padding: 16px 20px; background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius); text-decoration: none; color: var(--text);
}
.note-item:hover { border-color: var(--accent); }
.note-item h3 { font-size: 16px; margin-bottom: 4px; }
.note-item .meta { font-size: 12px; color: var(--text-muted); }

.note-content {
    background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 32px; max-width: 780px;
}
.note-content h1, .note-content h2, .note-content h3 { margin: 24px 0 12px; }
.note-content h1:first-child { margin-top: 0; }
.note-content p { margin-bottom: 12px; }
.note-content a { color: var(--accent); }
.note-content .broken-link { color: #dc2626; border-bottom: 1px dashed #dc2626; cursor: pointer; }
.note-content pre { background: #f5f5f4; padding: 16px; border-radius: var(--radius); overflow-x: auto; }
.note-content code { font-family: "SF Mono", Menlo, monospace; font-size: 13px; }
.note-content blockquote {
    border-left: 3px solid var(--accent); padding-left: 16px; color: var(--text-muted); margin: 12px 0;
}

.backlinks { margin-top: 32px; padding-top: 24px; border-top: 1px solid var(--border); }
.backlinks h3 { font-size: 14px; color: var(--text-muted); margin-bottom: 12px; }

.tag-cloud { display: flex; flex-wrap: wrap; gap: 8px; }
.tag { padding: 4px 12px; background: #f5f5f4; border-radius: 20px; font-size: 13px; text-decoration: none; color: var(--text); }
.tag:hover { background: var(--accent); color: white; }

.graph-container { width: 100%; height: 70vh; border: 1px solid var(--border); border-radius: var(--radius); background: var(--bg-card); }

.editor-wrapper { max-width: 900px; margin: 0 auto; }
.editor-wrapper .EasyMDEContainer .CodeMirror { height: 60vh; }

.btn {
    padding: 8px 20px; border: none; border-radius: var(--radius); font-size: 14px;
    cursor: pointer; background: var(--accent); color: white; text-decoration: none; display: inline-block;
}
.btn:hover { background: var(--accent-hover); }
.btn-ghost { background: transparent; color: var(--text); border: 1px solid var(--border); }
.btn-ghost:hover { background: #f5f5f4; }

.search-results { display: flex; flex-direction: column; gap: 12px; }
.search-result { padding: 16px 20px; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); }
.search-result mark { background: #fef08a; }
.empty { text-align: center; color: var(--text-muted); padding: 48px 0; font-size: 15px; }
```

- [ ] **Step 3: Write static/js/editor.js**

```javascript
document.addEventListener('DOMContentLoaded', () => {
    const textarea = document.getElementById('editor-textarea');
    if (!textarea) return;

    const easyMDE = new EasyMDE({
        element: textarea,
        spellChecker: false,
        autosave: { enabled: false },
        placeholder: '开始写作...使用 [[slug]] 创建链接',
        toolbar: ['bold', 'italic', 'heading', '|', 'quote', 'unordered-list', 'ordered-list', '|', 'link', 'image', '|', 'preview', 'side-by-side', 'fullscreen', '|', 'guide'],
    });

    document.getElementById('save-btn').addEventListener('click', () => {
        const form = document.getElementById('note-form');
        const formData = new FormData(form);
        formData.set('content', easyMDE.value());

        fetch('/api/notes', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => {
                if (data.slug) {
                    window.location.href = '/note/' + data.slug;
                }
            });
    });
});
```

- [ ] **Step 4: Write static/js/graph.js**

```javascript
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('graph-container');
    if (!container) return;

    const width = container.clientWidth;
    const height = container.clientHeight;

    const svg = d3.select('#graph-container')
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    fetch('/api/graph')
        .then(res => res.json())
        .then(data => {
            const simulation = d3.forceSimulation(data.nodes)
                .force('link', d3.forceLink(data.edges).id(d => d.slug).distance(80))
                .force('charge', d3.forceManyBody().strength(-200))
                .force('center', d3.forceCenter(width / 2, height / 2));

            const link = svg.append('g')
                .selectAll('line')
                .data(data.edges)
                .join('line')
                .attr('stroke', '#d6d3d1')
                .attr('stroke-width', 1);

            const node = svg.append('g')
                .selectAll('circle')
                .data(data.nodes)
                .join('circle')
                .attr('r', d => Math.max(4, Math.min(20, d.degree * 3 + 4)))
                .attr('fill', '#2563eb')
                .attr('cursor', 'pointer')
                .on('click', (event, d) => {
                    window.location.href = '/note/' + d.slug;
                })
                .call(d3.drag()
                    .on('start', (event, d) => { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
                    .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y; })
                    .on('end', (event, d) => { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; })
                );

            const labels = svg.append('g')
                .selectAll('text')
                .data(data.nodes)
                .join('text')
                .text(d => d.title.length > 10 ? d.title.slice(0, 10) + '...' : d.title)
                .attr('font-size', 10)
                .attr('dx', 14)
                .attr('dy', 4)
                .attr('fill', '#78716c');

            simulation.on('tick', () => {
                link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
                node.attr('cx', d => d.x).attr('cy', d => d.y);
                labels.attr('x', d => d.x).attr('y', d => d.y);
            });
        });
});
```

- [ ] **Step 5: Commit**

```bash
git add templates/base.html static/
git commit -m "feat: base template, CSS, and client-side JS"
```

---

### Task 7: Page Routes & Templates

**Files:**
- Create: `routes/pages.py`
- Create: `templates/index.html`
- Create: `templates/note_detail.html`
- Create: `templates/note_edit.html`
- Create: `templates/search_results.html`
- Create: `templates/graph.html`
- Create: `templates/tag.html`
- Create: `tests/test_routes.py`

- [ ] **Step 1: Write routes/pages.py**

```python
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from database import get_db
from services.notes import get_note_by_slug, get_all_notes
from services.links import get_backlinks, extract_links
from services.search import search_notes
from services.graph import get_graph_data

router = APIRouter()
templates = __import__('jinja2').Environment(
    loader=__import__('jinja2').FileSystemLoader("templates")
)

_tpl_cache = {}
def render(name: str, **ctx) -> str:
    if name not in _tpl_cache:
        with open(f"templates/{name}") as f:
            _tpl_cache[name] = templates.from_string(f.read())
    return _tpl_cache[name].render(**ctx)


@router.get("/", response_class=HTMLResponse)
def page_index(request: Request, tag: str = None):
    db = get_db()
    notes = get_all_notes(db, tag=tag)
    tags = db.execute("SELECT * FROM tags ORDER BY name").fetchall()
    with open("templates/index.html") as f:
        tpl = templates.from_string(f.read())
    return tpl.render(notes=notes, tags=[dict(t) for t in tags], current_tag=tag)

@router.get("/note/new", response_class=HTMLResponse)
def page_new_note(request: Request):
    with open("templates/note_edit.html") as f:
        tpl = templates.from_string(f.read())
    return tpl.render(note=None)

@router.get("/note/{slug}", response_class=HTMLResponse)
def page_note_detail(request: Request, slug: str):
    db = get_db()
    note = get_note_by_slug(db, slug)
    if note is None:
        return HTMLResponse("<h1>404</h1>", status_code=404)
    backlinks = get_backlinks(db, note["id"])
    with open("templates/note_detail.html") as f:
        tpl = templates.from_string(f.read())
    return tpl.render(note=note, backlinks=backlinks)

@router.get("/note/{slug}/edit", response_class=HTMLResponse)
def page_note_edit(request: Request, slug: str):
    db = get_db()
    note = get_note_by_slug(db, slug)
    if note is None:
        return HTMLResponse("<h1>404</h1>", status_code=404)
    from services.notes import get_note_tags
    tags = get_note_tags(db, note["id"])
    note_tags = ",".join(t["name"] for t in tags)
    with open("templates/note_edit.html") as f:
        tpl = templates.from_string(f.read())
    return tpl.render(note=note, note_tags=note_tags)

@router.get("/search", response_class=HTMLResponse)
def page_search(request: Request, q: str = ""):
    db = get_db()
    results = search_notes(db, q) if q.strip() else []
    with open("templates/search_results.html") as f:
        tpl = templates.from_string(f.read())
    return tpl.render(query=q, results=results)

@router.get("/graph", response_class=HTMLResponse)
def page_graph(request: Request):
    with open("templates/graph.html") as f:
        tpl = templates.from_string(f.read())
    return tpl.render()

@router.get("/tag/{slug}", response_class=HTMLResponse)
def page_tag(request: Request, slug: str):
    db = get_db()
    notes = get_all_notes(db, tag=slug)
    tag_name = db.execute("SELECT name FROM tags WHERE slug = ?", (slug,)).fetchone()
    tag_name = tag_name["name"] if tag_name else slug
    with open("templates/index.html") as f:
        tpl = templates.from_string(f.read())
    tags = db.execute("SELECT * FROM tags ORDER BY name").fetchall()
    return tpl.render(notes=notes, tags=[dict(t) for t in tags], current_tag=slug, tag_name=tag_name)
```

- [ ] **Step 2: Write templates/index.html**

```html
{% extends "base.html" %}
{% block title %}{{ tag_name or '首页' }} - Knowledge Base{% endblock %}
{% block content %}
<h2 style="margin-bottom: 20px;">{% if tag_name %}#{{ tag_name }}{% else %}最近笔记{% endif %}</h2>

{% if tags %}
<div class="tag-cloud" style="margin-bottom: 24px;">
    {% for t in tags %}
    <a href="/tag/{{ t.slug }}" class="tag">{{ t.name }}</a>
    {% endfor %}
</div>
{% endif %}

{% if notes %}
<div class="note-list">
    {% for note in notes %}
    <a href="/note/{{ note.slug }}" class="note-item">
        <h3>{{ note.title }}</h3>
        <span class="meta">{{ note.updated_at[:10] }}{% if not note.content %} · 草稿{% endif %}</span>
    </a>
    {% endfor %}
</div>
{% else %}
<div class="empty">还没有笔记，<a href="/note/new">写一篇</a></div>
{% endif %}
{% endblock %}
```

- [ ] **Step 3: Write templates/note_detail.html**

```html
{% extends "base.html" %}
{% block title %}{{ note.title }} - Knowledge Base{% endblock %}
{% block content %}

{% set content = note.content %}
{# Replace [[slug]] with links, [[slug|alias]] with aliased links #}
{% set content_rendered = content %}
{# We'll do actual link replacement in Python; here we rely on server-side rendering #}

<div class="note-content">
    {{ note.html_content | safe if note.html_content else note.content }}
</div>

<div style="margin-top: 24px;">
    <a href="/note/{{ note.slug }}/edit" class="btn">编辑</a>
    <button class="btn btn-ghost" onclick="if(confirm('删除？')){fetch('/api/notes/{{ note.id }}/delete',{method:'POST'}).then(()=>location.href='/')}">删除</button>
</div>

{% if backlinks %}
<div class="backlinks">
    <h3>链接到这里的笔记</h3>
    <div class="note-list" style="margin-top: 12px;">
        {% for bl in backlinks %}
        <a href="/note/{{ bl.slug }}" class="note-item">
            <h3>{{ bl.title }}</h3>
        </a>
        {% endfor %}
    </div>
</div>
{% endif %}

{% endblock %}
```

- [ ] **Step 4: Write templates/note_edit.html**

```html
{% extends "base.html" %}
{% block title %}{% if note %}编辑 {{ note.title }}{% else %}新建笔记{% endif %} - Knowledge Base{% endblock %}
{% block content %}

<div class="editor-wrapper">
    <h2 style="margin-bottom: 20px;">{% if note %}编辑{% else %}新建{% endif %}笔记</h2>
    <form id="note-form">
        {% if note %}<input type="hidden" name="note_id" value="{{ note.id }}">{% endif %}
        <div style="margin-bottom: 12px;">
            <input type="text" name="title" placeholder="标题" value="{{ note.title if note else '' }}"
                   style="width: 100%; padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius); font-size: 18px;">
        </div>
        <textarea id="editor-textarea" name="content">{{ note.content if note else '' }}</textarea>
        <div style="margin-bottom: 12px; margin-top: 12px;">
            <input type="text" name="tags" placeholder="标签（逗号分隔）" value="{{ note_tags if note_tags else '' }}"
                   style="width: 100%; padding: 8px 14px; border: 1px solid var(--border); border-radius: var(--radius); font-size: 14px;">
        </div>
        <div style="margin-top: 16px;">
            <button type="button" id="save-btn" class="btn">保存</button>
            {% if note %}
            <a href="/note/{{ note.slug }}" class="btn btn-ghost">取消</a>
            {% else %}
            <a href="/" class="btn btn-ghost">取消</a>
            {% endif %}
        </div>
    </form>
</div>

<script src="/static/js/editor.js"></script>
{% endblock %}
```

- [ ] **Step 5: Write templates/search_results.html**

```html
{% extends "base.html" %}
{% block title %}搜索: {{ query }} - Knowledge Base{% endblock %}
{% block content %}
<h2 style="margin-bottom: 20px;">搜索: "{{ query }}"</h2>

{% if results %}
<div class="search-results">
    {% for r in results %}
    <a href="/note/{{ r.slug }}" class="search-result">
        <h3>{{ r.title_hl | safe if r.title_hl else r.title }}</h3>
        <p style="font-size: 13px; color: var(--text-muted); margin-top: 4px;">
            {% if r.content_hl %}{{ r.content_hl | safe }}{% endif %}
        </p>
    </a>
    {% endfor %}
</div>
{% elif query %}
<div class="empty">没有找到匹配 "{{ query }}" 的结果</div>
{% endif %}
{% endblock %}
```

- [ ] **Step 6: Write templates/graph.html**

```html
{% extends "base.html" %}
{% block title %}知识图谱 - Knowledge Base{% endblock %}
{% block content %}
<h2 style="margin-bottom: 20px;">知识图谱</h2>
<div id="graph-container" class="graph-container"></div>
<script src="/static/js/graph.js"></script>
{% endblock %}
```

- [ ] **Step 7: Write templates/tag.html** (same as index.html, already handled by route)

Actually, the tag route uses `index.html` template already. No separate `tag.html` needed.

- [ ] **Step 8: Write tests/test_routes.py**

```python
def test_home_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "最近笔记" in resp.text

def test_new_note_page(client):
    resp = client.get("/note/new")
    assert resp.status_code == 200
    assert "新建" in resp.text

def test_graph_page(client):
    resp = client.get("/graph")
    assert resp.status_code == 200
    assert "graph-container" in resp.text

def test_search_page(client):
    resp = client.get("/search?q=test")
    assert resp.status_code == 200

def test_create_note_via_api(client):
    resp = client.post("/api/notes", data={"title": "Hello", "content": "World"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["slug"] == "hello"

def test_view_created_note(client):
    client.post("/api/notes", data={"title": "View Test", "content": "# Hello"})
    resp = client.get("/note/view-test")
    assert resp.status_code == 200
    assert "View Test" in resp.text

def test_edit_note_page(client):
    client.post("/api/notes", data={"title": "Edit Test"})
    resp = client.get("/note/edit-test/edit")
    assert resp.status_code == 200
    assert "Edit Test" in resp.text

def test_search_api(client):
    resp = client.get("/search?q=nonexistent_xyz")
    assert resp.status_code == 200
    assert "没有找到" in resp.text

def test_graph_api(client):
    client.post("/api/notes", data={"title": "G1", "content": "[[g2]]"})
    resp = client.get("/api/graph")
    assert resp.status_code == 200
    data = resp.json()
    assert "nodes" in data
    assert "edges" in data

def test_note_not_found(client):
    resp = client.get("/note/nonexistent-12345")
    assert resp.status_code == 404
```

- [ ] **Step 9: Run tests to verify**

```bash
cd /Users/mymac/cc && python -m pytest tests/test_routes.py -v
```

Expected: all 10 tests pass

- [ ] **Step 10: Commit**

```bash
git add routes/pages.py templates/ tests/test_routes.py
git commit -m "feat: all page routes and Jinja2 templates"
```

---

### Task 8: Markdown Rendering & Wiki-Link Processing

**Files:**
- Modify: `services/notes.py` (add render_markdown)
- Modify: `routes/pages.py` (use render_markdown in detail page)

- [ ] **Step 1: Add render_markdown to services/notes.py**

Append to `services/notes.py`:

```python
import mistune
import re

_md = mistune.create_markdown()

def render_markdown(content: str) -> str:
    """Convert Markdown to HTML, turning [[wiki-links]] into proper <a> tags."""
    # First, replace [[slug]] and [[slug|label]] with placeholder HTML
    def replace_link(match):
        slug = match.group(1)
        # Check if note exists (best effort — caller should pass db for accuracy)
        return f'<a href="/note/{slug}" class="internal-link">{slug}</a>'

    processed = re.sub(r'\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]', replace_link, content)
    return _md(processed)
```

- [ ] **Step 2: Update routes/pages.py to render markdown for detail pages**

In `page_note_detail`, add:

```python
from services.notes import render_markdown

# Inside page_note_detail, after getting note:
html_content = render_markdown(note["content"])
note["html_content"] = html_content
```

- [ ] **Step 3: Commit**

```bash
git add services/notes.py routes/pages.py
git commit -m "feat: Markdown rendering with wiki-link conversion"
```

---

### Task 9: Tag Management

**Files:**
- Modify: `services/notes.py` (add tag methods)
- Create: `tests/test_tags.py`

- [ ] **Step 1: Add tag methods to services/notes.py**

Append to `services/notes.py`:

```python
def upsert_tag(db, name: str) -> int:
    slug = slugify(name)
    row = db.execute("SELECT id FROM tags WHERE slug = ?", (slug,)).fetchone()
    if row:
        return row["id"]
    db.execute("INSERT INTO tags (name, slug) VALUES (?, ?)", (name, slug))
    db.commit()
    return db.execute("SELECT last_insert_rowid()").fetchone()[0]

def set_note_tags(db, note_id: int, tag_names: list[str]):
    db.execute("DELETE FROM note_tags WHERE note_id = ?", (note_id,))
    for name in tag_names:
        name = name.strip()
        if name:
            tag_id = upsert_tag(db, name)
            db.execute("INSERT OR IGNORE INTO note_tags (note_id, tag_id) VALUES (?, ?)", (note_id, tag_id))
    db.commit()

def get_note_tags(db, note_id: int) -> list[dict]:
    rows = db.execute("""
        SELECT t.name, t.slug FROM tags t
        JOIN note_tags nt ON nt.tag_id = t.id
        WHERE nt.note_id = ?
        ORDER BY t.name
    """, (note_id,)).fetchall()
    return [dict(r) for r in rows]
```

- [ ] **Step 2: Write tests/test_tags.py**

```python
from services.notes import upsert_tag, set_note_tags, get_note_tags, create_note

def test_upsert_tag(db):
    id1 = upsert_tag(db, "Python")
    id2 = upsert_tag(db, "Python")
    assert id1 == id2

    id3 = upsert_tag(db, "JavaScript")
    assert id3 != id1

def test_set_and_get_tags(db):
    create_note(db, title="Test")
    set_note_tags(db, 1, ["Python", "Web"])
    tags = get_note_tags(db, 1)
    assert len(tags) == 2
    assert {t["name"] for t in tags} == {"Python", "Web"}

def test_set_tags_replaces(db):
    create_note(db, title="Test")
    set_note_tags(db, 1, ["A", "B"])
    set_note_tags(db, 1, ["C"])
    tags = get_note_tags(db, 1)
    assert len(tags) == 1
    assert tags[0]["name"] == "C"

def test_empty_tags(db):
    create_note(db, title="Test")
    set_note_tags(db, 1, ["  ", ""])
    tags = get_note_tags(db, 1)
    assert tags == []
```

- [ ] **Step 3: Run tag tests**

```bash
cd /Users/mymac/cc && python -m pytest tests/test_tags.py -v
```

Expected: all 4 tests pass

- [ ] **Step 4: Commit**

```bash
git add services/notes.py tests/test_tags.py
git commit -m "feat: tag management (create, set, get)"
```

---

### Task 10: Deployment Config

**Files:**
- Create: `Dockerfile`

- [ ] **Step 1: Write Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data
ENV KB_DB_PATH=/data/kb.db

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Update config.py for env override**

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("KB_DB_PATH", BASE_DIR / "kb.db"))
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
```

- [ ] **Step 3: Test Docker build and run**

```bash
cd /Users/mymac/cc && docker build -t kb . && docker run --rm -p 8000:8000 kb
```

Verify you can access http://localhost:8000

- [ ] **Step 4: Commit**

```bash
git add Dockerfile config.py
git commit -m "feat: Dockerfile and env-configurable DB path"
```

---

### Task 11: Final Integration Verification

- [ ] **Step 1: Run all tests**

```bash
cd /Users/mymac/cc && python -m pytest tests/ -v
```

Expected: all tests pass (~25 tests)

- [ ] **Step 2: Manual smoke test**

```bash
cd /Users/mymac/cc && uvicorn main:app --reload &
```

Then:
1. Open http://localhost:8000 — see empty home page
2. Click "+ 新建" — editor page loads
3. Write a note with `[[link]]` syntax — saves, redirects to detail page
4. Create another note linking back — backlinks appear
5. Visit /graph — see connected nodes
6. Use search — find notes
