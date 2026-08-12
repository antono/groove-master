// The catalogue's structural metadata (tiers, stages, modules) is the same on
// every level below the highway, so it loads once here and flows to the landing,
// tier and stage pages through their `data`. Loading it in `load` rather than
// `onMount` means headings and breadcrumbs render server-side. The lesson page
// under [id] does its own thing and simply ignores this.
//
// Only the metadata moves here — practice history (IndexedDB) and the MIDI-derived
// charts stay client-side on the pages that need them.

import { fetchManifest, type Manifest } from "$lib/catalogue";
import type { LayoutLoad } from "./$types";

export const load: LayoutLoad = async ({ fetch }) => {
  try {
    const manifest = await fetchManifest(fetch);
    return { manifest, manifestError: false };
  } catch {
    // The catalogue must degrade to a message, not a crash, when the manifest
    // has not been generated (run make-lessons.py).
    return { manifest: null as Manifest | null, manifestError: true };
  }
};
