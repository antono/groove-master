# Supabase setup (cloud sync)

The schema and RLS are applied by the migrations in `supabase/migrations/`. A few
things live in the Supabase dashboard / Management API and can't be scripted from
the repo — do these once per project.

## 1. Environment variables

`.env` (local, gitignored) and the Vercel project must both set:

```
PUBLIC_SUPABASE_URL=https://dbfmnbnjjjmbywbeuqts.supabase.co
PUBLIC_SUPABASE_ANON_KEY=sb_publishable_…   # the publishable key (browser-safe)
```

`.env.example` documents the shape. Auth is optional — with these unset the app
still builds and runs, entirely device-local (`supabaseConfigured` is false).

## 2. Auth → URL Configuration (required for magic links)

Dashboard → **Authentication → URL Configuration**:

- **Site URL**: the production origin (e.g. `https://groove.academy`).
- **Redirect URLs** — allowlist every origin the magic link may return to:
  - `http://localhost:5173/auth/confirm` (dev)
  - `http://localhost:4173/auth/confirm` (preview)
  - `https://<your-vercel-domain>/auth/confirm`
  - `https://groove.academy/auth/confirm`

The sign-in flow calls `signInWithOtp({ emailRedirectTo: <origin>/auth/confirm })`;
`/auth/confirm` (`src/routes/auth/confirm/+server.ts`) accepts either a PKCE
`?code=` (default email template) or a `?token_hash=&type=` link.

## 3. Email template (optional)

The default "Magic Link" template works as-is with the PKCE `code` flow. If you
prefer the `token_hash` flow, set the link to
`{{ .SiteURL }}/auth/confirm?token_hash={{ .TokenHash }}&type=email` — the confirm
route handles both.

## 4. Pre-existing advisor (unrelated to this change)

`get_advisors(security)` flags `public.rls_auto_enable()` — a `SECURITY DEFINER`
function callable by `anon`/`authenticated` that predates this work. Review and
revoke/relocate it if it isn't intentional:
https://supabase.com/docs/guides/database/database-linter?lint=0028_anon_security_definer_function_executable
