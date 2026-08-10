-- Groove Academy cloud sync: per-user lesson progress and run stats.
-- See openspec/changes/supabase-integration/design.md (Decision 3).

create table public.lesson_progress (
  user_id    uuid        not null references auth.users (id) on delete cascade,
  lesson_id  text        not null,
  max_bpm    integer     not null default 0,   -- the BPM ceiling
  tier       integer,                          -- selected rung
  unlocked   boolean     not null default false,-- lesson itself unlocked
  updated_at timestamptz not null default now(),
  primary key (user_id, lesson_id)
);

create table public.sessions (
  id          uuid        primary key,          -- client-generated dedup key
  user_id     uuid        not null references auth.users (id) on delete cascade,
  at          bigint      not null,             -- finish epoch ms
  day         text        not null,             -- local YYYY-MM-DD
  lesson      text        not null,
  lesson_name text,
  bpm         integer,
  device      text,
  device_id   text,
  stat        jsonb       not null,             -- full SessionStat payload
  created_at  timestamptz not null default now()
);

create index sessions_user_at_idx  on public.sessions (user_id, at);
create index sessions_user_day_idx on public.sessions (user_id, day);
