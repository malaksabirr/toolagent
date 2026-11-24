"""Tests unitaires des outils (sans réseau ni LLM) : `pytest backend/tests`."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.storage import save_upload  # noqa: E402
from app.tools import registry  # noqa: E402
from app.tools.utils import calculator  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def test_registry_has_all_required_tools():
    names = {t.name for t in registry.all()}
    assert {"web_search", "analyze_dataset", "run_sql", "generate_image", "summarize_document"} <= names


def test_calculator_safe():
    assert "= 14" in calculator("2*(3+4)").content
    assert "Erreur" in calculator("__import__('os').system('ls')").content


def test_sql_readonly():
    ok = registry.get("run_sql").func("SELECT COUNT(*) AS n FROM clients")
    assert "1 ligne" in ok.content
    bad = registry.get("run_sql").func("DROP TABLE clients")
    assert "refusée" in bad.content


def test_analyze_dataset_builds_charts():
    meta = save_upload("ventes.csv", (ROOT / "samples" / "ventes.csv").read_bytes())
    res = registry.get("analyze_dataset").func(meta["id"])
    kinds = [b.get("kind") for b in res.ui if b["type"] == "chart"]
    assert kinds == ["line", "donut", "bar"]
    agg = registry.get("aggregate_dataset").func(meta["id"], "région", "ventes")
    assert "Casablanca" in agg.content


def test_summarize_document():
    meta = save_upload("note.txt", (ROOT / "samples" / "note_projet.txt").read_bytes())
    res = registry.get("summarize_document").func(meta["id"])
    assert "ToolAgent" in res.content
