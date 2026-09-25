from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import init_db
from app.product_routes import router as product_router
from app.routes import router as local_router
from app.seed import seed_database

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="MACCY-CREATIONS Career Hub", version="1.2.0")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.include_router(local_router)
app.include_router(product_router)


@app.on_event("startup")
def startup():
    init_db()
    seed_database()


@app.get("/", include_in_schema=False)
def landing():
    from fastapi.responses import HTMLResponse
    return HTMLResponse((BASE_DIR / "templates" / "index.html").read_text())


@app.get("/dashboard", include_in_schema=False)
def dashboard():
    from fastapi.responses import HTMLResponse
    return HTMLResponse((BASE_DIR / "templates" / "dashboard.html").read_text())


@app.get("/health")
def health():
    return {"status": "ok", "project": "MACCY-CREATIONS", "offline_database": "ready", "product_routes": "ready"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
