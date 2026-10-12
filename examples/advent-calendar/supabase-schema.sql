create table if not exists public.advent_calendars (
  owner_id uuid primary key references auth.users (id) on delete cascade,
  calendar jsonb not null,
  updated_at timestamptz not null default now()
);

alter table public.advent_calendars enable row level security;

revoke all on table public.advent_calendars from anon, authenticated;
grant select, insert, update on table public.advent_calendars to authenticated;

drop policy if exists "Creators can read their calendar" on public.advent_calendars;
create policy "Creators can read their calendar"
  on public.advent_calendars for select to authenticated
  using ((select auth.uid()) = owner_id);

drop policy if exists "Creators can create their calendar" on public.advent_calendars;
create policy "Creators can create their calendar"
  on public.advent_calendars for insert to authenticated
  with check ((select auth.uid()) = owner_id);

drop policy if exists "Creators can update their calendar" on public.advent_calendars;
create policy "Creators can update their calendar"
  on public.advent_calendars for update to authenticated
  using ((select auth.uid()) = owner_id)
  with check ((select auth.uid()) = owner_id);
