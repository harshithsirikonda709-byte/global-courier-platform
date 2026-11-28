-- Migration 003: Pickup Assignment, Parcel Inspection, & Status Transitions
-- Day 4: Administrative & Pickup Executive authorized operations
begin;

-- 1. Driver RLS Policy: Drivers can view bookings assigned to them
drop policy if exists "Drivers view assigned bookings" on public.bookings;
create policy "Drivers view assigned bookings" on public.bookings
  for select to authenticated
  using (auth.uid() = assigned_driver_id);

-- 2. RPC: Admin assigns pickup executive to a booking
create or replace function public.assign_pickup_executive(
  p_booking_id uuid,
  p_driver_id uuid
)
returns public.bookings
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_booking public.bookings;
begin
  update public.bookings
  set assigned_driver_id = p_driver_id,
      status = 'PICKUP_ASSIGNED',
      updated_at = now()
  where id = p_booking_id
    and status in ('PENDING_PICKUP', 'PICKUP_ASSIGNED')
  returning * into v_booking;

  if not found then
    raise exception 'Booking not found or cannot be assigned in its current status';
  end if;

  return v_booking;
end;
$$;

-- 3. RPC: Pickup executive records inspection details and marks parcel as PICKED_UP
create or replace function public.inspect_parcel_and_pickup(
  p_booking_id uuid,
  p_driver_id uuid,
  p_actual_weight numeric,
  p_actual_length numeric,
  p_actual_width numeric,
  p_actual_height numeric,
  p_packaging_status text,
  p_final_price numeric,
  p_special_instructions text default null
)
returns public.bookings
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_booking public.bookings;
begin
  -- Validate packaging status
  if p_packaging_status not in ('ORIGINAL', 'REPACKAGED', 'CUSTOM_CRATING', 'DAMAGED') then
    raise exception 'Invalid packaging status: %', p_packaging_status;
  end if;

  -- Validate measurements
  if p_actual_weight <= 0 or p_actual_length <= 0 or p_actual_width <= 0 or p_actual_height <= 0 then
    raise exception 'Actual weight and dimensions must be greater than zero';
  end if;

  update public.bookings
  set actual_weight_kg = p_actual_weight,
      actual_length_cm = p_actual_length,
      actual_width_cm = p_actual_width,
      actual_height_cm = p_actual_height,
      packaging_status = p_packaging_status,
      final_price = p_final_price,
      special_instructions = coalesce(p_special_instructions, special_instructions),
      status = 'PICKED_UP',
      updated_at = now()
  where id = p_booking_id
    and (assigned_driver_id = p_driver_id or auth.uid() = assigned_driver_id)
    and status = 'PICKUP_ASSIGNED'
  returning * into v_booking;

  if not found then
    raise exception 'Booking not found, not assigned to driver, or not in PICKUP_ASSIGNED status';
  end if;

  return v_booking;
end;
$$;

-- 4. RPC: Driver or Admin updates booking workflow status
create or replace function public.update_booking_workflow_status(
  p_booking_id uuid,
  p_driver_id uuid,
  p_new_status text
)
returns public.bookings
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_booking public.bookings;
  v_current_status text;
begin
  select status into v_current_status
  from public.bookings
  where id = p_booking_id and (assigned_driver_id = p_driver_id or auth.uid() = assigned_driver_id);

  if not found then
    raise exception 'Booking not found or not assigned to this driver';
  end if;

  -- Validate workflow state transitions
  if v_current_status = 'PICKED_UP' and p_new_status not in ('IN_TRANSIT', 'CANCELLED') then
    raise exception 'Cannot transition from PICKED_UP to %', p_new_status;
  elsif v_current_status = 'IN_TRANSIT' and p_new_status not in ('OUT_FOR_DELIVERY', 'CANCELLED') then
    raise exception 'Cannot transition from IN_TRANSIT to %', p_new_status;
  elsif v_current_status = 'OUT_FOR_DELIVERY' and p_new_status not in ('DELIVERED', 'CANCELLED') then
    raise exception 'Cannot transition from OUT_FOR_DELIVERY to %', p_new_status;
  elsif v_current_status in ('DELIVERED', 'CANCELLED') then
    raise exception 'Cannot modify terminal booking status %', v_current_status;
  end if;

  update public.bookings
  set status = p_new_status,
      updated_at = now()
  where id = p_booking_id
  returning * into v_booking;

  return v_booking;
end;
$$;

-- Grants
grant execute on function public.assign_pickup_executive(uuid, uuid) to authenticated, service_role;
grant execute on function public.inspect_parcel_and_pickup(uuid, uuid, numeric, numeric, numeric, numeric, text, numeric, text) to authenticated, service_role;
grant execute on function public.update_booking_workflow_status(uuid, uuid, text) to authenticated, service_role;

commit;
