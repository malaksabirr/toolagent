# ToolAgent — Agent conversationnel intelligent à outils

**Projet de Traitement Automatique du Langage Naturel (TALN)**  
**Sujet 10 : Agent conversationnel à outils**

ToolAgent est un assistant conversationnel intelligent conçu pour comprendre les demandes en langage naturel, sélectionner dynamiquement les outils adaptés et exploiter leurs résultats afin de produire des réponses pertinentes et contextualisées.

Contrairement à un chatbot classique, l'agent ne se limite pas à générer du texte : il peut décider d'utiliser un ou plusieurs outils, exécuter les opérations nécessaires et présenter les résultats directement dans l'interface conversationnelle.

## Fonctionnalités principales

L'agent dispose de plusieurs catégories d'outils qu'il peut sélectionner en fonction de la demande de l'utilisateur.

| Catégorie | Fonctionnalités |
|---|---|
| Recherche Web | Recherche d'informations en ligne et présentation de sources cliquables |
| Analyse de données | Lecture de fichiers CSV/Excel, exploration, statistiques et visualisations |
| Base de données SQL | Consultation de données, génération et exécution de requêtes SQL |
| Génération d'images | Création d'images à partir de descriptions textuelles |
| Documents | Lecture et résumé de documents textuels et PDF |
| Calculatrice | Résolution d'opérations et de calculs numériques |
| Météo | Consultation des conditions météorologiques |

L'agent prend également en charge les demandes nécessitant l'utilisation successive de plusieurs outils.

## Architecture technique

Le projet repose sur une architecture client-serveur composée de deux parties principales :

### Backend

Développé en Python avec FastAPI, le backend assure la gestion des conversations, l'orchestration de l'agent et l'exécution des outils.

- **FastAPI** : exposition des endpoints REST.
- **Boucle d'agent** : interaction entre le modèle de langage et les outils.
- **Function Calling** : sélection dynamique des outils selon le contexte.
- **Streaming SSE** : transmission progressive des réponses.
- **Pandas** : traitement et analyse des données.
- **SQLite** : stockage et interrogation des données.
- **API compatible OpenAI** : communication avec les modèles de langage.

### Frontend

Développé avec React, le frontend propose une interface conversationnelle permettant d'interagir avec l'agent et de visualiser les résultats.

- **React 18** : construction de l'interface.
- **Vite** : environnement de développement.
- **Recharts** : visualisation des données.
- **react-markdown** : rendu des réponses formatées.
- **Streaming en temps réel** : affichage progressif des réponses et de l'exécution des outils.

L'interface propose également un thème clair/sombre, un historique local des conversations et une gestion des fichiers.

## Technologies utilisées

| Domaine | Technologies |
|---|---|
| Langage Backend | Python |
| Framework Backend | FastAPI |
| Intelligence Artificielle | LLM, Function Calling |
| Traitement des données | Pandas |
| Base de données | SQLite |
| Communication | API REST, Server-Sent Events (SSE) |
| Frontend | React 18, JavaScript |
| Build Tool | Vite |
| Visualisation | Recharts |
| Rendu Markdown | react-markdown |
| Versionnement | Git, GitHub |

## Structure du projet

```text
toolagent/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── agent.py
│   │   ├── prompts.py
│   │   │
│   │   └── tools/
│   │       ├── base.py
│   │       ├── web.py
│   │       ├── data.py
│   │       ├── sql.py
│   │       ├── image.py
│   │       ├── docs.py
│   │       └── utils.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── seed_db.py
│
├── frontend/
│   ├── src/
│   │   ├── App
│   │   ├── store/
│   │   ├── components/
│   │   └── views/
│   ├── package.json
│   └── vite.config.js
│
├── docs/
│   └── ARCHITECTURE.md
│
├── samples/
├── scripts/
├── .env.example
├── .gitignore
├── Makefile
├── run.sh
└── README.md
```

## Installation et configuration

### Prérequis

- Python 3.10 ou supérieur.
- Node.js 18 ou supérieur.
- npm.
- Une clé API pour le fournisseur de modèle choisi, sauf utilisation d'un modèle local.

Sur macOS, les dépendances peuvent être installées avec Homebrew :

```bash
brew install python node
```

### 1. Récupération du projet

```bash
git clone https://github.com/malaksabirr/toolagent.git
cd toolagent
```

### 2. Configuration des variables d'environnement

Au premier lancement, le script `run.sh` prépare le fichier `.env` et s'arrête pour permettre sa configuration.

```bash
./run.sh
```

Ouvrir ensuite le fichier `.env` et renseigner les paramètres nécessaires :

```env
LLM_API_KEY=your_api_key
LLM_BASE_URL=your_provider_base_url
LLM_MODEL=your_model
```

Les autres paramètres éventuels sont documentés dans `.env.example`.

**Important :** le fichier `.env` contient des informations sensibles. Il ne doit jamais être ajouté au dépôt Git.

### 3. Lancement de l'application

Après configuration du fichier `.env` :

```bash
./run.sh
```

Le script installe les dépendances nécessaires et lance les services.

Interface Web : http://localhost:5173  
API Backend : http://localhost:8000  
Documentation API : http://localhost:8000/docs

## Fournisseurs de modèles de langage

ToolAgent utilise une interface de communication compatible avec l'API OpenAI, permettant de configurer différents fournisseurs selon leur compatibilité.

