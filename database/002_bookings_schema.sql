-- Migration 002: Courier Bookings Schema & Row Level Security
-- Compatible with PostgreSQL / Supabase
begin;

create table if not exists public.bookings (
  id uuid primary key default gen_random_uuid(),
  tracking_number text not null unique,
  customer_id uuid not null references auth.users(id) on delete cascade,
  status text not null default 'PENDING_PICKUP' check (
    status in ('PENDING_PICKUP', 'PICKUP_ASSIGNED', 'PICKED_UP', 'IN_TRANSIT', 'OUT_FOR_DELIVERY', 'DELIVERED', 'CANCELLED')
  ),

  -- Pickup details
  pickup_name text not null,
  pickup_phone text not null,
  pickup_address_line_1 text not null,
  pickup_address_line_2 text,
  pickup_city text not null,
  pickup_state text not null,
  pickup_postal_code text not null,
  pickup_country text not null default 'India',
  pickup_date date,
  pickup_time_slot text,

  -- Receiver details
  receiver_name text not null,
  receiver_phone text not null,
  receiver_email text,
  receiver_address_line_1 text not null,
  receiver_address_line_2 text,
  receiver_city text not null,
  receiver_state text not null,
  receiver_postal_code text not null,
  receiver_country text not null default 'India',

  -- Parcel details
  parcel_category text not null check (
    parcel_category in ('document', 'electronics', 'clothing', 'fragile', 'perishable', 'general')
  ),
  parcel_description text,
  length_cm numeric(8, 2) not null check (length_cm > 0),
  width_cm numeric(8, 2) not null check (width_cm > 0),
  height_cm numeric(8, 2) not null check (height_cm > 0),
  estimated_weight_kg numeric(8, 2) not null check (estimated_weight_kg > 0),

  -- Pickup assignment, inspection and pricing (Day 4 fields)
  assigned_driver_id uuid references auth.users(id) on delete set null,
  actual_weight_kg numeric(8, 2) check (actual_weight_kg is null or actual_weight_kg > 0),
  actual_length_cm numeric(8, 2) check (actual_length_cm is null or actual_length_cm > 0),
  actual_width_cm numeric(8, 2) check (actual_width_cm is null or actual_width_cm > 0),
  actual_height_cm numeric(8, 2) check (actual_height_cm is null or actual_height_cm > 0),
  packaging_status text check (
    packaging_status is null or packaging_status in ('ORIGINAL', 'REPACKAGED', 'CUSTOM_CRATING', 'DAMAGED')
  ),
  estimated_price numeric(10, 2) check (estimated_price is null or estimated_price >= 0),
  final_price numeric(10, 2) check (final_price is null or final_price >= 0),
  special_instructions text,

  -- Timestamps
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Indexes for performant filtering and queries
create index if not exists idx_bookings_customer_id on public.bookings(customer_id);
create index if not exists idx_bookings_status on public.bookings(status);
create index if not exists idx_bookings_tracking_number on public.bookings(tracking_number);
create index if not exists idx_bookings_created_at on public.bookings(created_at desc);

-- Enable Row Level Security
alter table public.bookings enable row level security;

-- RLS Policies
drop policy if exists "Customers view their own bookings" on public.bookings;
drop policy if exists "Customers create their own bookings" on public.bookings;
drop policy if exists "Customers update their own bookings" on public.bookings;

-- 1. Customers can only view their own bookings
create policy "Customers view their own bookings" on public.bookings
  for select to authenticated using (auth.uid() = customer_id);

-- 2. Customers can only insert bookings belonging to themselves
create policy "Customers create their own bookings" on public.bookings
  for insert to authenticated with check (auth.uid() = customer_id);

-- 3. Customers can only update their own bookings
create policy "Customers update their own bookings" on public.bookings
  for update to authenticated using (auth.uid() = customer_id) with check (auth.uid() = customer_id);

-- Access grants
revoke all on public.bookings from public, anon;
grant select, insert, update on public.bookings to authenticated;

commit;
