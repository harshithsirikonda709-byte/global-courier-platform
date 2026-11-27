-- Execute this in Supabase SQL Editor. auth.users is managed by Supabase Auth.
begin;

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
-- Uses ON CONFLICT (user_id) DO NOTHING to ensure existing profile records are never overwritten.
create or replace function public.create_customer_profile()
returns trigger
language plpgsql
security definer set search_path = ''
as $$
begin
  insert into public.customer_profiles (user_id, email, full_name, phone)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data ->> 'full_name', split_part(new.email, '@', 1)),
    new.raw_user_meta_data ->> 'phone'
  )
  on conflict (user_id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row when (new.email is not null) execute procedure public.create_customer_profile();

-- Backfill any existing auth users without profile records.
-- ON CONFLICT (user_id) DO NOTHING prevents overwriting existing customer profiles.
insert into public.customer_profiles (user_id, email, full_name, phone)
select id, email, coalesce(raw_user_meta_data ->> 'full_name', split_part(email, '@', 1)),
       raw_user_meta_data ->> 'phone'
from auth.users where email is not null
on conflict (user_id) do nothing;

revoke all on public.customer_profiles from public, anon, authenticated;
grant select on public.customer_profiles to authenticated;
grant update (full_name, phone, address_line_1, address_line_2, city, state, postal_code, country)
  on public.customer_profiles to authenticated;
revoke all on function public.create_customer_profile() from public, anon, authenticated;

drop policy if exists "Customers read their own profile" on public.customer_profiles;
drop policy if exists "Customers create their own profile" on public.customer_profiles;
drop policy if exists "Customers update their own profile" on public.customer_profiles;

create policy "Customers read their own profile" on public.customer_profiles
  for select to authenticated using (auth.uid() = user_id);
create policy "Customers update their own profile" on public.customer_profiles
  for update to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

commit;
