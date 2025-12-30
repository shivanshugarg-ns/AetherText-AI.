# AetherText AI

AI Content Generator with FastAPI backend and React (Vite + TypeScript) frontend. Supports summarize, translate, and generate tasks with streaming output, token usage, and cost estimation.

## Project Structure
- `backend/` FastAPI app (`app/main.py`, API routes under `/api/v1`)
- `frontend/` React + Vite (TypeScript)

## Requirements
- Python 3.10+
- Node.js 18+
- OpenAI API key

## Backend setup
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# env
cat > .env <<'EOF'
OPENAI_API_KEY=your_key
OPENAI_DEFAULT_MODEL=gpt-4.1-mini
OPENAI_FALLBACK_MODEL=gpt-4o-mini
OPENAI_PROMPT_COST_PER_1K=0.15
OPENAI_COMPLETION_COST_PER_1K=0.60
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_ORIGIN=http://localhost:5173
EOF

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API endpoints
- `POST /api/v1/ai` — non-streaming; body: `{task, input_text, target_language?, options}`
- `POST /api/v1/ai/stream` — SSE streaming; events: `chunk`, `end` (with usage + cost), `error`
- `GET /api/v1/usage/recent` — recent token/cost history
- `GET /health` — readiness

## Frontend setup
```bash
cd frontend
npm install
npm run dev  # http://localhost:5173
# or build
npm run build
```

Env: `frontend/.env`
```
VITE_API_BASE_URL=http://localhost:8000
```

## Usage
- Open frontend, choose task (Summarize/Translate/Generate), enter text (and target language for translate), optionally toggle streaming.
- Output streams live (if supported). Tokens and estimated cost shown per call; recent usage tab shows history.

## Deployment options
- **Render/Fly/Heroku-like**: Deploy backend as a web service; set env vars above. Serve frontend as static build (`npm run build`) on Netlify/Vercel/Render static site; set `VITE_API_BASE_URL` to backend URL.
- **Single VM/Nginx**: Build frontend and serve `frontend/dist`; reverse-proxy backend uvicorn with Nginx.
- **Docker (outline)**: Containerize backend with uvicorn; containerize frontend as static nginx. Configure env vars; expose backend on 8000; serve frontend on 80 and point it to backend URL.

## Notes
- Secrets: keep `.env` out of git.
- Models/costs are adjustable via env.
- Streaming uses SSE; ensure client/browser supports ReadableStream.
