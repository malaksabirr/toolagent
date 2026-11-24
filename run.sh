#!/usr/bin/env bash
# Lance backend (FastAPI :8000) + frontend (Vite :5173). Usage : ./run.sh
set -e
cd "$(dirname "$0")"

[ -f .env ] || { cp .env.example .env; echo "➜ .env créé : ouvre-le et colle ta clé API (LLM_API_KEY), puis relance ./run.sh"; exit 0; }

if [ ! -d backend/.venv ]; then
  echo "➜ Création de l'environnement Python…"
  python3 -m venv backend/.venv
fi
source backend/.venv/bin/activate
pip install -q -r backend/requirements.txt

if [ ! -d frontend/node_modules ]; then
  echo "➜ Installation des dépendances front (npm)…"
  (cd frontend && npm install --silent)
fi

trap 'kill 0' EXIT INT TERM
(cd backend && uvicorn app.main:app --reload --port 8000) &
(cd frontend && npm run dev -- --open) &
wait
