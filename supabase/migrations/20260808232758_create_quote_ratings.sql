-- Quote of the Day: per-user like/dislike of a quote.
-- See openspec/changes/quote-of-the-day/design.md (Decisions 4 & 5).
--
-- One current rating per (user, quote); a rating can change, so unlike
-- lesson_progress (monotonic) and sessions (append-only) the merge is
-- last-write-wins by updated_at. Owner-scoped like the other tables.

create table public.quote_ratings (
  user_id    uuid        not null references auth.users (id) on delete cascade,
  quote_id   text        not null,             -- stable id from quotes.json
  value      text        not null check (value in ('like', 'dislike')),
  updated_at timestamptz not null default now(),
  primary key (user_id, quote_id)              -- leads with user_id for RLS reads
);

alter table public.quote_ratings enable row level security;

-- PostgREST needs table-level grants alongside RLS. Authenticated only.
grant select, insert, update on public.quote_ratings to authenticated;

-- Owner may read, create, and update (upsert) their own ratings; no anon
-- policy, so anon sees and writes nothing. auth.uid() wrapped in a subselect
-- so it is evaluated once per query, not once per row.
create policy "quote_ratings_select_own" on public.quote_ratings
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy "quote_ratings_insert_own" on public.quote_ratings
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy "quote_ratings_update_own" on public.quote_ratings
  for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);
