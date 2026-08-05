// Loads and plays the pre-rendered drum one-shots from static/drums/.
// Shared by the settings grid and the lessons highway.

import { base } from "$app/paths";

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
        const res = await fetch(`${base}/drums/kit${kit}/${note}.oga`);
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
