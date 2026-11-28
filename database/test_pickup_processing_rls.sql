-- Verification script for Day 4 Pickup Assignment, Parcel Inspection & Delivery Workflow
-- Run in Supabase SQL Editor
begin;

-- Create temporary admin, driver, and unassigned driver users
insert into auth.users (id, email, raw_user_meta_data) values
  ('d0ca0187-87ef-44a6-9761-546340000001', 'customer_day4@example.invalid', '{"full_name":"Customer Day 4"}'),
  ('d0ca0187-87ef-44a6-9761-546340000002', 'driver_assigned@example.invalid', '{"full_name":"Driver One"}'),
  ('d0ca0187-87ef-44a6-9761-546340000003', 'driver_unassigned@example.invalid', '{"full_name":"Driver Two"}');

-- Create a pending booking
insert into public.bookings (
  id, tracking_number, customer_id, status,
  pickup_name, pickup_phone, pickup_address_line_1, pickup_city, pickup_state, pickup_postal_code,
  receiver_name, receiver_phone, receiver_address_line_1, receiver_city, receiver_state, receiver_postal_code,
  parcel_category, length_cm, width_cm, height_cm, estimated_weight_kg, estimated_price
) values (
  'e0ca0187-87ef-44a6-9761-546340000001', 'GCP-DAY4-000001', 'd0ca0187-87ef-44a6-9761-546340000001', 'PENDING_PICKUP',
  'Customer Day 4', '+919876543210', '123 Main St', 'Hyderabad', 'Telangana', '500001',
  'Receiver Day 4', '+919876543211', '456 Cross St', 'Bengaluru', 'Karnataka', '560001',
  'electronics', 30.0, 20.0, 15.0, 2.5, 450.00
);

-- =========================================================================
-- TEST 1: Admin assigns pickup executive
-- =========================================================================
do $$
declare
  v_assigned public.bookings;
begin
  v_assigned := public.assign_pickup_executive(
    'e0ca0187-87ef-44a6-9761-546340000001',
    'd0ca0187-87ef-44a6-9761-546340000002'
  );

  if v_assigned.status != 'PICKUP_ASSIGNED' or v_assigned.assigned_driver_id != 'd0ca0187-87ef-44a6-9761-546340000002' then
    raise exception 'TEST 1 FAILED: Driver assignment failed';
  end if;
end;
$$;

-- =========================================================================
-- TEST 2: Driver RLS view policy
-- =========================================================================
set local role authenticated;

-- Impersonate Assigned Driver
select set_config('request.jwt.claim.sub', 'd0ca0187-87ef-44a6-9761-546340000002', true);

do $$
begin
  -- Assigned driver CAN view this booking
  if not exists (select from public.bookings where id = 'e0ca0187-87ef-44a6-9761-546340000001') then
    raise exception 'TEST 2 FAILED: Assigned driver cannot view assigned booking';
  end if;
end;
$$;

-- Impersonate Unassigned Driver
select set_config('request.jwt.claim.sub', 'd0ca0187-87ef-44a6-9761-546340000003', true);

do $$
begin
  -- Unassigned driver CANNOT view this booking
  if exists (select from public.bookings where id = 'e0ca0187-87ef-44a6-9761-546340000001') then
    raise exception 'TEST 2 FAILED: Unassigned driver can view booking';
  end if;
end;
$$;

-- =========================================================================
-- TEST 3: Unassigned driver CANNOT inspect parcel
-- =========================================================================
do $$
declare
  v_caught boolean := false;
begin
  begin
    perform public.inspect_parcel_and_pickup(
      'e0ca0187-87ef-44a6-9761-546340000001',
      'd0ca0187-87ef-44a6-9761-546340000003',
      2.80, 32.0, 22.0, 16.0, 'REPACKAGED', 510.00
    );
  exception when others then
    v_caught := true;
  end;

  if not v_caught then
    raise exception 'TEST 3 FAILED: Unassigned driver inspected parcel';
  end if;
end;
$$;

-- =========================================================================
-- TEST 4: Assigned driver records parcel inspection details
-- =========================================================================
select set_config('request.jwt.claim.sub', 'd0ca0187-87ef-44a6-9761-546340000002', true);

do $$
declare
  v_inspected public.bookings;
begin
  v_inspected := public.inspect_parcel_and_pickup(
    'e0ca0187-87ef-44a6-9761-546340000001',
    'd0ca0187-87ef-44a6-9761-546340000002',
    2.80, 32.0, 22.0, 16.0, 'REPACKAGED', 510.00, 'Carefully re-taped'
  );

  if v_inspected.status != 'PICKED_UP'
     or v_inspected.actual_weight_kg != 2.80
     or v_inspected.packaging_status != 'REPACKAGED'
     or v_inspected.final_price != 510.00 then
    raise exception 'TEST 4 FAILED: Parcel inspection values not recorded properly';
  end if;
end;
$$;

-- =========================================================================
-- TEST 5: Driver transitions status along delivery workflow
-- =========================================================================
do $$
declare
  v_booking public.bookings;
begin
  -- 5a: Transition to IN_TRANSIT
  v_booking := public.update_booking_workflow_status(
    'e0ca0187-87ef-44a6-9761-546340000001',
    'd0ca0187-87ef-44a6-9761-546340000002',
    'IN_TRANSIT'
  );
  if v_booking.status != 'IN_TRANSIT' then
    raise exception 'TEST 5a FAILED: Could not transition to IN_TRANSIT';
  end if;

  -- 5b: Transition to OUT_FOR_DELIVERY
  v_booking := public.update_booking_workflow_status(
    'e0ca0187-87ef-44a6-9761-546340000001',
    'd0ca0187-87ef-44a6-9761-546340000002',
    'OUT_FOR_DELIVERY'
  );
  if v_booking.status != 'OUT_FOR_DELIVERY' then
    raise exception 'TEST 5b FAILED: Could not transition to OUT_FOR_DELIVERY';
  end if;

  -- 5c: Transition to DELIVERED
  v_booking := public.update_booking_workflow_status(
    'e0ca0187-87ef-44a6-9761-546340000001',
    'd0ca0187-87ef-44a6-9761-546340000002',
    'DELIVERED'
  );
  if v_booking.status != 'DELIVERED' then
    raise exception 'TEST 5c FAILED: Could not transition to DELIVERED';
  end if;
end;
$$;

-- =========================================================================
-- TEST 6: Terminal status cannot be modified
-- =========================================================================
do $$
declare
  v_caught boolean := false;
begin
  begin
    perform public.update_booking_workflow_status(
      'e0ca0187-87ef-44a6-9761-546340000001',
      'd0ca0187-87ef-44a6-9761-546340000002',
      'PICKUP_ASSIGNED'
    );
  exception when others then
    v_caught := true;
  end;

  if not v_caught then
    raise exception 'TEST 6 FAILED: Allowed transition from terminal DELIVERED status';
  end if;
end;
$$;

reset role;
rollback;

select 'SUCCESS: All Day 4 pickup assignment, parcel inspection & workflow tests passed.' as result;
