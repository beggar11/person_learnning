# Personal Knowledge Base — Design Spec

## Overview

A personal knowledge base web application inspired by Obsidian/Roam, focused on networked thinking through bidirectional links and knowledge graph visualization.

**Stack:** Python FastAPI + SQLite (FTS5) + Jinja2 + lightweight client-side JS

## Architecture

```
Browser (Jinja2 HTML + JS enhancements)
  └── HTTP/JSON/HTML ── FastAPI Server
        ├── Routes & API: note CRUD, search, graph data
        ├── Core logic: markdown parsing, link extraction, FTS indexing
        └── SQLite + FTS5
```

- Server-rendered pages with Jinja2 templates
- Client-side JS only where interactivity is needed (editor, graph, search suggestions)
- Single SQLite file for all data, including full-text index

## Data Model

### notes
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| title | TEXT | |
| slug | TEXT UNIQUE | URL-friendly identifier, used in `[[wiki-links]]` |
| content | TEXT | Full Markdown body |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### links
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| source_note_id | INTEGER FK → notes.id | Which note contains the `[[link]]` |
| target_note_id | INTEGER FK → notes.id | Which note is being linked to |

- Populated automatically on save by parsing `[[slug]]` from content
- Rebuilt on each save: old links deleted, new ones inserted
- Reverse links are a simple JOIN: `SELECT * FROM links WHERE target_note_id = ?`

### tags
| Column | Type |
|--------|------|
| id | INTEGER PK |
| name | TEXT |
| slug | TEXT UNIQUE |

### note_tags
| Column | Type |
|--------|------|
| note_id | INTEGER FK → notes.id |
| tag_id | INTEGER FK → tags.id |

### notes_fts
FTS5 virtual table indexing title + content. Updated synchronously on save.

## Routes

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Home — note list, recent first, tag cloud sidebar |
| GET | `/note/{slug}` | Note detail — rendered Markdown, backlinks |
| GET | `/note/{slug}/edit` | Edit page — Markdown editor with live preview |
| GET | `/note/new` | Create new note |
| POST | `/api/notes` | Create or update a note (JSON) |
| GET | `/api/notes` | List notes (JSON, for filtering) |
| GET | `/api/graph` | Graph data: `{nodes, edges}` (JSON) |
| GET | `/search?q=` | Search results page |
| GET | `/tag/{slug}` | Notes by tag |

## Key Workflows

### Save → Link Parsing
1. Editor submits Markdown content via `POST /api/notes`
2. Backend regex-extracts all `[[target-slug]]` patterns
3. Looks up or creates placeholder target notes by slug
4. Clears existing links for this note, inserts new ones
5. Updates FTS index
6. Saves note, returns redirect to `/note/{slug}`

### Knowledge Graph
- `GET /api/graph` returns `{nodes: [{id, title, slug}], edges: [{source, target}]}`
- Frontend renders with D3-force layout
- Node radius scales by degree (number of links)
- Click node → navigate to note

### Full-Text Search
- Content tokenized with jieba for Chinese, written to FTS5 index
- Query uses `MATCH` with FTS5 bm25 ranking
- Title matches weighted higher than body matches
- Results displayed with `snippet()` highlighting

## Edge Cases

| Scenario | Handling |
|----------|----------|
| Broken link (target slug doesn't exist) | Render as dashed red link, click to create placeholder |
| Duplicate slug | Auto-append `-2`, `-3` suffix on save |
| Empty content | Allowed; shown as "draft" in list |
| Large graph (too many nodes) | Default limit to recent N nodes, allow filtering by tag/time |
| Database backup | SQLite single-file — copy to backup; add export button in UI |

## Testing Strategy

| Layer | Approach |
|-------|----------|
| Unit | Link regex extraction, slug generation, Markdown rendering |
| Integration | FastAPI TestClient: note CRUD, search, graph API |
| Frontend | Manual verification of editor, graph interaction (no frontend test framework) |

## Dependencies

### Python
- `fastapi` + `uvicorn` — web framework
- `jinja2` — template rendering
- `sqlalchemy` or `aiosqlite` — database access
- `jieba` — Chinese text tokenization for FTS
- `python-markdown` or `mistune` — server-side Markdown rendering

### Frontend (vendored or CDN)
- EasyMDE or Milkdown — Markdown editor component
- D3.js (d3-force) — knowledge graph layout
- Minimal custom JS — page transitions, search autocomplete

## Deployment

- Docker image (~100MB) with single volume mount for the SQLite file
- Or: `uvicorn main:app` behind nginx, with systemd for auto-restart
- No external database server needed — SQLite is self-contained
