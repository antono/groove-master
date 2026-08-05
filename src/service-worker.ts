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

  // Everything else — page navigations included — is left to the browser.
});
