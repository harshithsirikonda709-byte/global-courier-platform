-- Verification script for bookings schema & Row Level Security policies
-- Run in Supabase SQL Editor to verify cross-customer booking isolation
begin;

-- Create two temporary users
insert into auth.users (id, email, raw_user_meta_data) values
  ('a0ca0187-87ef-44a6-9761-546340000001', 'booking_user1@example.invalid', '{"full_name":"Customer One"}'),
  ('a0ca0187-87ef-44a6-9761-546340000002', 'booking_user2@example.invalid', '{"full_name":"Customer Two"}');

-- Create a booking for Customer 1
insert into public.bookings (
  id, tracking_number, customer_id, status,
  pickup_name, pickup_phone, pickup_address_line_1, pickup_city, pickup_state, pickup_postal_code,
  receiver_name, receiver_phone, receiver_address_line_1, receiver_city, receiver_state, receiver_postal_code,
  parcel_category, length_cm, width_cm, height_cm, estimated_weight_kg
) values (
  'b0ca0187-87ef-44a6-9761-546340000001', 'GCP-TEST-000001', 'a0ca0187-87ef-44a6-9761-546340000001', 'PENDING_PICKUP',
  'Customer One', '+919876543210', '123 Main St', 'Hyderabad', 'Telangana', '500001',
  'Receiver One', '+919876543211', '456 Cross St', 'Bengaluru', 'Karnataka', '560001',
  'electronics', 30.0, 20.0, 15.0, 2.5
);

-- Test 1: Impersonate Customer 2 (who did not create the booking)
set local role authenticated;
select set_config('request.jwt.claim.sub', 'a0ca0187-87ef-44a6-9761-546340000002', true);

do $$
begin
  -- Customer 2 should NOT be able to see Customer 1's booking
  if exists (select from public.bookings where id = 'b0ca0187-87ef-44a6-9761-546340000001') then
    raise exception 'SECURITY VIOLATION: Customer 2 can view Customer 1 booking';
  end if;

  -- Customer 2 should NOT be able to update Customer 1's booking
  update public.bookings set status = 'CANCELLED' where id = 'b0ca0187-87ef-44a6-9761-546340000001';
  if found then
    raise exception 'SECURITY VIOLATION: Customer 2 modified Customer 1 booking';
  end if;
end;
$$;

-- Test 2: Impersonate Customer 1 (owner of the booking)
select set_config('request.jwt.claim.sub', 'a0ca0187-87ef-44a6-9761-546340000001', true);

do $$
begin
  -- Customer 1 CAN see their own booking
  if not exists (select from public.bookings where id = 'b0ca0187-87ef-44a6-9761-546340000001') then
    raise exception 'Customer 1 cannot view own booking';
  end if;

  -- Customer 1 CAN update their own booking (e.g. cancel before pickup)
  update public.bookings set status = 'CANCELLED' where id = 'b0ca0187-87ef-44a6-9761-546340000001';
  if not found then
    raise exception 'Customer 1 update failed';
  end if;
end;
$$;

reset role;
rollback;
