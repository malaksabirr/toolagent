"""Socle commun des outils : définition, résultat, registre."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class ToolResult:
    """`content` est renvoyé au LLM ; `ui` (blocs riches) est envoyé à l'interface."""
    content: str
    ui: list[dict] = field(default_factory=list)
    summary: str = ""


@dataclass
class Tool:
    name: str
    label: str            # libellé affiché dans l'UI
    description: str      # description pour le LLM
    ui_description: str   # sous-titre court affiché dans la sidebar
    icon: str             # clé d'icône côté React
    parameters: dict      # JSON Schema
    func: Callable[..., ToolResult]
    category: str = "core"

    def spec(self) -> dict:
        return {"type": "function", "function": {
            "name": self.name, "description": self.description, "parameters": self.parameters}}

    def public(self) -> dict:
        props = self.parameters.get("properties", {})
        return {"name": self.name, "label": self.label, "description": self.ui_description,
                "long_description": self.description, "icon": self.icon,
                "category": self.category, "params": list(props.keys())}


class Registry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> Tool:
        self._tools[tool.name] = tool
        return tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def all(self) -> list[Tool]:
        return list(self._tools.values())

    def specs(self, enabled: list[str] | None = None) -> list[dict]:
        return [t.spec() for t in self._tools.values() if enabled is None or t.name in enabled]


registry = Registry()


def obj(properties: dict[str, Any], required: list[str] | None = None) -> dict:
    return {"type": "object", "properties": properties, "required": required or []}
