# DAY 3 API DOCUMENTATION & COMPLETION REPORT – Courier Booking Backend

**Date:** 27 November 2026  
**Developer:** Charan Teja  
**Project:** Global Courier Platform  
**Branch:** `feature/charan-backend`  
**Status:** **100% COMPLETE & TESTED (33/33 Tests Passing)**  

---

## 1. Overview & Completed Objectives

Day 3 introduces the core courier booking engine for customers:

1. **Courier Booking Database Schema (`database/002_bookings_schema.sql`)**:
   - `public.bookings` table with foreign key to `auth.users(id)` ON DELETE CASCADE.
   - Comprehensive pickup, receiver, and parcel attributes.
   - Pre-configured columns for Day 4 pickup assignment, parcel inspection, and pricing.
   - PostgreSQL Row Level Security (RLS) enforcing customer booking isolation.
2. **Customer Booking APIs**:
   - `POST /api/v1/bookings`: Create courier booking with auto-generated tracking number (`GCP-YYYYMMDD-XXXX`).
   - `GET /api/v1/bookings`: List bookings for the authenticated customer (with optional `status` filter).
   - `GET /api/v1/bookings/{booking_id}`: Retrieve booking details.
   - `POST /api/v1/bookings/{booking_id}/cancel`: Customer cancellation workflow (only allowed when `PENDING_PICKUP`).
3. **Validation & Error Handling**:
   - Dimensions (`length_cm`, `width_cm`, `height_cm`) and `estimated_weight_kg` must be strictly positive numbers.
   - Phone numbers, addresses, and recipient contacts validated.
   - Parcel categories constrained to: `document`, `electronics`, `clothing`, `fragile`, `perishable`, `general`.
4. **Security & Customer Isolation**:
   - Customer identity is extracted strictly from the validated JWT `sub` claim.
   - Customers can neither view nor mutate other customers' bookings.

---

## 2. API Contract & Sample Requests / Responses

**Base URL:** `http://localhost:8000/api/v1`  
**Authentication:** `Authorization: Bearer <access_token>`

### A. Create a Booking

* **Method / Endpoint:** `POST /api/v1/bookings`
* **Status Code:** `201 Created`
* **Request Body:**
  ```json
  {
    "pickup": {
      "name": "Charan Teja",
      "phone": "+919876543210",
      "address_line_1": "123 Jubilee Hills",
      "address_line_2": "Floor 2",
      "city": "Hyderabad",
      "state": "Telangana",
      "postal_code": "500033",
      "country": "India",
      "pickup_date": "2026-11-28",
      "pickup_time_slot": "09:00 - 12:00"
    },
    "receiver": {
      "name": "Uma Sharma",
      "phone": "+919876543211",
      "email": "uma@example.com",
      "address_line_1": "456 Indiranagar",
      "address_line_2": null,
      "city": "Bengaluru",
      "state": "Karnataka",
      "postal_code": "560038",
      "country": "India"
    },
    "parcel": {
      "category": "electronics",
      "description": "Laptop and accessories",
      "length_cm": 35.0,
      "width_cm": 25.0,
      "height_cm": 10.0,
      "estimated_weight_kg": 2.5
    },
    "special_instructions": "Handle with care, fragile electronic equipment"
  }
  ```
* **Success Response (`201 Created`):**
  ```json
  {
    "id": "b1ca0187-87ef-44a6-9761-546340000001",
    "tracking_number": "GCP-20261127-A9B8C7",
    "customer_id": "d4ac61ee-a041-4dd0-9ca1-047200f380de",
    "status": "PENDING_PICKUP",
    "pickup": {
      "name": "Charan Teja",
      "phone": "+919876543210",
      "address_line_1": "123 Jubilee Hills",
      "address_line_2": "Floor 2",
      "city": "Hyderabad",
      "state": "Telangana",
      "postal_code": "500033",
      "country": "India",
      "pickup_date": "2026-11-28",
      "pickup_time_slot": "09:00 - 12:00"
    },
    "receiver": {
      "name": "Uma Sharma",
      "phone": "+919876543211",
      "email": "uma@example.com",
      "address_line_1": "456 Indiranagar",
      "address_line_2": null,
      "city": "Bengaluru",
      "state": "Karnataka",
      "postal_code": "560038",
      "country": "India"
    },
    "parcel": {
      "category": "electronics",
      "description": "Laptop and accessories",
      "length_cm": 35.0,
      "width_cm": 25.0,
      "height_cm": 10.0,
      "estimated_weight_kg": 2.5
    },
    "special_instructions": "Handle with care, fragile electronic equipment",
    "assigned_driver_id": null,
    "actual_weight_kg": null,
    "actual_length_cm": null,
    "actual_width_cm": null,
    "actual_height_cm": null,
    "packaging_status": null,
    "estimated_price": null,
    "final_price": null,
    "created_at": "2026-11-27T12:50:00Z",
    "updated_at": "2026-11-27T12:50:00Z"
  }
  ```

