# RESCUEGRID Backend
FastAPI + SQLAlchemy + SQLite.

Run:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Demo accounts use `demo123`.


## Deployment

### Render
1. Create a new Web Service from this backend folder/repository.
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set `RESCUEGRID_SECRET` to a strong secret.
5. Set `RESCUEGRID_CORS` to your Vercel frontend URL, comma-separated if needed. The API also permits Vercel preview origins through the configured Vercel regex.

### Frontend
Set Vercel environment variable `VITE_API_URL` to the deployed backend API base, ending in `/api`.
