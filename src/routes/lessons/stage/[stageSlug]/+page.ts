import { error } from "@sveltejs/kit";
import type { PageLoad } from "./$types";

// Resolve the stage, and the tier it belongs to (for the breadcrumb trail), from
// the manifest the layout already loaded.
export const load: PageLoad = async ({ params, parent }) => {
  const { manifest } = await parent();
  const stage = manifest?.stages?.find((s) => s.slug === params.stageSlug);
  if (!stage) throw error(404, `Unknown stage: ${params.stageSlug}`);
  const tier =
    manifest?.tiers?.find((t) => t.stages.includes(stage.number)) ?? null;
  return { stage, tier };
};
