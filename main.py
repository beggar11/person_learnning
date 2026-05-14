from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from config import STATIC_DIR
from database import init_db

app = FastAPI(title="Knowledge Base")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.on_event("startup")
def startup():
    init_db()
