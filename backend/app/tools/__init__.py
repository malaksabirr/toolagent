"""Importer ce paquet enregistre tous les outils dans `registry`."""
from . import data, docs, image, sql, utils, web  # noqa: F401
from .base import registry

# Ordre d'affichage dans l'interface
ORDER = ["web_search", "fetch_url", "analyze_dataset", "make_chart", "aggregate_dataset",
         "describe_database", "run_sql", "generate_image", "summarize_document",
         "calculator", "weather", "get_datetime"]
registry._tools = {k: registry._tools[k] for k in ORDER if k in registry._tools}

__all__ = ["registry"]
