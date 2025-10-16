# LinkedIn Job Scraper & Alert System

A modern full-stack app that scrapes LinkedIn jobs using Selenium, stores them, and provides alerts and a sleek dashboard.

## Stack
- Backend: FastAPI, SQLAlchemy, APScheduler, Selenium, SQLite
- Frontend: React (Vite), Tailwind

## Prereqs
- Python 3.11+
- Node.js 18+
- Chrome installed

## Backend Setup
```
cd backend
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Create .env (see .env.example)
uvicorn app.main:app --reload --port 8000
```

## Frontend Setup
```
cd frontend
npm install
# Create .env (VITE_API_URL=http://localhost:8000/api)
npm run dev
```

## Usage
1. Open http://localhost:3000
2. Use search bar and filters
3. Click "Run Scrape" to fetch latest jobs and see them appear

## Deploy
- Backend: Render/Railway (set env vars, use `uvicorn app.main:app`)
- Frontend: Vercel (set `VITE_API_URL` to backend URL)

## Notes
- LinkedIn may rate-limit or change markup; adjust selectors in `app/services/scraper.py` as needed.
- For email alerts (Gmail), use an app password.

## Deployment checklist (critical)
- Ensure frontend `VITE_API_URL` points to your deployed backend.
- Deploy backend on a non-serverless host (Render/Railway/Fly) for Selenium and APScheduler.
- Verify `/api/health` and `/api/version` on the backend before redeploying the frontend.
