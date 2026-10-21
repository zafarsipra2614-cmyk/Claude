# Flostocks Content Calendar

An open calendar of what goes out on each platform and when:
**https://zafarsipra2614-cmyk.github.io/Content-Calendar/**

- Each post has a date, an optional time, what's being posted, its platforms, and a status: **Pending**, **Scheduled** or **Uploaded**.
- Anyone with the link can view and edit. There are no logins or keys.
- Posts are saved in a free Supabase project and appear on everyone's screen as soon as someone saves.

## One-time database update

Run this once in your Supabase project. It opens the posts table to the calendar and adds the Pending status. It's safe to run again.

1. Open your project at <https://supabase.com/dashboard>.
2. In the left menu click **SQL Editor**, then **New query**.
3. Copy all of the SQL below (hover over the box and click the copy icon), paste it in, and click **Run**. If Supabase warns about a destructive operation, click **Run this query**: it only replaces access rules, not posts.

```sql
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
```

The same SQL is in [setup.sql](setup.sql).

## Turn on the site

1. In this repository open **Settings → Pages**.
2. Set **Source** to *Deploy from a branch*, choose **main** and **/ (root)**, and click **Save**.

## Good to know

- Because the portal is open, anyone who has the link can change or delete posts. Share it only with people you trust.
- The calendar only stores text, so it stays far within Supabase's free plan.
- Supabase pauses free projects after a week with no activity. Opening the calendar regularly prevents this; if it does pause, click **Restore project** in the Supabase dashboard. No posts are lost.

## Troubleshooting

| What you see | What to do |
| --- | --- |
| "The calendar's database isn't open for editing yet" | Run the SQL above. |
| "The Pending status needs the database update" | Run the SQL above. |
| "The calendar couldn't connect" | Check your internet connection and reload. |
