# ToolAgent — Agent conversationnel à outils

Projet de TAL · **Sujet 10 : Agent conversationnel à outils**.
Un assistant capable de répondre à n'importe quelle question et de **choisir seul les bons outils** (function calling) :
recherche web, analyse de fichiers CSV/Excel avec graphiques, SQL, génération d'images, résumé de documents, calculatrice, météo.

- **Backend** : Python · FastAPI · boucle d'agent avec streaming SSE · pandas · SQLite · API LLM compatible OpenAI
- **Frontend** : React 18 · Vite · Recharts · react-markdown (interface fixe, thème clair/sombre)

## Démarrage rapide (macOS / Cursor)

Prérequis : Python 3.10+ et Node 18+ (`brew install python node`).

```bash
unzip toolagent.zip && cd toolagent
./run.sh            # 1re fois : crée .env et s'arrête
# → ouvre .env, colle ta clé dans LLM_API_KEY (voir ci-dessous), puis :
./run.sh            # installe tout et ouvre http://localhost:5173
```

### Quelle clé API ?
| Option | Coût | Config dans `.env` |
|---|---|---|
| **Groq** (recommandé) | gratuit | clé sur console.groq.com/keys, modèle `llama-3.3-70b-versatile` |
| OpenAI | payant | `LLM_BASE_URL=https://api.openai.com/v1`, `LLM_MODEL=gpt-4o-mini` |
| Anthropic | payant | `LLM_BASE_URL=https://api.anthropic.com/v1/`, `LLM_MODEL=claude-sonnet-4-5` |
| Ollama (local) | gratuit | `LLM_BASE_URL=http://localhost:11434/v1`, `LLM_MODEL=qwen2.5:7b` |

Plus le modèle est fort, meilleur est le choix des outils : pour la démo, préfère un modèle ≥ 70B ou GPT-4o-mini / Claude.

### Lancement manuel (2 terminaux)
```bash
# Terminal 1 — backend
cd ~/Downloads/toolagent
python3 -m venv backend/.venv && source backend/.venv/bin/activate
pip install -r backend/requirements.txt
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend
cd ~/Downloads/toolagent/frontend
npm install && npm run dev
```

## Scénarios de démonstration
1. **Analyse de données** : joindre `samples/ventes.csv` → « Analyse ce fichier CSV et donne-moi un résumé avec les graphiques principaux. »
2. **Question de suivi** : « Quel est le total des ventes par région ? » (outil `aggregate_dataset`)
3. **Web** : « Recherche les dernières actualités sur l'IA. » (sources cliquables)
4. **SQL** : « Quels sont les 5 clients qui ont le plus dépensé ? » (schéma → requête → tableau)
5. **Image** : « Crée une image d'un paysage marocain au coucher du soleil. »
6. **Document** : joindre `samples/note_projet.txt` (ou un PDF) → « Résume ce document. »
7. **Sans outil** : « Explique la différence entre RNN et Transformer. » · **Calcul** : « Combien font 17,5 % de 23 480 ? »
8. **Multi-outils** : « Quelle est la météo à Rabat et convertis 22 °C en Fahrenheit. »

## Fonctionnalités de l'interface
Streaming token par token · trace des outils utilisés en direct · graphiques (courbe, donut, barres) · tableaux · sources cliquables ·
suggestions de questions de suivi · export du rapport (.md) · historique local · activation/désactivation des outils · glisser-déposer de fichiers · thème clair/sombre.

## Structure
```
backend/app/
  main.py        API : /api/chat (SSE), /api/upload, /api/tools, /api/health
  agent.py       boucle LLM ↔ outils (streaming, erreurs, nb max d'étapes)
  prompts.py     prompt système (règles d'usage des outils, structure des réponses)
  tools/         web · data · sql · image · docs · utils (registre commun dans base.py)
  seed_db.py     base SQLite de démo (clients, produits, commandes)
backend/tests/   tests unitaires des outils
frontend/src/    App · store (état + streaming) · components (Chat, Message, Blocks, Sidebar, Views)
docs/ARCHITECTURE.md   architecture, protocole d'événements, choix de conception, plan d'évaluation
```

## Ajouter un outil (3 étapes)
Créer `backend/app/tools/mon_outil.py` avec une fonction retournant `ToolResult(content, ui=[...])`, l'enregistrer avec
`registry.register(Tool(...))`, puis l'importer dans `tools/__init__.py`. Il apparaît automatiquement dans l'interface.

## Dépannage
- **« Backend hors ligne »** : le backend ne tourne pas sur le port 8000 (`lsof -i :8000`).
- **« Clé API manquante / invalide »** : vérifier `.env` puis relancer le backend.
- **Recherche web sans résultat** : DuckDuckGo limite parfois le débit ; réessayer.
- **Image qui ne charge pas** : le service gratuit est parfois saturé → bouton « Réessayer », ou `IMAGE_PROVIDER=openai`.
- **Tests** : `make test`.
