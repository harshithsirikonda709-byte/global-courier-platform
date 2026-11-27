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

## Companion and visit workflow

- Account registration supports family, parent, or companion accounts through the same Supabase Auth project. Companion accounts do not receive family memberships.
- Companions submit a profile and recurring weekly availability. Profile self-reporting cannot set verification or approval status.
- Administrators are identified by trusted Supabase user IDs in `ADMIN_USER_IDS` (comma-separated). Add only designated operator IDs and restart the API. Admin APIs are denied by default when the setting is empty.
- Admin review requires a completed companion profile, manual identity verification, and explicit approval. Only verified and approved companions can be assigned; the API also checks availability and prevents overlapping assignments.
- Families can request a visit only for a parent they are authorized to book for and who has current personal consent. Companions can accept/reject and check in/out. Parent consent withdrawal cancels requested/assigned/accepted visits and prevents future assignment or check-in.
- Parents register with the `parent` account type. A designated administrator must link their account to the correct parent profile after verifying identity. Family reports are not consent.
- This demo records the identity document type only; documents must be checked through an approved offline process. Secure document upload, audit/retention policy, and production identity-provider integration remain deployment decisions.
- Visit requirements are for companionship preferences only. CareCircle does not provide medical or nursing care.

The API publishes the workflow contract at `/docs` (for example `http://127.0.0.1:8000/docs`). Core endpoints include `/api/v1/carecircle/companions/me`, `/api/v1/carecircle/companions/me/availability`, `/api/v1/carecircle/admin/companions`, `/api/v1/carecircle/visits`, `/api/v1/carecircle/companion/visits`, and `/api/v1/carecircle/admin/visits`.

## Tests

From `CareCircle\backend` run:

```powershell
python -m unittest discover -s tests -v
alembic upgrade head
alembic check
```

The backend tests cover parent-family isolation, consent and withdrawal, shared Supabase token acceptance, companion account boundaries, admin review/approval gates, availability, visit assignment, and the visit lifecycle.

## Start the frontend

```powershell
cd CareCircle
npm install
npm run dev
```

Open `http://localhost:3000`.
