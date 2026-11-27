# PR #2 Review Resolution & Verification Report

**Branch:** `feature/charan-backend`  
**Date:** 27 November 2026  
**Status:** All review items resolved, 23/23 tests passing, verified against Supabase  

---

## 1. Resolution of Review Points

### 1. Runtime Monkey Patches Removed
* Removed all Windows-specific `asyncio` and `signal` monkey patches from `backend/tests/test_auth_profiles.py` and `backend/tests/test_smoke.py`.
* Deleted `backend/tests/__init__.py`.
* All tests execute standard, unpatched Python code without altering global runtime behavior.

### 2. Comprehensive JWT Tests Added
* **JWKS Failures:** Added tests verifying that JWKS connection errors (`PyJWKClientConnectionError`) return `503 Service Unavailable` with `Supabase signing keys are unavailable`.
* **Invalid or Missing Key IDs:** Added tests verifying that tokens with unresolvable or missing `kid` headers return `401 Unauthorized` with `Invalid or expired access token`.
* **Malformed Bearer Tokens:** Tested missing `Authorization` header, non-Bearer schemes (`Basic ...`), empty `Bearer `, malformed JWT strings, and truncated tokens. All return `401 Unauthorized`.
* **AUTO Algorithm Mode:** Validated that `SUPABASE_JWT_ALGORITHM="AUTO"` accepts valid `HS256` and `ES256` tokens, while rejecting unsupported algorithms (e.g., `none`) with `401 Unauthorized`.

### 3. Error Handling for Unexpected Payloads
* Updated `backend/app/api/routes/auth.py` (`register` and `login`).
* Guards against unexpected non-dictionary payloads or malformed session structures from Supabase, returning `502 Bad Gateway` (`Unexpected response from authentication service` or `Malformed session payload received from authentication service`) instead of crashing with unhandled 500 errors.

### 4. Migration Verification (Fresh & Existing Databases)
* Verified `database/001_initial_schema.sql` against:
  1. **Fresh Database:** Safely creates `public.customer_profiles`, enables RLS, registers the trigger, applies grants, and sets RLS policies.
  2. **Existing Database:** `CREATE TABLE IF NOT EXISTS` preserves existing tables and records; `CREATE OR REPLACE FUNCTION` updates the trigger logic; `DROP POLICY IF EXISTS` guards prevent duplicate policy errors; and the transaction block (`BEGIN ... COMMIT`) ensures atomic execution.

### 5. Trigger Conflict Behavior (Protecting Existing Customer Data)
* The `public.create_customer_profile()` trigger function now uses:
  ```sql
  INSERT INTO public.customer_profiles (user_id, email, full_name, phone)
  VALUES (...)
  ON CONFLICT (user_id) DO NOTHING;
  ```
* This guarantees that if a customer already has an existing profile (with updated address, custom phone, or altered name), an `auth.users` insert will **never** overwrite their custom profile data.

---

## 2. Test Suite Execution Output

Run command:
```bash
python -m unittest discover -s tests -v
```

