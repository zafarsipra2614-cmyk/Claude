-- Flostocks Content Calendar: one-time Supabase setup.
-- Paste this whole file into Supabase → SQL Editor → New query, then click Run.

-- 1. Posts table
create table if not exists public.posts (
  id          uuid primary key default gen_random_uuid(),
  date        text not null,                       -- YYYY-MM-DD
  time        text not null default '',            -- HH:MM, optional
  title       text not null default '',
  caption     text not null default '',
  platforms   text[] not null default '{}',
  status      text not null default 'scheduled' check (status in ('scheduled', 'uploaded')),
  media       jsonb not null default '[]',         -- [{path, name, type, size}]
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

-- Only signed-in team members can read or change posts.
alter table public.posts enable row level security;

drop policy if exists "team reads posts" on public.posts;
drop policy if exists "team adds posts" on public.posts;
drop policy if exists "team edits posts" on public.posts;
drop policy if exists "team deletes posts" on public.posts;
create policy "team reads posts"   on public.posts for select to authenticated using (true);
create policy "team adds posts"    on public.posts for insert to authenticated with check (true);
create policy "team edits posts"   on public.posts for update to authenticated using (true) with check (true);
create policy "team deletes posts" on public.posts for delete to authenticated using (true);

-- Live updates: changes appear for everyone without reloading.
do $$ begin
  alter publication supabase_realtime add table public.posts;
exception when duplicate_object then null; end $$;

-- 2. Private file storage for the content (50 MB per file on the free plan)
insert into storage.buckets (id, name, public, file_size_limit)
values ('content', 'content', false, 52428800)
on conflict (id) do nothing;

drop policy if exists "team reads content" on storage.objects;
drop policy if exists "team uploads content" on storage.objects;
drop policy if exists "team updates content" on storage.objects;
drop policy if exists "team deletes content" on storage.objects;
create policy "team reads content"   on storage.objects for select to authenticated using (bucket_id = 'content');
create policy "team uploads content" on storage.objects for insert to authenticated with check (bucket_id = 'content');
create policy "team updates content" on storage.objects for update to authenticated using (bucket_id = 'content');
create policy "team deletes content" on storage.objects for delete to authenticated using (bucket_id = 'content');
