-- Owner-scoped RLS for cloud sync (design.md Decision 2 + spec cloud-sync).
-- Every row is scoped to auth.uid(); no anon policy, so anon sees no rows.

alter table public.lesson_progress enable row level security;
alter table public.sessions        enable row level security;

-- PostgREST needs table-level grants in addition to RLS. Authenticated only.
grant select, insert, update on public.lesson_progress to authenticated;
grant select, insert         on public.sessions        to authenticated;

-- lesson_progress: owner may read, create, and update their own rows (upsert).
create policy "progress_select_own" on public.lesson_progress
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "progress_insert_own" on public.lesson_progress
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy "progress_update_own" on public.lesson_progress
  for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

-- sessions: append-only. Owner may read and insert; no update/delete policy.
create policy "sessions_select_own" on public.sessions
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "sessions_insert_own" on public.sessions
  for insert to authenticated
  with check ((select auth.uid()) = user_id);
