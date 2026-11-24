# Backend foundation

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add Supabase credentials.
4. Run `database/001_initial_schema.sql` in the Supabase SQL Editor.
5. Start the API: `uvicorn app.main:app --reload --port 8000`

Interactive documentation is at `http://localhost:8000/docs`.

## Day 1 API contract

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/auth/register` | Creates a Supabase customer account |
| POST | `/api/v1/auth/login` | Returns a customer session token |
| GET | `/api/v1/customers/me` | Returns the authenticated customer's profile |
| PUT | `/api/v1/customers/me` | Creates or updates the authenticated customer's profile |
| GET | `/health` | Service health check |

The authentication endpoints delegate password management to Supabase Auth. The profile endpoints require `Authorization: Bearer <access-token>` and enforce Supabase's row-level security in the database.
