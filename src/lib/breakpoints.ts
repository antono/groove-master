// The one mobile breakpoint.
//
// Below this the navigation collapses to a menu, the result screen fills the
// screen, and /stats reflows to a single column.
//
// It is declared twice — here, and as a literal in the CSS that needs it — and
// this file is the source of truth. A custom property cannot be used in a media
// query, and the pieces that need to know (the menu panel's focus trap, the
// install strip) run in JS, so one of the two has to be a literal. Every CSS
// rule that hard-codes 48rem carries a comment pointing back here.
//
// 48rem: seven monospace nav links plus the brand need roughly 40rem before
// they crowd, and the header has its own padding on top of that.

/** The mobile breakpoint in rem, as written in the media queries. */
export const MOBILE_BREAKPOINT_REM = 48;

/** The same value in CSS pixels, for matchMedia. Assumes a 16px root. */
export const MOBILE_BREAKPOINT_PX = MOBILE_BREAKPOINT_REM * 16;

/** `(max-width: 48rem)` — true on the layouts this change is about. */
export const MOBILE_QUERY = `(max-width: ${MOBILE_BREAKPOINT_REM}rem)`;
