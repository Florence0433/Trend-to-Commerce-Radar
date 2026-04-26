# Trend-to-Commerce

Trend-to-Commerce is a course practice project that turns weekly hot keyword data, post/comment text, and merchandising records into a production-style trend insight website. It provides heat leaderboards, topic exploration, merchandising suggestions, and AI-powered Q&A. Built with a FastAPI backend, a browser-based dashboard, SQLite job storage, Docker deployment, and remote LLM calls, it helps merchants quickly identify rising demand and generate actionable product ideas.

## Important: Private API Key Included

This release package includes a configured `.env` file for remote model calls. Keep this folder and zip file private because `.env` contains a real API key.

If you need to replace the key, edit `.env`:

```env
GENERATION_API_URL=https://your-provider.example/v1/chat/completions
GENERATION_API_KEY=your_api_key_here
GENERATION_MODEL=deepseek-v3
GENERATION_PREFER_REMOTE=1
GENERATION_FALLBACK_ON_ERROR=1
```

The release version uses:

- `web/` as the official product webpage.
- `backend/` as one FastAPI server for both the API and static frontend.
- `Data/` as the required runtime data directory.
- SQLite for Question job history.

## Quick Start: Local Computer

Requirements:

- Python 3.11 or newer recommended.

macOS/Linux:

```bash
./scripts/start_local.sh
```

Windows:

```bat
scripts\start_local.bat
```

Then open:

```text
http://127.0.0.1:8000
```

The app will also expose:

```text
http://127.0.0.1:8000/api/health
```

## Quick Start: Docker

Requirements:

- Docker
- Docker Compose

```bash
docker compose up --build
```

Then open:

```text
http://127.0.0.1:8000
```

To use a different host port:

```bash
TREND_TO_COMMERCE_PORT=8080 docker compose up --build
```

## Server Deployment

1. Copy the project to the server.
2. Ensure the `Data/` directory is present.
3. Confirm `.env` has the correct remote model credentials.
4. Run:

```bash
docker compose up --build -d
```

5. Put a reverse proxy such as Nginx or Caddy in front of port `8000` if you need a public domain and HTTPS.

## Environment Variables

The included `.env` is already configured for remote model calls. `.env.example` is provided as a clean template.

Important variables:

- `TREND_TO_COMMERCE_DATA_DIR`: path to the runtime `Data/` directory. Defaults to `./Data` locally and `/app/Data` in Docker.
- `TREND_TO_COMMERCE_DB_PATH`: SQLite job database path. Use a persistent path or volume in production.
- `GENERATION_API_URL`: OpenAI-compatible chat completions URL.
- `GENERATION_API_KEY`: API key for remote generation.
- `GENERATION_MODEL`: remote generation model name.
- `GENERATION_TIMEOUT_SECONDS`: remote model timeout. Defaults to `45`.
- `GENERATION_FALLBACK_ON_ERROR`: defaults to `1`, so Question falls back to local data if the remote model fails.
- `GENERATION_PREFER_REMOTE`: defaults to `1`, so configured deployments call the remote model first.
- `GENERATION_TRANSLATE_WITH_API`: defaults to `0`. Keep it off for reliable local and server runs; set to `1` only if the server can reach Google Translate.
- `GENERATION_TRANSLATION_TIMEOUT_SECONDS`: translation API timeout. Defaults to `5`.
- `TREND_TO_COMMERCE_CORS_ORIGINS`: optional comma-separated list of allowed cross-origin domains. Leave empty for normal same-origin production deployment.

If remote generation variables are set, Question calls the remote model for full answers. If the call fails, Trend-to-Commerce still uses local keyword post/comment data for a basic fallback answer.

## Data Requirements

The backend reads these directories from `Data/`:

- `Data/行业热度榜`
- `Data/关键词具体帖子评论`

The product webpage also includes embedded leaderboard fallback data in `web/js/data-embedded.js`, so the dashboard can render core screens even when some CSV files are unavailable. The Question API still needs `Data/` for best results.

## Troubleshooting

### The Question page waits too long

Check that the backend is running:

```bash
curl http://127.0.0.1:8000/api/health
```

If it is running but slow, the server may be waiting for the remote model API. Set:

```env
GENERATION_FALLBACK_ON_ERROR=1
GENERATION_TIMEOUT_SECONDS=20
```

If remote generation is unavailable, Trend-to-Commerce falls back to local keyword post/comment data so the Question page can still return a basic answer.

### The page loads but API requests fail

Use the FastAPI-served URL:

```text
http://127.0.0.1:8000
```

Avoid opening `web/index.html` directly with `file://` for release usage.

### Docker starts but data is missing

Confirm the project has a populated `Data/` directory and that Compose is mounting it:

```yaml
volumes:
  - ./Data:/app/Data:ro
```

### Job history disappears

Use a persistent database path. Docker Compose stores it in the named volume `trend-to-commerce-storage`.

## Included Files

Keep these files/folders:

- `backend/`
- `web/`
- `Data/`
- `scripts/`
- `.env`
- `.env.example`
- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`
- `README.md`

The package intentionally excludes local virtual environments, Python caches, local SQLite job history, and legacy local env files.
