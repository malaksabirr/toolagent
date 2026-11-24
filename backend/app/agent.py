"""Boucle d'agent : LLM (streaming) ↔ outils, jusqu'à la réponse finale."""
from __future__ import annotations

import asyncio
import json
import time
import uuid
from typing import Any, AsyncIterator

from openai import AsyncOpenAI, APIError

from .config import settings
from .prompts import build_system_prompt
from .tools import registry

MAX_TOOL_CHARS = 12000
HISTORY_LIMIT = 24


def _client() -> AsyncOpenAI:
    return AsyncOpenAI(base_url=settings.LLM_BASE_URL, api_key=settings.LLM_API_KEY or "none", timeout=90)


def _friendly_error(exc: Exception) -> str:
    msg = str(exc)
    low = msg.lower()
    if "401" in msg or "invalid api key" in low or "authentication" in low:
        return "Clé API invalide ou manquante. Vérifie LLM_API_KEY dans le fichier .env puis relance le backend."
    if "429" in msg or "rate limit" in low:
        return "Limite de requêtes atteinte chez le fournisseur LLM. Patiente quelques secondes puis réessaie."
    if "connect" in low:
        return f"Impossible de joindre le fournisseur LLM ({settings.LLM_BASE_URL}). Vérifie ta connexion / ton URL."
    return f"Erreur du modèle : {msg[:300]}"


async def _run_tool(name: str, raw_args: str) -> tuple[dict, Any]:
    tool = registry.get(name)
    if tool is None:
        return {"ok": False, "summary": "Outil inconnu"}, f"Outil inconnu : {name}"
    try:
        args = json.loads(raw_args) if raw_args.strip() else {}
        if not isinstance(args, dict):
            raise ValueError("arguments non valides")
    except Exception:  # noqa: BLE001
        return {"ok": False, "summary": "Arguments invalides"}, "Arguments JSON invalides, réessaie avec un JSON correct."
    try:
        result = await asyncio.to_thread(tool.func, **args)
    except TypeError as exc:
        return {"ok": False, "summary": "Paramètres invalides"}, f"Paramètres invalides pour {name} : {exc}"
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "summary": "Erreur"}, f"Erreur d'exécution de {name} : {exc}"
    return {"ok": True, "summary": result.summary}, result


async def run_agent(messages: list[dict], files: list[dict], enabled_tools: list[str] | None = None,
                    temperature: float | None = None) -> AsyncIterator[dict]:
    if not settings.configured:
        yield {"type": "error", "message": "Aucune clé API configurée. Copie .env.example vers .env, renseigne LLM_API_KEY, puis relance le backend."}
        yield {"type": "done"}
        return

    client = _client()
    convo: list[dict] = [{"role": "system", "content": build_system_prompt(files)}]
    convo += [{"role": m["role"], "content": m["content"]} for m in messages[-HISTORY_LIMIT:] if m.get("content")]
    specs = registry.specs(enabled_tools)
    temp = settings.TEMPERATURE if temperature is None else temperature
    retried = False
    step = 0

    while step < settings.MAX_STEPS:
        step += 1
        kwargs: dict[str, Any] = dict(model=settings.LLM_MODEL, messages=convo, temperature=temp, stream=True)
        if specs:
            kwargs["tools"] = specs
            kwargs["tool_choice"] = "auto"
        content = ""
        calls: dict[int, dict] = {}
        try:
            stream = await client.chat.completions.create(**kwargs)
            async for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                if delta.content:
                    content += delta.content
                    yield {"type": "token", "text": delta.content}
                for tc in delta.tool_calls or []:
                    slot = calls.setdefault(tc.index, {"id": "", "name": "", "args": ""})
                    if tc.id:
                        slot["id"] = tc.id
                    if tc.function:
                        if tc.function.name:
                            slot["name"] += tc.function.name
                        if tc.function.arguments:
                            slot["args"] += tc.function.arguments
        except APIError as exc:
            if not retried and not content and ("tool" in str(exc).lower() or "generate" in str(exc).lower()):
                retried = True
                step -= 1
                continue
            yield {"type": "error", "message": _friendly_error(exc)}
            break
        except Exception as exc:  # noqa: BLE001
            yield {"type": "error", "message": _friendly_error(exc)}
            break

        if not calls:
            break

        ordered = [calls[i] for i in sorted(calls)]
        for c in ordered:
            c["id"] = c["id"] or f"call_{uuid.uuid4().hex[:8]}"
        convo.append({"role": "assistant", "content": content or None, "tool_calls": [
            {"id": c["id"], "type": "function", "function": {"name": c["name"], "arguments": c["args"] or "{}"}} for c in ordered]})

        for c in ordered:
            tool = registry.get(c["name"])
            try:
                shown_args = json.loads(c["args"] or "{}")
            except Exception:  # noqa: BLE001
                shown_args = {}
            yield {"type": "tool_start", "id": c["id"], "name": c["name"],
                   "label": tool.label if tool else c["name"], "icon": tool.icon if tool else "tool", "args": shown_args}
            t0 = time.perf_counter()
            meta, res = await _run_tool(c["name"], c["args"])
            ms = int((time.perf_counter() - t0) * 1000)
            text = res if isinstance(res, str) else res.content
            yield {"type": "tool_result", "id": c["id"], "name": c["name"], "ok": meta["ok"],
                   "summary": meta["summary"], "ms": ms}
            if not isinstance(res, str):
                for block in res.ui:
                    yield {"type": "block", "block": block}
            convo.append({"role": "tool", "tool_call_id": c["id"], "content": text[:MAX_TOOL_CHARS]})
    else:
        yield {"type": "error", "message": "Nombre maximal d'étapes atteint. Reformule ou découpe ta demande."}

    yield {"type": "done"}
