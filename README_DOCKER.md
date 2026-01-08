Docker deployment quickstart (PowerShell)

Prerequisites:
- Docker Desktop installed and running on Windows.

Build and run both services with docker-compose (from repo root):
```powershell
cd 'C:\Users\DELL\CrashCrew'
# Build and start (background)
docker-compose up --build -d

# View logs (optional)
docker-compose logs -f

# Stop and remove containers
docker-compose down
```

Notes:
- Backend is exposed on http://localhost:5000
- Frontend (served by nginx) is exposed on http://localhost:5173
- I copied the frontend build into nginx's default html folder, so it serves from "/" at port 5173.

If you prefer to run locally without Docker:
- Install Node.js and run the frontend dev server with npm install && npm run dev (see previous messages).
- Start backend via the Python venv: `\.venv\Scripts\python.exe backend\app.py`.
