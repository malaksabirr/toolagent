"""Outils utilitaires : calculatrice sécurisée, date/heure, météo."""
from __future__ import annotations

import ast
import math
import operator as op
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx

from .base import Tool, ToolResult, obj, registry

_OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
        ast.Pow: op.pow, ast.Mod: op.mod, ast.FloorDiv: op.floordiv,
        ast.USub: op.neg, ast.UAdd: op.pos}
_FUNCS = {n: getattr(math, n) for n in (
    "sqrt", "sin", "cos", "tan", "asin", "acos", "atan", "log", "log10", "log2", "exp",
    "floor", "ceil", "factorial", "radians", "degrees", "gcd")}
_FUNCS.update({"abs": abs, "round": round, "min": min, "max": max, "sum": sum})
_CONSTS = {"pi": math.pi, "e": math.e, "tau": math.tau}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 1000:
            raise ValueError("Exposant trop grand")
        return _OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.Name) and node.id in _CONSTS:
        return _CONSTS[node.id]
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCS:
        return _FUNCS[node.func.id](*[_eval(a) for a in node.args])
    if isinstance(node, (ast.List, ast.Tuple)):
        return [_eval(e) for e in node.elts]
    raise ValueError("Expression non autorisée")


def safe_calc(expression: str) -> float | int:
    expr = expression.replace("^", "**").replace(",", ".") if "(" not in expression else expression.replace("^", "**")
    return _eval(ast.parse(expr.strip(), mode="eval").body)


def calculator(expression: str) -> ToolResult:
    try:
        value = safe_calc(expression)
    except Exception as exc:  # noqa: BLE001
        return ToolResult(f"Erreur de calcul : {exc}. Reformule l'expression (ex: 12*(3+4)/5).", summary="Erreur")
    return ToolResult(f"{expression} = {value}", summary=f"= {value}")


def get_datetime(timezone: str = "Africa/Casablanca") -> ToolResult:
    try:
        now = datetime.now(ZoneInfo(timezone))
    except Exception:  # noqa: BLE001
        return ToolResult(f"Fuseau horaire inconnu : {timezone}. Utilise un nom IANA (ex: Europe/Paris).")
    txt = now.strftime("%A %d %B %Y, %H:%M:%S") + f" ({timezone})"
    return ToolResult(txt, summary=now.strftime("%d/%m/%Y %H:%M"))


_WMO = {0: "ciel dégagé", 1: "plutôt dégagé", 2: "partiellement nuageux", 3: "couvert", 45: "brouillard",
        48: "brouillard givrant", 51: "bruine légère", 53: "bruine", 55: "bruine forte", 61: "pluie légère",
        63: "pluie", 65: "pluie forte", 71: "neige légère", 73: "neige", 75: "neige forte",
        80: "averses", 81: "averses fortes", 82: "averses violentes", 95: "orage", 96: "orage avec grêle", 99: "orage violent"}


def weather(city: str) -> ToolResult:
    try:
        with httpx.Client(timeout=12) as c:
            geo = c.get("https://geocoding-api.open-meteo.com/v1/search",
                        params={"name": city, "count": 1, "language": "fr"}).json()
            if not geo.get("results"):
                return ToolResult(f"Ville introuvable : {city}.", summary="Introuvable")
            g = geo["results"][0]
            w = c.get("https://api.open-meteo.com/v1/forecast", params={
                "latitude": g["latitude"], "longitude": g["longitude"], "timezone": "auto", "forecast_days": 4,
                "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code"}).json()
    except Exception as exc:  # noqa: BLE001
        return ToolResult(f"Service météo indisponible : {exc}", summary="Indisponible")
    cur, d = w["current"], w["daily"]
    lines = [f"Météo à {g['name']} ({g.get('country', '')}) :",
             f"- Maintenant : {cur['temperature_2m']}°C (ressenti {cur['apparent_temperature']}°C), "
             f"{_WMO.get(cur['weather_code'], 'variable')}, humidité {cur['relative_humidity_2m']}%, vent {cur['wind_speed_10m']} km/h",
             "Prévisions :"]
    for i, day in enumerate(d["time"]):
        lines.append(f"- {day} : {d['temperature_2m_min'][i]}°C → {d['temperature_2m_max'][i]}°C, "
                     f"{_WMO.get(d['weather_code'][i], 'variable')}, pluie {d['precipitation_sum'][i]} mm")
    return ToolResult("\n".join(lines), summary=f"{g['name']} : {cur['temperature_2m']}°C")


registry.register(Tool(
    name="calculator", label="Calculatrice", ui_description="Calculs exacts et fiables", icon="calculator",
    description="Évalue une expression mathématique avec précision (+ - * / ** %, sqrt, log, sin, pi...). "
                "À UTILISER pour tout calcul non trivial au lieu de calculer de tête.",
    parameters=obj({"expression": {"type": "string", "description": "Ex: '(1250*0.2)+sqrt(144)'"}}, ["expression"]),
    func=calculator, category="utility"))

registry.register(Tool(
    name="get_datetime", label="Date & heure", ui_description="Date et heure actuelles", icon="clock",
    description="Donne la date et l'heure actuelles dans un fuseau horaire (défaut Africa/Casablanca).",
    parameters=obj({"timezone": {"type": "string", "description": "Nom IANA, ex: Europe/Paris"}}),
    func=get_datetime, category="utility"))

registry.register(Tool(
    name="weather", label="Météo", ui_description="Météo actuelle et prévisions", icon="cloud",
    description="Météo actuelle et prévisions à 4 jours pour une ville du monde.",
    parameters=obj({"city": {"type": "string", "description": "Nom de la ville, ex: Rabat"}}, ["city"]),
    func=weather, category="utility"))
