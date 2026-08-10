// Server-side Supabase session handling for SSR.
//
// `supabase` builds a request-scoped, cookie-bound server client; `authGuard`
// resolves the *validated* user once and puts it on `event.locals`. Validation
// matters: getSession() only reads the cookie, which is spoofable, so
// safeGetSession() calls getUser() to authenticate the JWT against Supabase and
// treats any failure as signed-out. When Supabase is not configured everything
// degrades to signed-out and the app runs as it always has.

import { createServerClient } from "@supabase/ssr";
import { type Handle } from "@sveltejs/kit";
import { sequence } from "@sveltejs/kit/hooks";
import { SUPABASE_KEY, SUPABASE_URL, supabaseConfigured } from "$lib/supabase";

const supabase: Handle = async ({ event, resolve }) => {
  if (!supabaseConfigured) {
    event.locals.supabase = null;
    event.locals.safeGetSession = async () => ({ session: null, user: null });
    return resolve(event);
  }

  event.locals.supabase = createServerClient(SUPABASE_URL, SUPABASE_KEY, {
    cookies: {
      getAll: () => event.cookies.getAll(),
      setAll: (cookiesToSet) => {
        cookiesToSet.forEach(({ name, value, options }) => {
          event.cookies.set(name, value, { ...options, path: "/" });
        });
      },
    },
  });

  event.locals.safeGetSession = async () => {
    const {
      data: { session },
    } = await event.locals.supabase!.auth.getSession();
    if (!session) return { session: null, user: null };
    // getUser() re-validates the token; a bare getSession() cookie is not trusted.
    const {
      data: { user },
      error,
    } = await event.locals.supabase!.auth.getUser();
    if (error) return { session: null, user: null };
    return { session, user };
  };

  return resolve(event, {
    filterSerializedResponseHeaders: (name) =>
      name === "content-range" || name === "x-supabase-api-version",
  });
};

const authGuard: Handle = async ({ event, resolve }) => {
  const { session, user } = await event.locals.safeGetSession();
  event.locals.session = session;
  event.locals.user = user;
  return resolve(event);
};

export const handle = sequence(supabase, authGuard);
