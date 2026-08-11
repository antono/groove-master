# Supabase setup (cloud sync)

The schema and RLS are applied by the migrations in `supabase/migrations/`. The
CLIs (`vercel`, `supabase`) are provided by `devenv.nix`; `vercel login` /
`supabase login` once, then the steps below are non-interactive.

## 1. Environment variables (Vercel)

The site is hosted on Vercel (project `groove-academy`). The two public vars must
be set there so the deployed build is `supabaseConfigured`:

```
PUBLIC_SUPABASE_URL=https://dbfmnbnjjjmbywbeuqts.supabase.co
PUBLIC_SUPABASE_ANON_KEY=sb_publishable_…   # the publishable key (browser-safe)
```

Set them with the CLI (repeat for `preview` and `development`):

```
vercel link --yes --project groove-academy
printf '%s' 'https://dbfmnbnjjjmbywbeuqts.supabase.co'       | vercel env add PUBLIC_SUPABASE_URL production
printf '%s' 'sb_publishable_…'                               | vercel env add PUBLIC_SUPABASE_ANON_KEY production
vercel --prod   # env changes only take effect on a new deployment
```

`.env` mirrors these locally (gitignored); `.env.example` documents the shape.
Auth is optional — with these unset the app still runs, entirely device-local
(`supabaseConfigured` is false).

## 2. Auth URL configuration (required for magic links)

Supabase only honours the app's requested `emailRedirectTo` if the URL is in the
redirect allowlist; otherwise it falls back to **Site URL**. Both live in the
Auth config and are versioned in `supabase/config.toml` under `[auth]`:

```
site_url = "https://groove.academy"
additional_redirect_urls = [
  "https://groove.academy/**",
  "http://localhost:5173/**",
  "http://localhost:4173/**",
]
```

Apply with the CLI — **review the diff first**, because `config push` sends the
whole `[auth]` block and default `config.toml` values differ from a live project
(TOTP MFA, email confirmations, OTP length…). The other `[auth]` fields here are
already aligned to the remote so the push is limited to the two URL fields:

```
supabase config push --project-ref dbfmnbnjjjmbywbeuqts          # shows the diff, prompts
```

The sign-in flow calls `signInWithOtp({ emailRedirectTo: <origin>/auth/confirm })`;
`/auth/confirm` (`src/routes/auth/confirm/+server.ts`) accepts either a PKCE
`?code=` (default email template) or a `?token_hash=&type=` link. After changing
Site URL, request a **fresh** link — already-sent emails keep the old target.

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
