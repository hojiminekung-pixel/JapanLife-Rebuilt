create or replace function public.legacy_get_account(p_game_id text, p_udid_hash text)
returns table(game_id text, status text, client_version text)
language sql
security definer
set search_path = public
as $$
  select a.game_id, a.status, a.client_version
  from public.legacy_game_accounts a
  where (p_game_id is not null and p_game_id <> '' and a.game_id = p_game_id)
     or (p_udid_hash is not null and p_udid_hash <> '' and a.udid_hash = p_udid_hash)
  limit 1
$$;

create or replace function public.legacy_upsert_account(
  p_game_id text,
  p_udid_hash text,
  p_password_hash text,
  p_client_version text
)
returns table(game_id text, status text, client_version text)
language plpgsql
security definer
set search_path = public
as $$
begin
  if coalesce(p_game_id,'') = '' then
    return;
  end if;

  insert into public.legacy_game_accounts(
    game_id,udid_hash,password_hash,client_version,status,last_login_at,updated_at
  )
  values(
    p_game_id,nullif(p_udid_hash,''),nullif(p_password_hash,''),
    nullif(p_client_version,''),'active',now(),now()
  )
  on conflict (game_id) do update set
    udid_hash=coalesce(excluded.udid_hash,legacy_game_accounts.udid_hash),
    password_hash=coalesce(excluded.password_hash,legacy_game_accounts.password_hash),
    client_version=coalesce(excluded.client_version,legacy_game_accounts.client_version),
    status='active',
    last_login_at=now(),
    updated_at=now();

  return query
    select a.game_id,a.status,a.client_version
    from public.legacy_game_accounts a
    where a.game_id=p_game_id;
end
$$;

grant execute on function public.legacy_get_account(text,text) to anon, authenticated;
grant execute on function public.legacy_upsert_account(text,text,text,text) to anon, authenticated;
