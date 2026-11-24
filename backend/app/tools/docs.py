"""Lecture et résumé de documents (PDF, DOCX, TXT, MD)."""
from __future__ import annotations

from pathlib import Path

from ..storage import get_path
from .base import Tool, ToolResult, obj, registry

MAX_CHARS = 14000


def extract_text(path: Path) -> tuple[str, int | None]:
    ext = path.suffix.lower()
    if ext == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        return "\n\n".join((p.extract_text() or "") for p in reader.pages), len(reader.pages)
    if ext == ".docx":
        from docx import Document
        doc = Document(str(path))
        parts = [p.text for p in doc.paragraphs if p.text.strip()]
        for t in doc.tables:
            for row in t.rows:
                parts.append(" | ".join(c.text.strip() for c in row.cells))
        return "\n".join(parts), None
    for enc in ("utf-8", "latin-1"):
        try:
            return path.read_text(encoding=enc), None
        except UnicodeDecodeError:
            continue
    raise ValueError("Format non pris en charge")


def _sample(text: str, limit: int = MAX_CHARS) -> str:
    """Pour les longs documents : début + milieu + fin afin de couvrir tout le contenu."""
    if len(text) <= limit:
        return text
    part = limit // 3
    mid = len(text) // 2
    return (text[:part] + "\n\n[… passage omitted …]\n\n" + text[mid - part // 2: mid + part // 2]
            + "\n\n[… passage omitted …]\n\n" + text[-part:])


def summarize_document(file_id: str, focus: str = "") -> ToolResult:
    try:
        path = get_path(file_id)
        text, pages = extract_text(path)
    except Exception as exc:  # noqa: BLE001
        return ToolResult(f"Lecture du document impossible : {exc}", summary="Échec")
    text = " ".join(text.split()) if len(text) < 200 else text.strip()
    if not text:
        return ToolResult("Le document ne contient pas de texte extractible (PDF scanné ?).", summary="Vide")
    words = len(text.split())
    head = f"Document : {path.name.split('__', 1)[-1]} | {words} mots" + (f" | {pages} pages" if pages else "")
    note = " (document long : extraits du début, du milieu et de la fin)" if len(text) > MAX_CHARS else ""
    task = f"\nFocus demandé : {focus}" if focus else ""
    return ToolResult(f"{head}{note}{task}\n\n{_sample(text)}\n\nRédige maintenant un résumé structuré : "
                      "idée centrale, points clés, chiffres/dates importants, conclusion.",
                      ui=[{"type": "doc", "name": path.name.split("__", 1)[-1], "words": words, "pages": pages}],
                      summary=f"{words} mots")


registry.register(Tool(
    name="summarize_document", label="Résumé de documents", ui_description="Synthétiser un document", icon="file",
    description="Lit un document joint (PDF, DOCX, TXT, MD) et fournit son contenu pour le résumer ou répondre à des questions dessus.",
    parameters=obj({"file_id": {"type": "string"}, "focus": {"type": "string", "description": "Aspect précis à résumer (optionnel)"}},
                   ["file_id"]),
    func=summarize_document, category="docs"))
