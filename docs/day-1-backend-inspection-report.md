# Day 1 backend inspection report — 24 November 2026

## Findings

- The repository was an initial scaffold: it contained a project README, empty `frontend/` and `database/` folders, and no `backend/` directory or FastAPI source.
- The chosen stack is FastAPI with Supabase PostgreSQL, Supabase Auth, and Supabase Storage.
- There was no existing database configuration, API, migration, or application logic to preserve.

## Implemented foundation

- FastAPI application with versioned `/api/v1` routes and a `/health` endpoint.
- Customer account registration and login endpoints, delegating credential management to Supabase Auth.
- Authenticated customer profile read/update endpoints.
- Environment-variable configuration with no keys committed to the repository.
- Initial Supabase migration for `customer_profiles`, automatic profile creation, and row-level security policies.

## Database design

`auth.users` is owned by Supabase Auth. `public.customer_profiles` stores customer details and uses the auth user UUID as its primary key.

| Entity | Day 1 status | Purpose |
|---|---|---|
| `auth.users` | Supabase managed | Email, password, identity |
| `customer_profiles` | Implemented | Customer name, phone, and pickup-address defaults |
| `bookings` | Planned | Courier booking and lifecycle status |
| `parcels` | Planned | Parcel dimensions, weight, contents, value |
| `pickup_addresses` | Planned | Reusable customer pickup locations |
| `drivers` / `driver_assignments` | Planned | Pickup workforce and task assignment |
| `shipment_events` | Planned | Tracking timeline |
| `payments` | Planned | Payment state and gateway references |
| `documents` | Planned | KYC/customs documents in Supabase Storage |

## API contract

| Method | Endpoint | Function |
|---|---|---|
| POST | `/api/v1/auth/register` | Create a customer account |
| POST | `/api/v1/auth/login` | Start an authenticated session |
| GET | `/api/v1/customers/me` | Get the signed-in customer profile |
| PUT | `/api/v1/customers/me` | Update the signed-in customer profile |
| GET | `/health` | Check service availability |

## Required setup before integration testing

1. Create the Supabase project and execute `database/001_initial_schema.sql` in its SQL Editor.
2. Copy `backend/.env.example` to `backend/.env` and add the Supabase URL, anon key, and JWT secret.
3. Configure the frontend to send the Supabase access token as `Authorization: Bearer <token>`.

## Remaining Day 2 work

- Add booking, parcel, address, payment, tracking, and driver schemas/routes.
- Add formal integration tests against a non-production Supabase project.
- Define error-code conventions, logging, rate limits, and CI checks.
