# SobaAI

Assistant IA web : interface de chat React, API FastAPI, réponses générées par Claude (Anthropic) en streaming.

## Stack

| Couche | Technologies |
|---|---|
| Frontend | React 19, Vite, TypeScript, Tailwind CSS 4 |
| Backend | Python 3.12+, FastAPI, SQLAlchemy 2 (async), Alembic |
| IA | API Claude via le SDK `anthropic` (modèle par défaut : `claude-sonnet-5-5`) |
| Base de données | PostgreSQL 16 + pgvector |
| Infra | Docker Compose |

## Structure

```
SobaAI/
├── backend/      # API FastAPI (app/), migrations (alembic/), tests
├── frontend/     # Application React (src/)
├── docker-compose.yml
└── .env.example
```

## Démarrage rapide (développement local)

### 1. Configuration

```bash
cp .env.example .env
# puis renseignez dans .env :
#   ANTHROPIC_API_KEY  (clé API Claude)
#   JWT_SECRET         (python -c "import secrets; print(secrets.token_urlsafe(32))")
```

Sans `JWT_SECRET`, une clé temporaire est générée à chaque démarrage du backend : tout le monde est alors déconnecté à chaque redémarrage.

### 2. Base de données

```bash
docker compose up -d db
```

### 3. Backend

```bash
cd backend
python -m venv .venv
# Windows : .venv\Scripts\activate    |    macOS/Linux : source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

API : http://localhost:8000 · Documentation interactive : http://localhost:8000/docs

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Application : http://localhost:5173 (les appels `/api` sont redirigés vers le backend).

## Tout lancer avec Docker

```bash
docker compose --profile full up --build
```

## Commandes utiles

| Commande | Dossier | Rôle |
|---|---|---|
| `pytest` | backend | Tests (SQLite en mémoire, ni PostgreSQL ni clé API requis) |
| `ruff check . && ruff format .` | backend | Lint + formatage |
| `alembic revision --autogenerate -m "..."` | backend | Nouvelle migration |
| `npm run lint` | frontend | ESLint |
| `npm run format` | frontend | Prettier |
| `npm run build` | frontend | Build de production |

## Endpoints

| Méthode | Route | Description |
|---|---|---|
| GET | `/api/health` | État de l'API et de la base (public) |
| POST | `/api/auth/register` | `{ "email", "password" }` (8 caractères min.) → crée le compte et ouvre la session |
| POST | `/api/auth/login` | `{ "email", "password" }` → ouvre la session |
| POST | `/api/auth/logout` | Ferme la session |
| GET | `/api/auth/me` | Utilisateur connecté |
| POST | `/api/chat` | `{ "conversation_id"?: "...", "message": "..." }` → réponse texte en streaming. Sans `conversation_id`, une conversation est créée et son id est renvoyé dans l'en-tête `X-Conversation-Id`. |
| GET | `/api/conversations` | Liste des conversations (plus récente d'abord) |
| GET | `/api/conversations/{id}` | Une conversation et ses messages |
| DELETE | `/api/conversations/{id}` | Supprime une conversation |

Toutes les routes hors `/api/health` et `/api/auth/*` exigent d'être connecté. La session est un jeton JWT stocké dans un cookie `httpOnly` (`SameSite=Lax`, `Secure` si `COOKIE_SECURE=true`). Chaque utilisateur ne voit que ses propres conversations.

## Feuille de route

- [x] MVP : chat en streaming
- [x] Sauvegarde des conversations en base
- [x] Authentification (email + mot de passe)
- [ ] Recherche dans des documents (RAG avec pgvector)
