# Backend foundation

## Run locally

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and configure your Supabase settings.
4. Apply the database migration `database/001_initial_schema.sql` in your Supabase SQL Editor.
5. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
6. Interactive Swagger documentation is available at `http://localhost:8000/docs`.

---

## API contract

| Method | Path | Status | Purpose |
|---|---|---|---|
| POST | `/api/v1/auth/register` | 201 / 202 | Registers a Supabase customer account. Returns 201 with `AuthSession` if immediate session is available, or 202 with `ConfirmationPending` when email confirmation is enabled. |
| POST | `/api/v1/auth/login` | 200 | Authenticates with email/password and returns an `AuthSession` with access and refresh tokens. |
| GET | `/api/v1/customers/me` | 200 | Returns the profile of the authenticated customer extracted from the JWT token. |
| PUT | `/api/v1/customers/me` | 200 | Updates the authenticated customer's profile (name, phone, address). |
| GET | `/health` | 200 | Health check returning status and current environment. |

---

## Configuration & Environment Variables

- `SUPABASE_URL`: Your Supabase project URL (e.g., `https://xyzcompany.supabase.co`).
- `SUPABASE_ANON_KEY`: Your Supabase anon public API key.
- `SUPABASE_JWT_ALGORITHM`: Signing algorithm used by Supabase Auth (`ES256`, `RS256`, `HS256`, or `AUTO`). Default is `ES256`.
  - For `ES256` or `RS256`: Signing keys are dynamically retrieved from `{SUPABASE_URL}/auth/v1/.well-known/jwks.json`.
  - For `HS256`: Verified locally using `SUPABASE_JWT_SECRET`.
  - For `AUTO`: Detects and validates against the token's algorithm safely.
- `SUPABASE_JWT_SECRET`: The project JWT secret (required when using `HS256`).
- `CORS_ALLOWED_ORIGINS`: Allowed origins for CORS. Supports either JSON array format or comma-separated strings:
  - `["http://localhost:3000", "http://localhost:5173"]`
  - `http://localhost:3000, http://localhost:5173`
- `ENVIRONMENT`: Runtime environment name (default `development`).

---

## Running Automated Tests

Run the test suite from the `backend/` directory:
```bash
python -m unittest discover -s tests -v
```

The test suite covers:
- User registration (immediate session creation and email confirmation pending flows).
- User authentication and invalid credential handling.
- Customer profile retrieval and updates.
- **Customer profile isolation**: Verifies that Customer A cannot read or modify Customer B's profile, even if attempted via forged tokens or query manipulation.
- Strict JWT validation: Issuer (`/auth/v1`), audience (`authenticated`), expiration (`exp`), and valid `sub` UUID format.
- CORS environment variable parsing (JSON lists and comma-separated strings).

---

## Database Migration & RLS Policy Verification

1. **Idempotent Migration (`database/001_initial_schema.sql`)**:
   - Creates `public.customer_profiles` linked with foreign key cascade to `auth.users(id)`.
   - Attaches `on_auth_user_created` trigger on `auth.users` with safe `ON CONFLICT DO UPDATE` handling.
   - Enforces PostgreSQL Row Level Security (RLS) where customers can only `SELECT` and `UPDATE` their own profile records (`auth.uid() = user_id`).
   - Includes `DROP POLICY IF EXISTS` guards so it can be safely re-run on existing databases without conflicts.

2. **Verifying RLS Policies (`database/test_profile_rls.sql`)**:
   - In your test Supabase project's SQL Editor, execute `database/test_profile_rls.sql`.
   - The test script inserts two test users into `auth.users`, switches to the `authenticated` role as User 1, and verifies that:
     1. User 1 can see and update their own profile.
     2. User 1 CANNOT see User 2's profile.
     3. User 1 CANNOT update User 2's profile.
     4. User 2's profile remains untouched.
     5. The transaction rolls back cleanly, leaving no test artifacts.
