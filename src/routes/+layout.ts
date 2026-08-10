// Create the Supabase client that pages share. In the browser it is a
// cookie-bound browser client; during SSR it is a server client seeded from the
// cookies the server load forwarded, so `getUser()` sees the same session.
// `depends('supabase:auth')` lets an auth-state change re-run this load.

import {
  createBrowserClient,
  createServerClient,
  isBrowser,
} from "@supabase/ssr";
import { SUPABASE_KEY, SUPABASE_URL, supabaseConfigured } from "$lib/supabase";
import type { LayoutLoad } from "./$types";

export const load: LayoutLoad = async ({ data, depends, fetch }) => {
  depends("supabase:auth");

  if (!supabaseConfigured) {
    return { supabase: null, session: null, user: null };
  }

  const supabase = isBrowser()
    ? createBrowserClient(SUPABASE_URL, SUPABASE_KEY, { global: { fetch } })
    : createServerClient(SUPABASE_URL, SUPABASE_KEY, {
        global: { fetch },
        cookies: { getAll: () => data?.cookies ?? [] },
      });

  const {
    data: { session },
  } = await supabase.auth.getSession();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  return { supabase, session, user };
};
