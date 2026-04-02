import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes import audits, auth, dashboard, events, records, users
from app.core.config import settings
from app.db_migrations import run_migrations
from app.models import audit_log, domain_event, financial_record, user  # noqa: F401

app = FastAPI(title=settings.app_name, version="1.0.0")
FRONTEND_DIR = PROJECT_ROOT / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")


@app.on_event("startup")
def on_startup() -> None:
    if settings.auto_run_migrations:
        run_migrations()


@app.exception_handler(SQLAlchemyError)
async def handle_db_error(_, exc: SQLAlchemyError):
    return JSONResponse(status_code=500, content={"detail": "Database operation failed", "error": str(exc)})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def landing():
    if FRONTEND_DIR.exists():
        return FileResponse(str(FRONTEND_DIR / "index.html"))
    return JSONResponse(status_code=404, content={"detail": "Frontend not found"})


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(records.router)
app.include_router(dashboard.router)
app.include_router(audits.router)
app.include_router(events.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=settings.app_port, reload=True)
