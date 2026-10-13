create table if not exists public.advent_creator_calendars (
  owner_id uuid not null references auth.users (id) on delete cascade,
  calendar_id uuid not null default gen_random_uuid(),
  calendar jsonb not null,
  updated_at timestamptz not null default now(),
  primary key (owner_id, calendar_id)
);

do $migration$
begin
  if to_regclass('public.advent_calendars') is not null then
    execute $copy$
      insert into public.advent_creator_calendars (owner_id, calendar, updated_at)
      select legacy.owner_id, legacy.calendar, legacy.updated_at
      from public.advent_calendars as legacy
      where not exists (
        select 1
        from public.advent_creator_calendars as existing_calendar
        where existing_calendar.owner_id = legacy.owner_id
      )
    $copy$;
  end if;
end
$migration$;

alter table public.advent_creator_calendars enable row level security;

revoke all on table public.advent_creator_calendars from anon, authenticated;
grant select, insert, update, delete on table public.advent_creator_calendars to authenticated;

drop policy if exists "Creators can read their calendars" on public.advent_creator_calendars;
create policy "Creators can read their calendars"
  on public.advent_creator_calendars for select to authenticated
  using ((select auth.uid()) = owner_id);

drop policy if exists "Creators can create their calendars" on public.advent_creator_calendars;
create policy "Creators can create their calendars"
  on public.advent_creator_calendars for insert to authenticated
  with check ((select auth.uid()) = owner_id);

drop policy if exists "Creators can update their calendars" on public.advent_creator_calendars;
create policy "Creators can update their calendars"
  on public.advent_creator_calendars for update to authenticated
  using ((select auth.uid()) = owner_id)
  with check ((select auth.uid()) = owner_id);

drop policy if exists "Creators can delete their calendars" on public.advent_creator_calendars;
create policy "Creators can delete their calendars"
  on public.advent_creator_calendars for delete to authenticated
  using ((select auth.uid()) = owner_id);
