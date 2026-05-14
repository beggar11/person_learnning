from fastapi import APIRouter, Request, Form, HTTPException, Depends
from database import get_db
from services.notes import create_note, get_note_by_id, get_all_notes, update_note, delete_note
from services.links import sync_links
from services.graph import get_graph_data

router = APIRouter(prefix="/api")


@router.post("/notes")
def api_save_note(
    request: Request,
    title: str = Form(...),
    content: str = Form(""),
    slug: str = Form(None),
    note_id: int = Form(None),
    tags: str = Form(""),
    db = Depends(get_db),
):
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
def api_list_notes(tag: str = None, db = Depends(get_db)):
    notes = get_all_notes(db, tag=tag)
    return {"notes": notes}


@router.get("/graph")
def api_graph(limit: int = 200, db = Depends(get_db)):
    return get_graph_data(db, limit=limit)


@router.post("/notes/{note_id}/delete")
def api_delete(note_id: int, db = Depends(get_db)):
    deleted = delete_note(db, note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"status": "ok"}
