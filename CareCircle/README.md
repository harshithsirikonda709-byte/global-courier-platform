# CareCircle

CareCircle is an AIVA companionship platform module.

## Implemented feature

Family Parent Profile Management includes:

- Family registration and login
- Parent profile creation
- Parent detail and history views
- Parent profile updates
- Address and contact storage
- Language, interests and accessibility preferences
- Emergency contacts
- Parent consent recording
- Consent withdrawal
- JWT authentication and family authorization

## Start the frontend

```powershell
cd CareCircle
npm install
npm run dev
```

Open `http://localhost:3000`.

## Start the backend

```powershell
cd CareCircle
python -m pip install -r backend\requirements.txt
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend creates a local SQLite database by default.

For PostgreSQL or Supabase, set `DATABASE_URL` to a PostgreSQL connection string and set a strong `JWT_SECRET`. Copy `backend/.env.example` and use `backend/.env`.
