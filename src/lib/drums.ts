// Loads and plays the pre-rendered drum one-shots from static/drums/.
// Shared by the settings grid and the lessons highway.

import { base } from "$app/paths";

/** GM percussion notes rendered for every kit — see scripts/render-drums.py. */
export const DRUM_NOTES: number[] = Array.from(
  { length: 36 },
  (_, i) => 35 + i,
);

export function drumUrl(kit: number, note: number) {
  return `${base}/drums/kit${kit}/${note}.oga`;
}

/**
 * Wait until a service worker is controlling the page, so fetches actually
 * reach it and get stored.
 *
 * On a first visit the document loads before the worker exists; it installs,
 * then calls clients.claim(), which fires `controllerchange`. Anything fetched
 * before that bypasses the worker entirely and is downloaded for nothing. The
 * timeout covers browsers with no service worker at all — warming still fills
 * the HTTP cache there, so it is worth doing anyway.
 */
async function whenCaching(timeoutMs = 5000): Promise<void> {
  if (!("serviceWorker" in navigator) || navigator.serviceWorker.controller)
    return;
  await new Promise<void>((resolve) => {
    const done = () => resolve();
    navigator.serviceWorker.addEventListener("controllerchange", done, {
      once: true,
    });
    setTimeout(done, timeoutMs);
  });
}

/**
 * Pull a whole kit into the service-worker cache (~700 KB).
 *
 * Fetch only — no decoding, so this needs no AudioContext and therefore no
 * user gesture, and can run on page load. Once the service worker has them,
 * later loads and kit switches are served locally.
 */
export async function warmKit(kit: number, concurrency = 6): Promise<void> {
  await whenCaching();
  const queue = [...DRUM_NOTES];
  const canCheck = typeof caches !== "undefined";
  const worker = async () => {
    for (let note = queue.pop(); note !== undefined; note = queue.pop()) {
      const url = drumUrl(kit, note);
      try {
        // Only fetch what isn't stored yet, so a repeat visit does no work at
        // all. caches.match searches every cache, so this needs no cache name.
        if (canCheck && (await caches.match(url))) continue;
        const res = await fetch(url);
        // Read the body out: an unread response can be cancelled before the
        // service worker finishes writing it.
        await res.arrayBuffer();
      } catch {
        // Offline or 404 — nothing to warm, the normal load path still tries.
      }
    }
  };
  await Promise.all(Array.from({ length: concurrency }, worker));
}

export class DrumPlayer {
  private cache = new Map<string, AudioBuffer>();
  private pending = new Map<string, Promise<AudioBuffer | null>>();

  constructor(private ctx: AudioContext) {}

  async load(kit: number, note: number): Promise<AudioBuffer | null> {
    const key = kit + ":" + note;
    const cached = this.cache.get(key);
    if (cached) return cached;
    const existing = this.pending.get(key);
    if (existing) return existing;
    const pending = (async () => {
      try {
        const res = await fetch(drumUrl(kit, note));
        const buf = await this.ctx.decodeAudioData(await res.arrayBuffer());
        this.cache.set(key, buf);
        return buf;
      } catch {
        return null;
      } finally {
        this.pending.delete(key);
      }
    })();
    this.pending.set(key, pending);
    return pending;
  }

  async preload(kit: number, notes: Iterable<number>): Promise<void> {
    await Promise.all([...new Set(notes)].map((n) => this.load(kit, n)));
  }

  private fire(buf: AudioBuffer, when?: number) {
    const src = this.ctx.createBufferSource();
    src.buffer = buf;
    src.connect(this.ctx.destination);
    src.start(when);
  }

  play(kit: number, note: number) {
    const cached = this.cache.get(kit + ":" + note);
    if (cached) this.fire(cached);
    else this.load(kit, note).then((b) => b && this.fire(b));
  }

  // Sample-accurate strike for the lesson demo, scheduled off the audio clock.
  // Only cached buffers can hit an exact time, so this never falls back to a load.
  playAt(kit: number, note: number, when: number) {
    const cached = this.cache.get(kit + ":" + note);
    if (cached) this.fire(cached, when);
  }
}
