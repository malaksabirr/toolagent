"""API FastAPI : santé, outils, upload, chat en streaming (SSE)."""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .agent import run_agent
from .config import GENERATED_DIR, ROOT, settings
from .seed_db import ensure_db
from .storage import save_upload
from .tools import registry

app = FastAPI(title="ToolAgent", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
                   allow_methods=["*"], allow_headers=["*"])
app.mount("/generated", StaticFiles(directory=GENERATED_DIR), name="generated")


@app.on_event("startup")
def _startup() -> None:
    ensure_db()


class ChatMessage(BaseModel):
    role: str
    content: str


class FileRef(BaseModel):
    id: str
    name: str
    kind: str = "other"


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    files: list[FileRef] = Field(default_factory=list)
    enabled_tools: list[str] | None = None
    temperature: float | None = Field(default=None, ge=0, le=1.5)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "configured": settings.configured, "model": settings.LLM_MODEL,
            "provider": settings.LLM_BASE_URL.split("//")[-1].split("/")[0], "tools": len(registry.all()),
            "temperature": settings.TEMPERATURE}


@app.get("/api/tools")
def tools() -> list[dict]:
    return [t.public() for t in registry.all()]


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)) -> dict:
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"Fichier trop volumineux (max {settings.MAX_UPLOAD_MB} Mo)")
    if not content:
        raise HTTPException(400, "Fichier vide")
    return save_upload(file.filename or "fichier", content)


@app.post("/api/chat")
async def chat(req: ChatRequest) -> StreamingResponse:
    async def gen():
        async for event in run_agent([m.model_dump() for m in req.messages], [f.model_dump() for f in req.files],
                                     req.enabled_tools, req.temperature):
            yield f"data: {json.dumps(event, ensure_ascii=False, default=str)}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# Mode production : sert le build React si présent (npm run build)
_dist = ROOT / "frontend" / "dist"
if _dist.exists():
    app.mount("/assets", StaticFiles(directory=_dist / "assets"), name="assets")

    @app.get("/{path:path}")
    def spa(path: str):
        f = _dist / path
        return FileResponse(f if f.is_file() else _dist / "index.html")
