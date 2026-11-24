"""Stockage des fichiers téléversés."""
from __future__ import annotations

import re
import uuid
from pathlib import Path

from .config import UPLOAD_DIR

KIND_BY_EXT = {
    ".csv": "data", ".tsv": "data", ".xlsx": "data", ".xls": "data", ".json": "data",
    ".pdf": "document", ".docx": "document", ".txt": "document", ".md": "document",
}


def kind_of(name: str) -> str:
    return KIND_BY_EXT.get(Path(name).suffix.lower(), "other")


def save_upload(filename: str, content: bytes) -> dict:
    safe = re.sub(r"[^\w.\-]+", "_", filename)[:80] or "fichier"
    file_id = uuid.uuid4().hex[:10]
    (UPLOAD_DIR / f"{file_id}__{safe}").write_bytes(content)
    return {"id": file_id, "name": filename, "size": len(content), "kind": kind_of(filename)}


def get_path(file_id: str) -> Path:
    if not re.fullmatch(r"[0-9a-f]{10}", file_id or ""):
        raise FileNotFoundError(f"Identifiant de fichier invalide : {file_id!r}. Utilise l'id exact indiqué dans la liste des fichiers.")
    matches = list(UPLOAD_DIR.glob(f"{file_id}__*"))
    if not matches:
        raise FileNotFoundError(f"Fichier {file_id} introuvable. Demande à l'utilisateur de le téléverser à nouveau.")
    return matches[0]