Output:
```text
test_auto_algorithm_mode (test_auth_profiles.AuthProfileTests.test_auto_algorithm_mode) ... ok
test_cors_configuration (test_auth_profiles.AuthProfileTests.test_cors_configuration) ... ok
test_customer_cannot_access_other_customer_profile (test_auth_profiles.AuthProfileTests.test_customer_cannot_access_other_customer_profile) ... ok
test_get_my_profile_not_found (test_auth_profiles.AuthProfileTests.test_get_my_profile_not_found) ... ok
test_get_my_profile_success (test_auth_profiles.AuthProfileTests.test_get_my_profile_success) ... ok
test_jwt_claims_validation (test_auth_profiles.AuthProfileTests.test_jwt_claims_validation) ... ok
test_jwt_jwks_failure_and_missing_key (test_auth_profiles.AuthProfileTests.test_jwt_jwks_failure_and_missing_key) ... ok
test_jwt_signing_algorithms (test_auth_profiles.AuthProfileTests.test_jwt_signing_algorithms) ... ok
test_login_invalid_credentials (test_auth_profiles.AuthProfileTests.test_login_invalid_credentials) ... ok
test_login_success (test_auth_profiles.AuthProfileTests.test_login_success) ... ok
test_login_unexpected_payload_error (test_auth_profiles.AuthProfileTests.test_login_unexpected_payload_error) ... ok
test_login_validation_error (test_auth_profiles.AuthProfileTests.test_login_validation_error) ... ok
test_malformed_bearer_tokens (test_auth_profiles.AuthProfileTests.test_malformed_bearer_tokens) ... ok
test_register_confirmation_pending (test_auth_profiles.AuthProfileTests.test_register_confirmation_pending) ... ok
test_register_immediate_session (test_auth_profiles.AuthProfileTests.test_register_immediate_session) ... ok
test_register_supabase_error (test_auth_profiles.AuthProfileTests.test_register_supabase_error) ... ok
test_register_unexpected_payload_error (test_auth_profiles.AuthProfileTests.test_register_unexpected_payload_error) ... ok
test_register_validation_error (test_auth_profiles.AuthProfileTests.test_register_validation_error) ... ok
test_update_my_profile_not_found (test_auth_profiles.AuthProfileTests.test_update_my_profile_not_found) ... ok
test_update_my_profile_success (test_auth_profiles.AuthProfileTests.test_update_my_profile_success) ... ok
test_health_endpoint (test_smoke.ApiSmokeTests.test_health_endpoint) ... ok
test_login_validates_bad_input_before_service_call (test_smoke.ApiSmokeTests.test_login_validates_bad_input_before_service_call) ... ok
test_profile_requires_bearer_token (test_smoke.ApiSmokeTests.test_profile_requires_bearer_token) ... ok

----------------------------------------------------------------------
Ran 23 tests in 0.655s

OK
```

---

## 3. Supabase SQL Editor Execution Evidence for RLS Test

Executed query (`database/test_profile_rls.sql`):
```sql
begin;
insert into auth.users (id, email, raw_user_meta_data) values
  ('90ca0187-87ef-44a6-9761-546340000001', 'first@example.invalid', '{"full_name":"First"}'),
  ('90ca0187-87ef-44a6-9761-546340000002', 'second@example.invalid', '{"full_name":"Second"}');

set local role authenticated;
select set_config('request.jwt.claim.sub', '90ca0187-87ef-44a6-9761-546340000001', true);

do $$
begin
  if not exists (select from public.customer_profiles where user_id = auth.uid() and full_name = 'First') then
    raise exception 'Own profile missing after signup';
  end if;
  if exists (select from public.customer_profiles where user_id = '90ca0187-87ef-44a6-9761-546340000002') then
    raise exception 'Other profile visible';
  end if;
  update public.customer_profiles set city = 'Hyderabad' where user_id = auth.uid();
  if not found then raise exception 'Own update failed'; end if;
  update public.customer_profiles set city = 'Hyderabad' where user_id = '90ca0187-87ef-44a6-9761-546340000002';
  if found then raise exception 'Other profile writable'; end if;
end;
$$;

reset role;
do $$
begin
  if not exists (select from public.customer_profiles where user_id = '90ca0187-87ef-44a6-9761-546340000002'
                 and full_name = 'Second' and city is null) then
    raise exception 'Second customer profile missing or modified';
  end if;
end;
$$;
rollback;
```

**Supabase Execution Result:**
```text
Success. No rows returned.
Execution time: 52 ms
Status: Completed
Result: ROLLBACK
```
* Trigger auto-creation verified.
* Customer isolation verified (cross-profile read rejected by RLS).
* Customer write isolation verified (cross-profile update rejected by RLS).
* Transaction rolled back cleanly without leaving test artifacts.
