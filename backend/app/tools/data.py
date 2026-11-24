"""Analyse de fichiers tabulaires (CSV / Excel / JSON) avec pandas."""
from __future__ import annotations

import csv
import re
import unicodedata
from functools import lru_cache

import pandas as pd

from ..storage import get_path
from .base import Tool, ToolResult, obj, registry

MEASURE_HINTS = ("vente", "montant", "revenu", "revenue", "total", "prix", "price", "sales", "amount", "chiffre", "ca")
GEO_HINTS = ("region", "région", "ville", "city", "pays", "country")


def _is_text(series: pd.Series) -> bool:
    return series.dtype == object or pd.api.types.is_string_dtype(series)


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "", s)


@lru_cache(maxsize=8)
def _load(path_str: str, mtime: float) -> pd.DataFrame:
    path_str_l = path_str.lower()
    if path_str_l.endswith((".xlsx", ".xls")):
        return pd.read_excel(path_str)
    if path_str_l.endswith(".json"):
        return pd.read_json(path_str)
    for enc in ("utf-8-sig", "latin-1"):
        try:
            with open(path_str, encoding=enc, newline="") as f:
                sample = f.read(8192)
            try:
                sep = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
            except csv.Error:
                sep = ","
            return pd.read_csv(path_str, sep=sep, encoding=enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("Encodage du fichier non reconnu")


def load_df(file_id: str) -> pd.DataFrame:
    p = get_path(file_id)
    return _load(str(p), p.stat().st_mtime).copy()


def resolve_col(df: pd.DataFrame, name: str | None) -> str | None:
    if not name:
        return None
    if name in df.columns:
        return name
    target = _norm(name)
    for c in df.columns:
        if _norm(c) == target:
            return c
    for c in df.columns:
        if target and target in _norm(c):
            return c
    raise KeyError(f"Colonne « {name} » introuvable. Colonnes disponibles : {', '.join(map(str, df.columns))}")


def detect_date_col(df: pd.DataFrame) -> str | None:
    for c in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[c]):
            return c
    for c in df.columns:
        if _is_text(df[c]):
            sample = df[c].dropna().head(200)
            if len(sample) and pd.to_datetime(sample, errors="coerce").notna().mean() > 0.9 and not sample.astype(str).str.fullmatch(r"\d+").any():
                return c
    return None


def detect_measure(df: pd.DataFrame) -> str | None:
    nums = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and not _norm(c).endswith("id")]
    for hint in MEASURE_HINTS:
        for c in nums:
            if hint in _norm(c):
                return c
    return nums[0] if nums else None


def detect_categories(df: pd.DataFrame, date_col: str | None) -> list[str]:
    cats = [c for c in df.columns if c != date_col and (_is_text(df[c]) or str(df[c].dtype) == "category")
            and 1 < df[c].nunique() <= 30]
    cats.sort(key=lambda c: (0 if any(h in _norm(c) for h in GEO_HINTS) else 1, df[c].nunique()))
    return cats


def _to_dt(df: pd.DataFrame, col: str) -> pd.Series:
    return pd.to_datetime(df[col], errors="coerce")


def _series_by_time(df: pd.DataFrame, date_col: str, measure: str | None, agg: str, freq: str | None = None) -> list[dict]:
    d = _to_dt(df, date_col)
    span = (d.max() - d.min()).days if d.notna().any() else 0
    freq = freq or ("M" if span > 60 else "D")
    period = d.dt.to_period({"D": "D", "W": "W", "M": "M", "Y": "Y", "Q": "Q"}.get(freq, "M"))
    grouped = df.groupby(period)[measure].agg(agg) if measure else df.groupby(period).size()
    return [{"name": str(k), "value": round(float(v), 2)} for k, v in grouped.items()][-60:]