---

### B. List My Bookings

* **Method / Endpoint:** `GET /api/v1/bookings`
* **Query Parameters (Optional):**
  * `status`: Filter by booking status (`PENDING_PICKUP`, `PICKUP_ASSIGNED`, `IN_TRANSIT`, etc.)
* **Status Code:** `200 OK`
* **Success Response:**
  ```json
  {
    "items": [
      {
        "id": "b1ca0187-87ef-44a6-9761-546340000001",
        "tracking_number": "GCP-20261127-A9B8C7",
        "customer_id": "d4ac61ee-a041-4dd0-9ca1-047200f380de",
        "status": "PENDING_PICKUP",
        "pickup": { ... },
        "receiver": { ... },
        "parcel": { ... },
        "created_at": "2026-11-27T12:50:00Z",
        "updated_at": "2026-11-27T12:50:00Z"
      }
    ],
    "total": 1
  }
  ```

---

### C. Get Booking by ID

* **Method / Endpoint:** `GET /api/v1/bookings/{booking_id}`
* **Status Code:** `200 OK` (or `404 Not Found` if not owned by caller)
* **Success Response:** Full `BookingResponse` object.

---

### D. Cancel a Booking

* **Method / Endpoint:** `POST /api/v1/bookings/{booking_id}/cancel`
* **Status Code:** `200 OK` (or `400 Bad Request` if already picked up / in transit)
* **Success Response:**
  ```json
  {
    "id": "b1ca0187-87ef-44a6-9761-546340000001",
    "tracking_number": "GCP-20261127-A9B8C7",
    "status": "CANCELLED",
    "message": "Booking cancelled successfully"
  }
  ```

---

## 3. Test Suite Execution Output

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
test_bookings_unauthenticated (test_bookings.BookingTests.test_bookings_unauthenticated) ... ok
test_cancel_booking_already_in_transit (test_bookings.BookingTests.test_cancel_booking_already_in_transit) ... ok
test_cancel_booking_success (test_bookings.BookingTests.test_cancel_booking_success) ... ok
test_create_booking_success (test_bookings.BookingTests.test_create_booking_success) ... ok
test_create_booking_validation_error (test_bookings.BookingTests.test_create_booking_validation_error) ... ok
test_customer_cannot_access_other_customer_booking (test_bookings.BookingTests.test_customer_cannot_access_other_customer_booking) ... ok
test_get_booking_by_id_not_found (test_bookings.BookingTests.test_get_booking_by_id_not_found) ... ok
test_get_booking_by_id_success (test_bookings.BookingTests.test_get_booking_by_id_success) ... ok
test_list_my_bookings_success (test_bookings.BookingTests.test_list_my_bookings_success) ... ok
test_list_my_bookings_with_status_filter (test_bookings.BookingTests.test_list_my_bookings_with_status_filter) ... ok
test_health_endpoint (test_smoke.ApiSmokeTests.test_health_endpoint) ... ok
test_login_validates_bad_input_before_service_call (test_smoke.ApiSmokeTests.test_login_validates_bad_input_before_service_call) ... ok
test_profile_requires_bearer_token (test_smoke.ApiSmokeTests.test_profile_requires_bearer_token) ... ok

----------------------------------------------------------------------
Ran 33 tests in 2.033s

OK
```
