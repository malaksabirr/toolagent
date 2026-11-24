"""Outils web : recherche (DuckDuckGo) et lecture d'une page."""
from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from .base import Tool, ToolResult, obj, registry

try:  # le paquet a été renommé duckduckgo_search -> ddgs
    from ddgs import DDGS
except ImportError:  # pragma: no cover
    from duckduckgo_search import DDGS  # type: ignore


def web_search(query: str, max_results: int = 6, recent: bool = False) -> ToolResult:
    max_results = max(1, min(int(max_results or 6), 10))
    try:
        with DDGS() as d:
            kwargs = {"max_results": max_results}
            if recent:
                kwargs["timelimit"] = "m"
            raw = list(d.text(query, **kwargs))
    except Exception as exc:  # noqa: BLE001
        return ToolResult(f"La recherche web a échoué ({exc}). Réponds avec tes connaissances en précisant que tu n'as pas pu vérifier en ligne.",
                          summary="Échec")
    items = [{"title": r.get("title", ""), "url": r.get("href") or r.get("url", ""), "snippet": r.get("body", "")} for r in raw]
    if not items:
        return ToolResult("Aucun résultat. Essaie une requête différente (autre langue, mots-clés plus simples).", summary="0 résultat")
    text = "\n\n".join(f"[{i + 1}] {it['title']}\nURL: {it['url']}\n{it['snippet']}" for i, it in enumerate(items))
    return ToolResult(text, ui=[{"type": "sources", "query": query, "items": items}], summary=f"{len(items)} sources")


def _is_public(url: str) -> bool:
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.hostname:
        return False
    try:
        for info in socket.getaddrinfo(p.hostname, None):
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return False
    except OSError:
        return False
    return True


def fetch_url(url: str, max_chars: int = 7000) -> ToolResult:
    if not _is_public(url):
        return ToolResult("URL refusée (non publique ou invalide).", summary="Refusée")
    try:
        r = httpx.get(url, timeout=15, follow_redirects=True,
                      headers={"User-Agent": "Mozilla/5.0 (ToolAgent student project)"})
        r.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        return ToolResult(f"Impossible de lire la page : {exc}", summary="Échec")
    soup = BeautifulSoup(r.text, "html.parser")
    for t in soup(["script", "style", "nav", "footer", "header", "aside", "form", "noscript"]):
        t.decompose()
    title = soup.title.get_text(strip=True) if soup.title else url
    text = " ".join(soup.get_text(" ", strip=True).split())
    max_chars = max(1000, min(int(max_chars or 7000), 15000))
    cut = len(text) > max_chars
    return ToolResult(f"Titre : {title}\nURL : {url}\n\n{text[:max_chars]}{' […tronqué]' if cut else ''}",
                      summary=title[:60])


registry.register(Tool(
    name="web_search", label="Recherche Web", ui_description="Obtenir des infos récentes", icon="search",
    description="Recherche sur le web. À UTILISER pour toute information récente ou susceptible d'avoir changé "
                "(actualités, prix, personnes, versions, événements, scores) ou que tu ne connais pas avec certitude. "
                "Fais des requêtes courtes et précises ; relance avec d'autres mots-clés si nécessaire.",
    parameters=obj({"query": {"type": "string", "description": "Requête de recherche"},
                    "max_results": {"type": "integer", "description": "1 à 10 (défaut 6)"},
                    "recent": {"type": "boolean", "description": "true pour limiter au dernier mois"}}, ["query"]),
    func=web_search, category="web"))

registry.register(Tool(
    name="fetch_url", label="Lecture de page", ui_description="Lire le contenu d'une URL", icon="globe",
    description="Télécharge et lit le texte d'une page web (après une recherche, ou si l'utilisateur donne une URL).",
    parameters=obj({"url": {"type": "string"}, "max_chars": {"type": "integer"}}, ["url"]),
    func=fetch_url, category="web"))