def _by_category(df: pd.DataFrame, cat: str, measure: str | None, agg: str, top_n: int, other: bool = False) -> list[dict]:
    grouped = df.groupby(cat)[measure].agg(agg) if measure else df.groupby(cat).size()
    grouped = grouped.sort_values(ascending=False)
    items = [{"name": str(k), "value": round(float(v), 2)} for k, v in grouped.head(top_n).items()]
    if other and len(grouped) > top_n:
        items.append({"name": "Autres", "value": round(float(grouped.iloc[top_n:].sum()), 2)})
    return items


def analyze_dataset(file_id: str) -> ToolResult:
    try:
        df = load_df(file_id)
    except Exception as exc:  # noqa: BLE001
        return ToolResult(f"Lecture impossible : {exc}", summary="Échec")
    rows, cols = df.shape
    date_col = detect_date_col(df)
    measure = detect_measure(df)
    cats = detect_categories(df, date_col)

    lines = [f"Lignes : {rows} | Colonnes : {cols}", "Colonnes (type, manquants) :"]
    for c in df.columns:
        lines.append(f"- {c} ({df[c].dtype}, {int(df[c].isna().sum())} manquants, {df[c].nunique()} valeurs uniques)")
    num = df.select_dtypes("number")
    if not num.empty:
        lines.append("\nStatistiques numériques :\n" + num.describe().round(2).to_string())
    for c in cats[:3]:
        lines.append(f"\nTop valeurs « {c} » : " + ", ".join(f"{k} ({v})" for k, v in df[c].value_counts().head(6).items()))
    if date_col:
        d = _to_dt(df, date_col)
        lines.append(f"\nPériode : {d.min().date()} → {d.max().date()} (colonne {date_col})")
    lines.append("\nAperçu (5 premières lignes) :\n" + df.head(5).to_string(index=False))

    ui: list[dict] = [{"type": "dataset", "rows": rows, "columns": [str(c) for c in df.columns]}]
    charts: list[dict] = []
    unit = ""
    if date_col and measure:
        s = _series_by_time(df, date_col, measure, "sum")
        charts.append({"type": "chart", "kind": "line", "title": "Évolution des ventes" if "vente" in _norm(measure) else f"Évolution : {measure}",
                       "data": s, "unit": unit})
        top = s and max(s, key=lambda x: x["value"])
        lines.append(f"\nTendance : {s[0]['name']}={s[0]['value']} → {s[-1]['name']}={s[-1]['value']} ; pic {top['name']}={top['value']}.")
    if cats:
        non_geo = [c for c in cats if not any(h in _norm(c) for h in GEO_HINTS)]
        first = non_geo[0] if non_geo else cats[0]
        charts.append({"type": "chart", "kind": "donut", "title": f"Répartition par {first}",
                       "data": _by_category(df, first, measure, "sum", 5, other=True), "unit": ""})
        geo = next((c for c in cats if c != first), None)
        if geo:
            charts.append({"type": "chart", "kind": "bar", "title": f"Top 3 · {geo}",
                           "data": _by_category(df, geo, measure, "sum", 3), "unit": ""})
    ui.extend(charts)
    if charts:
        lines.append(f"\n{len(charts)} graphiques ont été affichés automatiquement à l'utilisateur (mesure = {measure}). "
                     "Ne répète pas toutes les valeurs : commente les tendances et les points saillants.")
    return ToolResult("\n".join(lines), ui=ui, summary=f"{rows} lignes · {cols} colonnes")


def make_chart(file_id: str, kind: str, x: str, y: str | None = None, agg: str = "sum", top_n: int = 10,
               freq: str | None = None, title: str | None = None) -> ToolResult:
    try:
        df = load_df(file_id)
        xc, yc = resolve_col(df, x), resolve_col(df, y)
        agg = agg if agg in ("sum", "mean", "count", "max", "min", "median") else "sum"
        if yc is None or agg == "count":
            yc, agg = None, "count"
        date_col = detect_date_col(df)
        if xc == date_col or kind == "line":
            data = _series_by_time(df, xc, yc, "count" if agg == "count" else agg, freq)
            kind = "line" if kind not in ("bar",) else "bar"
        else:
            data = _by_category(df, xc, yc, "count" if agg == "count" else agg, int(top_n or 10), other=(kind in ("pie", "donut")))
        kind = "donut" if kind == "pie" else (kind if kind in ("line", "bar", "donut") else "bar")
    except Exception as exc:  # noqa: BLE001
        return ToolResult(f"Graphique impossible : {exc}", summary="Échec")
    ttl = title or f"{agg} de {yc or 'lignes'} par {xc}"
    text = "Données du graphique :\n" + "\n".join(f"- {d['name']}: {d['value']}" for d in data[:30])
    return ToolResult(text, ui=[{"type": "chart", "kind": kind, "title": ttl, "data": data, "unit": ""}], summary=ttl[:60])


