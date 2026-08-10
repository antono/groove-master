// Magic-link landing. Handles both magic-link shapes so it works with the
// default Supabase email template and a customised one:
//   - PKCE:       /auth/confirm?code=…            → exchangeCodeForSession
//   - token hash: /auth/confirm?token_hash=…&type → verifyOtp
// On success a session cookie is set and the student continues to their account;
// any failure lands on /auth/error.

import { redirect } from "@sveltejs/kit";
import type { EmailOtpType } from "@supabase/supabase-js";
import type { RequestHandler } from "./$types";

export const GET: RequestHandler = async ({ url, locals: { supabase } }) => {
  const code = url.searchParams.get("code");
  const token_hash = url.searchParams.get("token_hash");
  const type = url.searchParams.get("type") as EmailOtpType | null;
  const next = url.searchParams.get("next") ?? "/account";
  // Only ever redirect to an in-app path, never an attacker-supplied absolute URL.
  const dest = next.startsWith("/") ? next : "/account";

  if (supabase) {
    if (code) {
      const { error } = await supabase.auth.exchangeCodeForSession(code);
      if (!error) redirect(303, dest);
    } else if (token_hash && type) {
      const { error } = await supabase.auth.verifyOtp({ type, token_hash });
      if (!error) redirect(303, dest);
    }
  }

  redirect(303, "/auth/error");
};
