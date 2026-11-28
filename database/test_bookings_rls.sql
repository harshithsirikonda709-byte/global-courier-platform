-- Verification script for bookings schema & Row Level Security policies
-- Run in Supabase SQL Editor to verify:
-- 1. Cross-customer booking isolation (Customer B cannot view or update Customer A's bookings)
-- 2. Customer permitted column updates succeed
-- 3. Customer protected column updates FAIL with permission denied (status, driver, actual specs, pricing)
-- 4. Secure cancellation via cancel_customer_booking RPC
begin;

-- Create two temporary users
insert into auth.users (id, email, raw_user_meta_data) values
  ('a0ca0187-87ef-44a6-9761-546340000001', 'booking_user1@example.invalid', '{"full_name":"Customer One"}'),
  ('a0ca0187-87ef-44a6-9761-546340000002', 'booking_user2@example.invalid', '{"full_name":"Customer Two"}');

-- Create a driver user
insert into auth.users (id, email, raw_user_meta_data) values
  ('a0ca0187-87ef-44a6-9761-546340000003', 'driver_user@example.invalid', '{"full_name":"Pickup Driver"}');

-- Create a booking for Customer 1
insert into public.bookings (
  id, tracking_number, customer_id, status,
  pickup_name, pickup_phone, pickup_address_line_1, pickup_city, pickup_state, pickup_postal_code,
  receiver_name, receiver_phone, receiver_address_line_1, receiver_city, receiver_state, receiver_postal_code,
  parcel_category, length_cm, width_cm, height_cm, estimated_weight_kg, estimated_price
) values (
  'b0ca0187-87ef-44a6-9761-546340000001', 'GCP-TEST-000001', 'a0ca0187-87ef-44a6-9761-546340000001', 'PENDING_PICKUP',
  'Customer One', '+919876543210', '123 Main St', 'Hyderabad', 'Telangana', '500001',
  'Receiver One', '+919876543211', '456 Cross St', 'Bengaluru', 'Karnataka', '560001',
  'electronics', 30.0, 20.0, 15.0, 2.5, 450.00
);

-- =========================================================================
-- TEST 1: Cross-customer isolation (Customer 2 cannot see or update Customer 1)
-- =========================================================================
set local role authenticated;
select set_config('request.jwt.claim.sub', 'a0ca0187-87ef-44a6-9761-546340000002', true);

do $$
begin
  -- Customer 2 should NOT see Customer 1's booking
  if exists (select from public.bookings where id = 'b0ca0187-87ef-44a6-9761-546340000001') then
    raise exception 'SECURITY VIOLATION: Customer 2 can view Customer 1 booking';
  end if;

  -- Customer 2 should NOT be able to update Customer 1's booking
  update public.bookings
  set special_instructions = 'Attempted overwrite by Customer 2'
  where id = 'b0ca0187-87ef-44a6-9761-546340000001';

  if found then
    raise exception 'SECURITY VIOLATION: Customer 2 modified Customer 1 booking';
  end if;
end;
$$;

-- Test 1b: Customer 2 cannot cancel Customer 1's booking via RPC
do $$
declare
  v_caught boolean := false;
begin
  begin
    perform public.cancel_customer_booking('b0ca0187-87ef-44a6-9761-546340000001');
  exception when others then
    v_caught := true;
  end;

  if not v_caught then
    raise exception 'SECURITY VIOLATION: Customer 2 cancelled Customer 1 booking via RPC';
  end if;
end;
$$;

-- =========================================================================
-- TEST 2: Permitted column update (Customer 1 can update safe fields)
-- =========================================================================
select set_config('request.jwt.claim.sub', 'a0ca0187-87ef-44a6-9761-546340000001', true);

do $$
begin
  -- Customer 1 can see own booking
  if not exists (select from public.bookings where id = 'b0ca0187-87ef-44a6-9761-546340000001') then
    raise exception 'Customer 1 cannot view own booking';
  end if;

  -- Customer 1 can update permitted columns (pickup phone, special instructions)
  update public.bookings
  set special_instructions = 'Please call before arrival',
      pickup_phone = '+919876543299'
  where id = 'b0ca0187-87ef-44a6-9761-546340000001';

  if not found then
    raise exception 'Customer 1 permitted field update failed';
  end if;
end;
$$;

-- =========================================================================
-- TEST 3: Column security (Customer 1 CANNOT update protected columns)
-- =========================================================================

-- 3a. Direct 'status' update must be rejected with 42501 (insufficient privilege)
do $$
declare
  v_denied boolean := false;
begin
  begin
    update public.bookings
    set status = 'DELIVERED'
    where id = 'b0ca0187-87ef-44a6-9761-546340000001';
  exception when insufficient_privilege then
    v_denied := true;
  end;

  if not v_denied then
    raise exception 'SECURITY VIOLATION: Customer 1 directly updated status column';
  end if;
end;
$$;

-- 3b. Direct 'assigned_driver_id' update must be rejected
do $$
declare
  v_denied boolean := false;
begin
  begin
    update public.bookings
    set assigned_driver_id = 'a0ca0187-87ef-44a6-9761-546340000003'
    where id = 'b0ca0187-87ef-44a6-9761-546340000001';
  exception when insufficient_privilege then
    v_denied := true;
  end;

  if not v_denied then
    raise exception 'SECURITY VIOLATION: Customer 1 directly updated assigned_driver_id';
  end if;
end;
$$;

-- 3c. Direct 'actual_weight_kg' update must be rejected
do $$
declare
  v_denied boolean := false;
begin
  begin
    update public.bookings
    set actual_weight_kg = 1.00
    where id = 'b0ca0187-87ef-44a6-9761-546340000001';
  exception when insufficient_privilege then
    v_denied := true;
  end;

  if not v_denied then
    raise exception 'SECURITY VIOLATION: Customer 1 directly updated actual_weight_kg';
  end if;
end;
$$;

-- 3d. Direct 'packaging_status' update must be rejected
do $$
declare
  v_denied boolean := false;
begin
  begin
    update public.bookings
    set packaging_status = 'REPACKAGED'
    where id = 'b0ca0187-87ef-44a6-9761-546340000001';
  exception when insufficient_privilege then
    v_denied := true;
  end;

  if not v_denied then
    raise exception 'SECURITY VIOLATION: Customer 1 directly updated packaging_status';
  end if;
end;
$$;

-- 3e. Direct 'final_price' / 'estimated_price' update must be rejected
do $$
declare
  v_denied boolean := false;
begin
  begin
    update public.bookings
    set final_price = 10.00
    where id = 'b0ca0187-87ef-44a6-9761-546340000001';
  exception when insufficient_privilege then
    v_denied := true;
  end;

  if not v_denied then
    raise exception 'SECURITY VIOLATION: Customer 1 directly updated final_price';
  end if;
end;
$$;

-- =========================================================================
-- TEST 4: Authorized cancellation via cancel_customer_booking RPC
-- =========================================================================
do $$
declare
  v_res public.bookings;
begin
  v_res := public.cancel_customer_booking('b0ca0187-87ef-44a6-9761-546340000001');

  if v_res.status != 'CANCELLED' then
    raise exception 'cancel_customer_booking failed to set status to CANCELLED';
  end if;
end;
$$;

reset role;
rollback;

-- If script reaches here without exceptions, all security assertions passed!
select 'SUCCESS: All booking RLS and column-level permission checks passed.' as result;
