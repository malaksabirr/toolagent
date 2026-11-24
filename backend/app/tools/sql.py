"""Exécution SQL en lecture seule sur une base SQLite de démonstration."""
from __future__ import annotations

import re
import sqlite3

from ..config import DB_PATH
from ..seed_db import ensure_db
from .base import Tool, ToolResult, obj, registry

_FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|alter|create|replace|attach|detach|pragma|vacuum|reindex)\b", re.I)


def _conn() -> sqlite3.Connection:
    ensure_db()
    return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)


def describe_database() -> ToolResult:
    con = _conn()
    try:
        out = []
        for (name,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
            cols = con.execute(f"PRAGMA table_info({name})").fetchall()
            n = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
            sample = con.execute(f"SELECT * FROM {name} LIMIT 2").fetchall()
            out.append(f"Table {name} ({n} lignes) : " + ", ".join(f"{c[1]} {c[2]}" for c in cols) + f"\n  exemples : {sample}")
    finally:
        con.close()
    out.append("Relations : commandes.client_id → clients.id ; commandes.produit_id → produits.id")
    return ToolResult("\n".join(out), summary="Schéma lu")


def run_sql(query: str, limit: int = 100) -> ToolResult:
    q = query.strip().rstrip(";").strip()
    if not re.match(r"^(select|with)\b", q, re.I) or ";" in q or _FORBIDDEN.search(q):
        return ToolResult("Requête refusée : seules les requêtes SELECT (une seule instruction) sont autorisées.", summary="Refusée")
    con = _conn()
    try:
        cur = con.execute(q)
        cols = [d[0] for d in cur.description or []]
        rows = cur.fetchmany(max(1, min(int(limit or 100), 200)))
    except sqlite3.Error as exc:
        return ToolResult(f"Erreur SQL : {exc}. Vérifie les noms de tables/colonnes avec describe_database et corrige la requête.",
                          summary="Erreur SQL")
    finally:
        con.close()
    shown = [[v if isinstance(v, (int, float)) or v is None else str(v) for v in r] for r in rows]
    text = f"{len(rows)} ligne(s). Colonnes : {', '.join(cols)}\n" + "\n".join(" | ".join(map(str, r)) for r in shown[:40])
    return ToolResult(text, ui=[{"type": "table", "title": "Résultat SQL", "sql": q, "columns": cols, "rows": shown[:100]}],
                      summary=f"{len(rows)} lignes")


registry.register(Tool(
    name="describe_database", label="Schéma SQL", ui_description="Voir les tables disponibles", icon="database",
    description="Décrit la base de données SQLite (tables clients, produits, commandes). À appeler AVANT d'écrire une requête SQL.",
    parameters=obj({}), func=describe_database, category="sql"))

registry.register(Tool(
    name="run_sql", label="Exécution SQL", ui_description="Interroger une base de données", icon="database",
    description="Exécute une requête SQL SELECT (SQLite, lecture seule) sur la base clients/produits/commandes. "
                "Utilise des JOIN, GROUP BY, ORDER BY. En cas d'erreur, corrige et réessaie.",
    parameters=obj({"query": {"type": "string", "description": "Requête SELECT SQLite"},
                    "limit": {"type": "integer", "description": "Max de lignes (défaut 100)"}}, ["query"]),
    func=run_sql, category="sql"))
