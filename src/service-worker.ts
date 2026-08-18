/// <reference types="@sveltejs/kit" />
/// <reference no-default-lib="true"/>
/// <reference lib="esnext" />
/// <reference lib="webworker" />

// Keeps the drum and bass one-shots on the user's machine, so a kit switch
// after the first visit costs nothing and the app works offline.
//
// The audio is deliberately left out of the install precache: all 12 kits plus
// the basses come to ~10 MB, which is not something to download before the
// first pad is even pressed. Instead each sample is cached the first time it is
// fetched, and the layout quietly warms the current kit (~700 KB) on load.
//
// SvelteKit registers this automatically because the file exists.

import { build, files, version } from "$service-worker";

const sw = self as unknown as ServiceWorkerGlobalScope;

const CACHE = `groove-master-${version}`;

const isAudio = (pathname: string) => pathname.endsWith(".oga");

// App shell: everything Vite built, plus static/. `files` already excludes the
// one-shots — see the serviceWorker.files filter in vite.config.ts.
const PRECACHE = [...build, ...files];
const PRECACHED = new Set(PRECACHE);

sw.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE)
      .then((cache) => cache.addAll(PRECACHE))
      // Take over straight away rather than waiting for every tab to close.
      // Samples live at stable URLs (/drums/kit1/47.oga), so a re-render only
      // reaches people once this version's cache replaces the last one — and
      // until it does they keep playing whatever was cached before.
      .then(() => sw.skipWaiting()),
  );
});

sw.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)),
        ),
      )
      .then(() => sw.clients.claim()),
  );
});

async function cacheFirst(request: Request): Promise<Response> {
  const cache = await caches.open(CACHE);
  const hit = await cache.match(request);
  if (hit) return hit;
  const res = await fetch(request);
  // Only full, successful responses — a 206 or an error page must not stick.
  if (res.status === 200) await cache.put(request, res.clone());
  return res;
}

async function networkFirst(request: Request): Promise<Response> {
  const cache = await caches.open(CACHE);
  try {
    const res = await fetch(request);
    if (res.status === 200) await cache.put(request, res.clone());
    return res;
  } catch (err) {
    const hit = await cache.match(request);
    if (hit) return hit;
    throw err;
  }
}

sw.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;

  const url = new URL(event.request.url);
  if (url.origin !== location.origin) return;

  // The point of all this: one-shots, cached on first use and kept.
  if (isAudio(url.pathname)) {
    // A query string means "give me the file as it is on disk" — cache-first is
    // by design immune to `cache: 'reload'`, so re-levelled samples would keep
    // reading as their old selves on /debug/levels. Left to the network and not
    // cached, so the busted URLs never pile up.
    if (url.search) return;
    event.respondWith(cacheFirst(event.request));
    return;
  }

  // Catalogues and lesson MIDIs change when the render scripts re-run, so prefer
  // the network and keep a copy only as the offline fallback. Cache-first here
  // would pin a lesson to whatever make-lessons.py emitted on the first visit —
  // an edited pattern (or a new count-in) would never reach the page.
  if (
    url.pathname.endsWith("/manifest.json") ||
    url.pathname.endsWith(".mid")
  ) {
    event.respondWith(networkFirst(event.request));
    return;
  }

  if (PRECACHED.has(url.pathname)) {
    event.respondWith(cacheFirst(event.request));
    return;
  }

  // Page documents: network-first, keeping a copy as the offline fallback.
  //
  // Network-first because a cached page is a snapshot of server-rendered HTML —
  // cache-first would pin the catalogue to whatever it looked like on the first
  // visit. Offline, the exact page is served if it has been seen or precached,
  // and /offline if not.
  //
  // The tidier-sounding alternative — one app shell for every route, rendered
  // client-side — is not available: adapter-vercel emits no SPA fallback
  // document, and serving /lessons' HTML for /stats would hydrate a mismatched
  // route. Precaching the real pages sidesteps it (see $lib/offline-set).
  //
  // Matched on the *path*, not on request.mode: the offline set is warmed with
  // ordinary fetch() calls, whose mode is "cors", so keying off "navigate" would
  // let every warmed page fall straight through here and cache nothing — the
  // precache would appear to work and the app would still be blank offline.
  if (isPage(url.pathname)) {
    event.respondWith(pageNetworkFirst(event.request, url));
    return;
  }

  // Everything else is left to the browser.
});

/**
 * A path that names a page rather than a file.
 *
 * Extensionless, which every route here is, and no built asset is. `/auth/confirm`
 * is the one extensionless endpoint that is not a page — it is a redirect that
 * consumes a single-use token, so caching it would be actively wrong.
 */
function isPage(pathname: string): boolean {
  if (pathname.startsWith("/auth/")) return false;
  return !/\.[a-z0-9]+$/i.test(pathname);
}

/**
 * Cache key for a page: origin + path, with the query dropped.
 *
 * `/lessons/1.2?bpm=90` is the same document as `/lessons/1.2` — the tempo is
 * read from the URL after hydration — so keying on the query would store a copy
 * per tempo and miss on the one navigation that mattered.
 */
const pageKey = (url: URL) => url.origin + url.pathname;

async function pageNetworkFirst(request: Request, url: URL): Promise<Response> {
  const cache = await caches.open(CACHE);
  const key = pageKey(url);
  try {
    const res = await fetch(request);
    if (res.status === 200) await cache.put(key, res.clone());
    return res;
  } catch {
    const hit = await cache.match(key);
    if (hit) return hit;
    const fallback = await cache.match(new URL("/offline", url.origin).href);
    if (fallback) return fallback;
    // Nothing cached at all — a first visit that went offline mid-flight. Say so
    // rather than throwing, which surfaces as the browser's own error page.
    return new Response(
      "<!doctype html><meta charset=utf-8><title>Offline</title><p>You are offline.",
      { status: 503, headers: { "content-type": "text/html; charset=utf-8" } },
    );
  }
}
