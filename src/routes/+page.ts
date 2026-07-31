import { redirect } from "@sveltejs/kit";
import { base } from "$app/paths";

// The main pad grid now lives at /settings.
export const load = () => {
  redirect(307, `${base}/settings`);
};