| Fournisseur | Configuration |
|---|---|
| Groq | API compatible OpenAI |
| OpenAI | API officielle |
| Ollama | Serveur local compatible OpenAI |
| Autres fournisseurs | Selon la compatibilité de leur API ou la présence d'un adaptateur dédié |

Pour Groq, le modèle proposé pour les démonstrations est `llama-3.3-70b-versatile`, sous réserve de sa disponibilité chez le fournisseur.

La qualité de sélection des outils dépend notamment des capacités du modèle utilisé.

## Lancement manuel

Il est également possible de démarrer séparément le backend et le frontend.

### Terminal 1 — Backend

```bash
cd backend

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000
```

### Terminal 2 — Frontend

```bash
cd frontend

npm install
npm run dev
```

L'interface est accessible à l'adresse :

http://localhost:5173

## Scénarios de démonstration

Les scénarios suivants permettent de tester les principales capacités de l'agent.

**1. Analyse de données**

Importer `samples/ventes.csv` et demander :

> Analyse ce fichier CSV et donne-moi un résumé avec les graphiques principaux.

**2. Analyse complémentaire**

Après l'analyse initiale :

> Quel est le total des ventes par région ?

L'agent peut utiliser l'outil `aggregate_dataset` pour effectuer l'agrégation.

**3. Recherche Web**

> Recherche les dernières actualités sur l'intelligence artificielle.

**4. Interrogation SQL**

> Quels sont les 5 clients qui ont le plus dépensé ?

L'agent exploite le schéma de la base de données pour construire et exécuter une requête.

**5. Génération d'images**

> Crée une image d'un paysage marocain au coucher du soleil.

**6. Résumé de documents**

Importer `samples/note_projet.txt` ou un PDF, puis demander :

> Résume ce document en présentant les idées principales.

**7. Réponse sans outil**

> Explique la différence entre un RNN et un Transformer.

**8. Calcul numérique**

> Combien font 17,5 % de 23 480 ?

**9. Utilisation de plusieurs outils**

> Quelle est la météo à Rabat et convertis 22 °C en Fahrenheit.

Ces scénarios permettent d'évaluer la sélection des outils, l'exécution des opérations et la présentation des résultats.

## Interface utilisateur

L'interface conversationnelle intègre plusieurs fonctionnalités :

- Streaming des réponses en temps réel.
- Visualisation des outils sélectionnés et de leur exécution.
- Affichage de tableaux et de graphiques.
- Sources Web cliquables.
- Suggestions de questions complémentaires.
- Import de fichiers par glisser-déposer.
- Historique local des conversations.
- Activation et désactivation des outils.
- Export des rapports au format Markdown.
- Thème clair et sombre.

## Extensibilité : ajouter un nouvel outil

L'architecture repose sur un registre commun permettant d'ajouter de nouvelles capacités à l'agent.

L'intégration d'un outil suit trois étapes principales :

**1. Créer le module**

Ajouter un fichier dans `backend/app/tools/`, par exemple :

```text
backend/app/tools/mon_outil.py
```

**2. Implémenter la fonctionnalité**

Définir une fonction qui réalise le traitement demandé et retourne un résultat au format `ToolResult`, avec éventuellement des éléments d'interface dans `ui`.

**3. Enregistrer l'outil**

Utiliser `registry.register(Tool(...))` et intégrer le module dans `tools/__init__.py`.

Une fois enregistré, l'outil peut être découvert et utilisé par l'agent selon les mécanismes de sélection prévus.

## Tests

Les tests unitaires des outils sont regroupés dans le dossier `backend/tests/`.

Pour les exécuter :

```bash
make test
```

## Dépannage

| Problème | Solution |
|---|---|
| Backend hors ligne | Vérifier que le serveur FastAPI fonctionne sur le port 8000 |
| Clé API manquante ou invalide | Vérifier les paramètres du fichier `.env` |
| Recherche Web sans résultat | Réessayer si le fournisseur limite temporairement les requêtes |
| Génération d'image indisponible | Vérifier le fournisseur configuré et la disponibilité de son service |
| Port déjà utilisé | Identifier le processus avec `lsof -i :8000` ou `lsof -i :5173` |

## Collaboration et versionnement

Le projet est versionné avec Git et hébergé sur GitHub.

Pour contribuer :

```bash
git pull origin main
```

Après avoir effectué des modifications :

```bash
git add .
git commit -m "Description des modifications"
git push origin main
```

Chaque collaborateur doit disposer de son propre fichier `.env`, créé à partir de `.env.example`.

Les clés API, bases de données locales, environnements virtuels et fichiers générés ne doivent pas être partagés dans le dépôt.

## Objectif pédagogique

Ce projet a pour objectif de mettre en pratique les concepts du Traitement Automatique du Langage Naturel à travers la conception d'un agent conversationnel capable d'interagir avec des outils externes.

Il permet notamment d'explorer :

- La compréhension des demandes en langage naturel.
- L'interaction entre un LLM et des outils.
- Le Function Calling et la sélection dynamique des capacités.
- L'orchestration de plusieurs opérations.
- La communication asynchrone et le streaming.
- L'intégration d'une interface conversationnelle avec un backend intelligent.

---

**ToolAgent — Projet académique de Traitement Automatique du Langage Naturel (TALN).**
