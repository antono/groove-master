// Hand the validated session/user (resolved in hooks.server.ts) and the request
// cookies down to the universal load, so the browser client hydrates in the same
// auth state the server rendered — no signed-out flash.

import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async ({
  locals: { session, user },
  cookies,
}) => {
  return { session, user, cookies: cookies.getAll() };
};
