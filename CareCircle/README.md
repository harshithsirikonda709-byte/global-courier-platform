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
- Shared Supabase authentication and family authorization
- Family-reported consent kept separate from parent-authenticated personal consent

## Configure and migrate the backend

```powershell
cd CareCircle\backend
Copy-Item .env.example .env
# Configure DATABASE_URL and the same Supabase Auth project used by Courier.
python -m pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Schema changes are managed with Alembic; the application does not create tables at startup. Use `alembic revision --autogenerate -m "describe change"` to prepare a migration, review it, then apply with `alembic upgrade head`.

For a pre-Alembic CareCircle database, back it up first, then run `alembic stamp f19e51001d9a` followed by `alembic upgrade head` to apply the shared-auth and consent migration. Existing local credentials are removed; users must authenticate through the shared Supabase project. For production data, map existing user identities to verified Supabase accounts before cutover.

CareCircle validates access tokens using the same Supabase issuer, `authenticated` audience, and signing algorithm/JWKS configuration as the Courier backend. Set `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_JWT_ALGORITHM`, and (for HS256 only) `SUPABASE_JWT_SECRET` in `.env`.

Family members can record a family report about consent, but that report is never active personal consent. Only the authenticated user linked to the parent profile can record or withdraw personal consent.

## Start the frontend

```powershell
cd CareCircle
npm install
npm run dev
```

Open `http://localhost:3000`.
