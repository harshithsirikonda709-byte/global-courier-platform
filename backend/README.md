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
| PUT | `/api/v1/customers/me` | Updates the authenticated customer's profile |
| GET | `/health` | Service health check |

The authentication endpoints delegate password management to Supabase Auth. The profile endpoints require `Authorization: Bearer <access-token>` and enforce Supabase's row-level security in the database.

Registration returns 201 with a session when the account can sign in immediately. A 202 response with `confirmation_required: true` tells the frontend to show the email confirmation screen. After confirmation, use the login endpoint.

Set SUPABASE_JWT_ALGORITHM to the active signing algorithm in your project's JWT signing keys settings. ES256 and RS256 use the project's published keys. Legacy HS256 requires SUPABASE_JWT_SECRET. Set CORS_ALLOWED_ORIGINS to a JSON array of frontend origins, including the scheme and port.

From backend, run `python -m unittest discover -s tests -v` for the API suite. To verify the database, run the initial migration twice on a fresh disposable Supabase project, then execute database/test_profile_rls.sql in the same project's SQL Editor. The script creates two temporary Auth users, checks that the signup trigger populated both profiles, and exercises reads and updates as the authenticated role. Success reaches ROLLBACK with no exception. Record the project reference and result in the PR.
