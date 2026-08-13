-- Submitted controller layouts for kits we don't yet ship a profile for.
-- See openspec/changes/edrum-support/design.md (Decision 9).
--
-- A write-only mailbox, not a catalogue. Clients may insert and nothing else:
-- there is no select policy for anon or authenticated, so nobody can read the
-- table back through PostgREST — including the submitter, and including their
-- own rows. Only the service role sees it, and a shipped profile is authored
-- from a row by hand rather than read back into the app.
--
-- Anonymous insert is deliberate. The people most likely to own an
-- unrecognised kit are the least likely to have made an account first, and
-- requiring sign-in would cost us most of the layouts we want.

create table public.device_layouts (
  id          uuid        primary key default gen_random_uuid(),
  -- null for a signed-out submitter; defaulted rather than client-supplied so
  -- it cannot be spoofed, and set null on delete so a departing user's
  -- contribution survives without pointing at them.
  user_id     uuid        references auth.users (id) on delete set null
                          default auth.uid(),
  device_name text        not null check (length(device_name) between 1 and 120),
  -- pads, roles, notes, sounds and the hi-hat classification. Bounded so a
  -- malformed or abusive insert is rejected here rather than stored.
  layout      jsonb       not null check (length(layout::text) <= 8192),
  created_at  timestamptz not null default now()
);

alter table public.device_layouts enable row level security;

-- PostgREST needs table-level grants alongside RLS. Insert only, and only the
-- two columns a submission carries: id, user_id and created_at are all defaulted.
grant insert (device_name, layout) on public.device_layouts to anon, authenticated;

-- The only policy on the table. No select, update or delete for either role,
-- so the grant above is the whole of what a client can do.
create policy "device_layouts_insert" on public.device_layouts
  for insert to anon, authenticated
  with check (user_id is null or user_id = (select auth.uid()));
