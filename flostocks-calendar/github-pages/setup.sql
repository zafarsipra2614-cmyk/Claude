-- Flostocks Content Calendar: open portal setup for Supabase.
-- Paste this whole file into Supabase → SQL Editor → New query, then click Run.
-- Safe to run more than once, and safe on a project that was set up before.

-- 1. Posts table
create table if not exists public.posts (
  id          uuid primary key default gen_random_uuid(),
  date        text not null,                       -- YYYY-MM-DD
  time        text not null default '',            -- HH:MM, optional
  title       text not null default '',
  platforms   text[] not null default '{}',
  status      text not null default 'scheduled',
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

-- 2. Allowed statuses: Pending, Scheduled, Uploaded.
alter table public.posts drop constraint if exists posts_status_check;
alter table public.posts add constraint posts_status_check check (status in ('pending', 'scheduled', 'uploaded'));

-- 3. Open portal: anyone with the calendar link can view, add, edit and delete posts.
alter table public.posts enable row level security;

drop policy if exists "team reads posts" on public.posts;
drop policy if exists "team adds posts" on public.posts;
drop policy if exists "team edits posts" on public.posts;
drop policy if exists "team deletes posts" on public.posts;
drop policy if exists "anyone reads posts" on public.posts;
drop policy if exists "anyone adds posts" on public.posts;
drop policy if exists "anyone edits posts" on public.posts;
drop policy if exists "anyone deletes posts" on public.posts;
create policy "anyone reads posts"   on public.posts for select to anon, authenticated using (true);
create policy "anyone adds posts"    on public.posts for insert to anon, authenticated with check (true);
create policy "anyone edits posts"   on public.posts for update to anon, authenticated using (true) with check (true);
create policy "anyone deletes posts" on public.posts for delete to anon, authenticated using (true);

-- 4. Live updates: changes appear for everyone without reloading.
do $$ begin
  alter publication supabase_realtime add table public.posts;
exception when duplicate_object then null; end $$;
