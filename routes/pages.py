from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from database import get_db
from services.notes import get_note_by_slug, get_all_notes, get_note_tags, render_markdown
from services.links import get_backlinks
from services.search import search_notes

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
def page_index(request: Request, tag: str = None, db = Depends(get_db)):
    notes = get_all_notes(db, tag=tag)
    tags = db.execute("SELECT * FROM tags ORDER BY name").fetchall()
    return render("index.html", notes=notes, tags=[dict(t) for t in tags], current_tag=tag)

@router.get("/note/new", response_class=HTMLResponse)
def page_new_note(request: Request):
    return render("note_edit.html", note=None)

@router.get("/note/{slug}", response_class=HTMLResponse)
def page_note_detail(request: Request, slug: str, db = Depends(get_db)):
    note = get_note_by_slug(db, slug)
    if note is None:
        return HTMLResponse("<h1>404 - Not Found</h1>", status_code=404)
    backlinks = get_backlinks(db, note["id"])
    note["html_content"] = render_markdown(note["content"])
    return render("note_detail.html", note=note, backlinks=backlinks)

@router.get("/note/{slug}/edit", response_class=HTMLResponse)
def page_note_edit(request: Request, slug: str, db = Depends(get_db)):
    note = get_note_by_slug(db, slug)
    if note is None:
        return HTMLResponse("<h1>404 - Not Found</h1>", status_code=404)
    tags = get_note_tags(db, note["id"])
    note_tags = ",".join(t["name"] for t in tags)
    return render("note_edit.html", note=note, note_tags=note_tags)

@router.get("/search", response_class=HTMLResponse)
def page_search(request: Request, q: str = "", db = Depends(get_db)):
    results = search_notes(db, q) if q.strip() else []
    return render("search_results.html", query=q, results=results)

@router.get("/graph", response_class=HTMLResponse)
def page_graph(request: Request):
    return render("graph.html")

@router.get("/tag/{slug}", response_class=HTMLResponse)
def page_tag(request: Request, slug: str, db = Depends(get_db)):
    notes = get_all_notes(db, tag=slug)
    tag_name = db.execute("SELECT name FROM tags WHERE slug = ?", (slug,)).fetchone()
    tag_name = tag_name["name"] if tag_name else slug
    tags = db.execute("SELECT * FROM tags ORDER BY name").fetchall()
    return render("index.html", notes=notes, tags=[dict(t) for t in tags], current_tag=slug, tag_name=tag_name)
