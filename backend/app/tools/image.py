"""Génération d'images : Pollinations (gratuit) ou DALL·E (OpenAI)."""
from __future__ import annotations

import base64
import random
import uuid
from urllib.parse import quote

import httpx

from ..config import GENERATED_DIR, settings
from .base import Tool, ToolResult, obj, registry


def generate_image(prompt: str, style: str = "", orientation: str = "landscape") -> ToolResult:
    full = f"{prompt}, {style}".strip(", ") if style else prompt
    w, h = {"portrait": (768, 1024), "square": (1024, 1024)}.get(orientation, (1024, 768))
    if settings.IMAGE_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        try:
            size = {"portrait": "1024x1536", "square": "1024x1024"}.get(orientation, "1536x1024")
            r = httpx.post("https://api.openai.com/v1/images/generations", timeout=120,
                           headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                           json={"model": "gpt-image-1", "prompt": full, "size": size, "n": 1})
            r.raise_for_status()
            b64 = r.json()["data"][0]["b64_json"]
            name = f"{uuid.uuid4().hex[:12]}.png"
            (GENERATED_DIR / name).write_bytes(base64.b64decode(b64))
            url = f"/generated/{name}"
        except Exception as exc:  # noqa: BLE001
            return ToolResult(f"Génération d'image échouée : {exc}", summary="Échec")
    else:
        url = f"https://image.pollinations.ai/prompt/{quote(full)}?width={w}&height={h}&nologo=true&seed={random.randint(1, 10**6)}"
    return ToolResult("Image générée et déjà affichée à l'utilisateur. Décris brièvement ce qu'elle représente "
                      "et propose des variantes (style, ambiance, cadrage). N'écris pas l'URL.",
                      ui=[{"type": "image", "url": url, "prompt": prompt}], summary="Image créée")


registry.register(Tool(
    name="generate_image", label="Génération d'images", ui_description="Créer des images avec l'IA", icon="image",
    description="Génère une image à partir d'une description. Écris TOUJOURS le prompt en anglais, détaillé "
                "(sujet, lumière, style, composition, ambiance), même si l'utilisateur écrit en français.",
    parameters=obj({"prompt": {"type": "string", "description": "Description détaillée en anglais"},
                    "style": {"type": "string", "description": "Ex: photorealistic, watercolor, 3D render, flat illustration"},
                    "orientation": {"type": "string", "enum": ["landscape", "portrait", "square"]}}, ["prompt"]),
    func=generate_image, category="creative"))
