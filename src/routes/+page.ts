import { redirect } from "@sveltejs/kit";
import { base } from "$app/paths";

// Lessons are the front door; the pad grid lives at /debug/settings.
export const load = () => {
  redirect(307, `${base}/lessons`);
};
