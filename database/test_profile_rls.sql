-- Run after 001_initial_schema.sql on a disposable Supabase database.
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
