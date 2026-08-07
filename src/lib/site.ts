// Identity for the crawlers: everything a link preview needs that isn't
// page-specific.
//
// The URLs here are absolute on purpose. Facebook, Slack, Mastodon and
// Twitter all discard a relative og:image, and `base` is relative during SSR
// (see the note in +layout.svelte), so neither the page's own origin nor
// `${base}/og.png` can be used — the origin has to be spelled out.
export const SITE_URL = "https://groove.academy";
export const SITE_NAME = "Groove Academy";

// 1200x630 card, rendered from docs/og-card.svg by scripts/render-og.sh.
export const OG_IMAGE = `${SITE_URL}/og.png`;
export const OG_IMAGE_WIDTH = 1200;
export const OG_IMAGE_HEIGHT = 630;
export const OG_IMAGE_ALT =
  "The Groove Academy mark — crossed drumsticks in a gold circle — beside the words " +
  "“Free drum lessons that scroll by in your browser.”";

/** Absolute URL for a route, for og:url and rel=canonical. */
export const absolute = (pathname: string) => new URL(pathname, SITE_URL).href;
