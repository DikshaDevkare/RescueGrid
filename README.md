# RESCUEGRID — ALG-WEB-02 Final

Offline-first disaster response and emergency coordination platform.

## Project structure

- `frontend/` — React + TypeScript + Vite PWA
- `backend/` — FastAPI + SQLAlchemy + SQLite

## Run locally

### Backend
Recommended: Python 3.12.x.

```bash
cd backend
python -m venv venv
# Windows PowerShell
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -q
uvicorn app.main:app --reload
```

Backend: http://127.0.0.1:8000
Swagger: http://127.0.0.1:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run build
npm run dev
```

Frontend: http://127.0.0.1:5173

The frontend defaults to `http://127.0.0.1:8000/api`. For deployment, create a Vercel environment variable named `VITE_API_URL` pointing to the deployed backend API, including `/api`.

## Demo accounts

- Community: `community@rescuegrid.demo` / `demo123`
- Rescue: `rescue@rescuegrid.demo` / `demo123`
- Admin: `admin@rescuegrid.demo` / `demo123`

## Important

The backend dependency stack should be installed with Python 3.12.x for the most reliable local setup. If a machine uses a newer Python release and pip attempts to compile `pydantic-core`, use Python 3.12 instead of changing project code.

## Deployment

- Frontend: deploy `frontend/` to Vercel.
- Backend: deploy `backend/` to a Python service such as Render using `render.yaml`.
- Set `VITE_API_URL` on Vercel to the deployed backend URL ending in `/api`.
- Set a strong `RESCUEGRID_SECRET` on the backend in production.