def aggregate_dataset(file_id: str, group_by: str, metric: str | None = None, agg: str = "sum",
                      top_n: int = 15, sort_desc: bool = True) -> ToolResult:
    try:
        df = load_df(file_id)
        g, m = resolve_col(df, group_by), resolve_col(df, metric)
        agg = agg if agg in ("sum", "mean", "count", "max", "min", "median") else "sum"
        res = (df.groupby(g)[m].agg(agg) if m and agg != "count" else df.groupby(g).size()).sort_values(ascending=not sort_desc)
    except Exception as exc:  # noqa: BLE001
        return ToolResult(f"Agrégation impossible : {exc}", summary="Échec")
    res = res.head(int(top_n or 15))
    rows = [[str(k), round(float(v), 2)] for k, v in res.items()]
    label = f"{agg}({m})" if m and agg != "count" else "nombre"
    text = f"{label} par {g} :\n" + "\n".join(f"- {r[0]} : {r[1]}" for r in rows)
    return ToolResult(text, ui=[{"type": "table", "title": f"{label} par {g}", "columns": [g, label], "rows": rows}],
                      summary=f"{len(rows)} groupes")


FILE_ID = {"type": "string", "description": "Identifiant du fichier (voir la liste des fichiers joints)"}

registry.register(Tool(
    name="analyze_dataset", label="Analyse de données", ui_description="Lire & analyser des fichiers", icon="chart",
    description="Analyse complète d'un fichier CSV/Excel/JSON : dimensions, colonnes, statistiques, valeurs manquantes, "
                "et génère automatiquement les graphiques principaux (évolution, répartition, classement). "
                "À appeler en premier quand l'utilisateur joint un fichier de données.",
    parameters=obj({"file_id": FILE_ID}, ["file_id"]), func=analyze_dataset, category="data"))

registry.register(Tool(
    name="make_chart", label="Graphique", ui_description="Créer un graphique sur mesure", icon="chart",
    description="Crée un graphique personnalisé (line, bar, donut) à partir d'un fichier de données : "
                "x = colonne de regroupement ou de date, y = colonne numérique, agg = sum|mean|count|max|min|median.",
    parameters=obj({"file_id": FILE_ID, "kind": {"type": "string", "enum": ["line", "bar", "donut"]},
                    "x": {"type": "string"}, "y": {"type": "string"},
                    "agg": {"type": "string", "enum": ["sum", "mean", "count", "max", "min", "median"]},
                    "top_n": {"type": "integer"}, "freq": {"type": "string", "enum": ["D", "W", "M", "Q", "Y"]},
                    "title": {"type": "string"}}, ["file_id", "kind", "x"]),
    func=make_chart, category="data"))

registry.register(Tool(
    name="aggregate_dataset", label="Agrégation", ui_description="Totaux, moyennes, classements", icon="chart",
    description="Calcule un tableau agrégé (somme, moyenne, nombre...) d'une métrique par groupe sur un fichier de données. "
                "À utiliser pour répondre précisément à des questions chiffrées sur le fichier.",
    parameters=obj({"file_id": FILE_ID, "group_by": {"type": "string"}, "metric": {"type": "string"},
                    "agg": {"type": "string", "enum": ["sum", "mean", "count", "max", "min", "median"]},
                    "top_n": {"type": "integer"}, "sort_desc": {"type": "boolean"}}, ["file_id", "group_by"]),
    func=aggregate_dataset, category="data"))
