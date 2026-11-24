"""Crée la base SQLite de démonstration (clients, produits, commandes)."""
from __future__ import annotations

import random
import sqlite3
from datetime import date, timedelta

from .config import DB_PATH

VILLES = ["Casablanca", "Rabat", "Marrakech", "Fès", "Tanger", "Agadir", "Meknès", "Oujda"]
PRENOMS = ["Yasmine", "Omar", "Salma", "Youssef", "Imane", "Mehdi", "Hajar", "Anas", "Khadija", "Amine", "Nadia", "Reda"]
NOMS = ["Benali", "El Idrissi", "Alaoui", "Tazi", "Bennani", "Chraibi", "Lahlou", "Fassi", "Berrada", "Zniber"]
PRODUITS = [("Laptop Pro", "Tech", 9500), ("Smartphone X", "Tech", 6200), ("Écouteurs BT", "Tech", 800),
            ("Montre connectée", "Tech", 1900), ("Canapé 3 places", "Maison", 5400), ("Lampe design", "Maison", 650),
            ("Cafetière", "Maison", 1200), ("Aspirateur robot", "Maison", 3200), ("Veste cuir", "Mode", 1800),
            ("Sneakers", "Mode", 950), ("Caftan moderne", "Mode", 2400), ("Sac à main", "Mode", 1400)]


def ensure_db(force: bool = False) -> None:
    if DB_PATH.exists() and not force:
        return
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    DB_PATH.unlink(missing_ok=True)
    rnd = random.Random(42)
    con = sqlite3.connect(DB_PATH)
    con.executescript("""
    CREATE TABLE clients (id INTEGER PRIMARY KEY, nom TEXT, email TEXT, ville TEXT, date_inscription TEXT);
    CREATE TABLE produits (id INTEGER PRIMARY KEY, nom TEXT, categorie TEXT, prix REAL);
    CREATE TABLE commandes (id INTEGER PRIMARY KEY, client_id INTEGER REFERENCES clients(id),
        produit_id INTEGER REFERENCES produits(id), quantite INTEGER, date_commande TEXT, statut TEXT);
    """)
    for i in range(1, 201):
        nom = f"{rnd.choice(PRENOMS)} {rnd.choice(NOMS)}"
        d = date(2024, 1, 1) + timedelta(days=rnd.randint(0, 700))
        con.execute("INSERT INTO clients VALUES (?,?,?,?,?)",
                    (i, nom, f"{nom.lower().replace(' ', '.')}{i}@mail.ma", rnd.choices(VILLES, [30, 20, 15, 10, 10, 7, 5, 3])[0], d.isoformat()))
    for i, (n, c, p) in enumerate(PRODUITS, 1):
        con.execute("INSERT INTO produits VALUES (?,?,?,?)", (i, n, c, p))
    for i in range(1, 3001):
        d = date(2025, 1, 1) + timedelta(days=rnd.randint(0, 600))
        con.execute("INSERT INTO commandes VALUES (?,?,?,?,?,?)",
                    (i, rnd.randint(1, 200), rnd.randint(1, len(PRODUITS)), rnd.randint(1, 4), d.isoformat(),
                     rnd.choices(["livrée", "en cours", "annulée"], [80, 14, 6])[0]))
    con.commit()
    con.close()


if __name__ == "__main__":
    ensure_db(force=True)
    print(f"Base créée : {DB_PATH}")
