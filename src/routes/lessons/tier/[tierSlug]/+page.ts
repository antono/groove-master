import { error } from "@sveltejs/kit";
import type { PageLoad } from "./$types";

// The tier is resolved from the manifest the layout already loaded, so the page
// gets a concrete tier (or a 404) rather than doing the lookup itself.
export const load: PageLoad = async ({ params, parent }) => {
  const { manifest } = await parent();
  const tier = manifest?.tiers?.find((t) => t.slug === params.tierSlug);
  if (!tier) throw error(404, `Unknown tier: ${params.tierSlug}`);
  return { tier };
};
