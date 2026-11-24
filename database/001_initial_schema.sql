-- Execute this in Supabase SQL Editor. auth.users is managed by Supabase Auth.
create table if not exists public.customer_profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  email text not null,
  full_name text not null,
  phone text,
  address_line_1 text,
  address_line_2 text,
  city text,
  state text,
  postal_code text,
  country text not null default 'India',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.customer_profiles enable row level security;

-- Keep the public profile in sync with each new Supabase Auth customer.
-- SECURITY DEFINER is required because the trigger writes across schemas.
create or replace function public.create_customer_profile()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.customer_profiles (user_id, email, full_name, phone)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data ->> 'full_name', split_part(new.email, '@', 1)),
    new.raw_user_meta_data ->> 'phone'
  );
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.create_customer_profile();

create policy "Customers read their own profile" on public.customer_profiles
  for select using (auth.uid() = user_id);
create policy "Customers create their own profile" on public.customer_profiles
  for insert with check (auth.uid() = user_id);
create policy "Customers update their own profile" on public.customer_profiles
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- Planned core entities: bookings, parcels, pickup_addresses, drivers,
-- driver_assignments, shipment_events, payments and documents.

