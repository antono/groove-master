// Installing the app, and what installing it earns you.
//
// Two things live here because they are the same question asked twice: is this
// somebody's instrument, or a page they landed on? The install affordance asks
// it, and the offline precache spends bandwidth only once the answer is yes.

import { savedKit } from "$lib/config";
import { warmUrls, allCached } from "$lib/drums";
import { fetchManifest, type Manifest } from "$lib/catalogue";
import { offlineUrls } from "$lib/offline-set";
import {
  pwaInstallOffered,
  pwaInstallPrompt,
  pwaInstalled,
} from "$lib/analytics";

const DISMISSED_KEY = "groove-master:install-dismissed";

/** The event Chromium fires instead of showing its own install UI. */
type InstallPromptEvent = Event & {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
};

/**
 * Running as an installed app.
 *
 * `display-mode: standalone` covers Chromium and desktop; `navigator.standalone`
 * is the iOS-only equivalent, and iOS is exactly the case that needs it — Safari
 * fires neither `beforeinstallprompt` nor `appinstalled`, so without this an iOS
 * install is invisible to us and never precaches.
 */
export function isInstalled(): boolean {
  if (typeof matchMedia !== "function") return false;
  if (matchMedia("(display-mode: standalone)").matches) return true;
  if (matchMedia("(display-mode: fullscreen)").matches) return true;
  return (navigator as { standalone?: boolean }).standalone === true;
}

export const pwaState = $state({
  /** The affordance can be shown: a prompt is held and nothing blocks it. */
  canInstall: false,
  /** Precache progress, 0..1, or null when nothing is running. */
  warming: null as number | null,
});

let deferred: InstallPromptEvent | null = null;

function dismissed(): boolean {
  try {
    return localStorage.getItem(DISMISSED_KEY) === "1";
  } catch {
    return false; // No storage (private mode) — offering it again is the lesser sin.
  }
}

/** Stop offering the affordance on this device. */
export function dismissInstall() {
  pwaState.canInstall = false;
  try {
    localStorage.setItem(DISMISSED_KEY, "1");
  } catch {
    // Nothing to do — it simply reappears next visit.
  }
}

/** Show the browser's install prompt and record what the student chose. */
export async function promptInstall() {
  const event = deferred;
  if (!event) return;
  // A deferred prompt is single-use: dropping the reference first stops a
  // double-click asking twice and throwing.
  deferred = null;
  pwaState.canInstall = false;
  try {
    await event.prompt();
    const { outcome } = await event.userChoice;
    pwaInstallPrompt(outcome);
    // A dismissed prompt is not a dismissed affordance — the browser will not
    // re-offer this event, but a later visit may fire a fresh one.
  } catch {
    // The browser refused to show it; nothing was installed and nothing broke.
  }
}

/**
 * Pull the offline set into the cache, reporting progress.
 *
 * Safe to call repeatedly. warmUrls skips what is already cached, so an
 * interrupted run is completed rather than restarted by the next one, and a
 * cache emptied by a service-worker version bump is simply refilled.
 */
export async function warmOfflineSet() {
  if (pwaState.warming !== null) return; // already running

  let manifest: Manifest | null = null;
  try {
    manifest = await fetchManifest(fetch);
  } catch {
    // No catalogue — warm the kit and the pages anyway; the lessons come next time.
  }

  const urls = offlineUrls(savedKit(), manifest);
  pwaState.warming = 0;
  try {
    await warmUrls(urls, 6, (done, total) => {
      pwaState.warming = total ? done / total : 1;
    });
  } finally {
    pwaState.warming = null;
  }
}

/**
 * Wire up install detection. Call once, from the root layout, in the browser.
 * Returns a teardown.
 */
export function initPwa(): () => void {
  const onBeforePrompt = (event: Event) => {
    // Keep the event so the affordance can show it later; without
    // preventDefault Chromium may show its own mini-infobar as well.
    event.preventDefault();
    deferred = event as InstallPromptEvent;
    if (dismissed() || isInstalled()) return;
    pwaState.canInstall = true;
    pwaInstallOffered();
  };

  const onInstalled = () => {
    pwaState.canInstall = false;
    pwaInstalled();
    void warmOfflineSet();
  };

  window.addEventListener("beforeinstallprompt", onBeforePrompt);
  window.addEventListener("appinstalled", onInstalled);

  // Launched as an installed app: top up whatever the offline set is missing.
  // This is not merely the iOS fallback for the absent `appinstalled` — it is
  // what makes the precache re-triggerable at all. The sample cache is
  // version-keyed and dropped on activate, so a re-render empties it, and a
  // once-ever flag would leave an installed app permanently unable to refill.
  if (isInstalled()) {
    void (async () => {
      let manifest: Manifest | null = null;
      try {
        manifest = await fetchManifest(fetch);
      } catch {
        // Offline already, or no catalogue — nothing to check against.
        return;
      }
      if (await allCached(offlineUrls(savedKit(), manifest))) return;
      await warmOfflineSet();
    })();
  }

  return () => {
    window.removeEventListener("beforeinstallprompt", onBeforePrompt);
    window.removeEventListener("appinstalled", onInstalled);
  };
}
