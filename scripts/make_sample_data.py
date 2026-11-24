"""Génère samples/ventes.csv (10 000 lignes) pour tester l'agent."""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

rnd = random.Random(7)
PRODUITS = {"Tech": ["Laptop Pro", "Smartphone X", "Écouteurs BT", "Montre connectée"],
            "Maison": ["Canapé 3 places", "Lampe design", "Cafetière", "Aspirateur robot"],
            "Mode": ["Veste cuir", "Sneakers", "Caftan moderne", "Sac à main"]}
out = Path(__file__).resolve().parents[1] / "samples" / "ventes.csv"
start = date(2026, 1, 1)
with out.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["date", "produit", "catégorie", "ventes", "région"])
    for _ in range(10000):
        d = start + timedelta(days=rnd.randint(0, 150))
        cat = rnd.choices(list(PRODUITS), [42, 34, 24])[0]
        region = rnd.choices(["Rabat", "Casablanca", "Marrakech"], [35, 40, 25])[0]
        growth = 1 + (d - start).days / 150 * 0.6
        w.writerow([d.isoformat(), rnd.choice(PRODUITS[cat]), cat, round(rnd.uniform(80, 900) * growth, 2), region])
print("OK", out)
