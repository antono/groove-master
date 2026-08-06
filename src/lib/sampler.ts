// Generic pitched-sample player for backing tracks (bass, etc.).
// Samples live at static/<family>/<id>/<note>.oga (e.g. bass/lately/40.oga).

import { base } from "$app/paths";

export class Sampler {
  private cache = new Map<string, AudioBuffer>();
  private pending = new Map<string, Promise<AudioBuffer | null>>();

  constructor(private ctx: AudioContext) {}

  private url(family: string, id: string, note: number) {
    return `${base}/${family}/${id}/${note}.oga`;
  }

  async load(
    family: string,
    id: string,
    note: number,
  ): Promise<AudioBuffer | null> {
    const key = `${family}/${id}/${note}`;
    const cached = this.cache.get(key);
    if (cached) return cached;
    const existing = this.pending.get(key);
    if (existing) return existing;
    const pending = (async () => {
      try {
        const res = await fetch(this.url(family, id, note));
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

  async preload(
    family: string,
    id: string,
    notes: Iterable<number>,
  ): Promise<void> {
    await Promise.all([...new Set(notes)].map((n) => this.load(family, id, n)));
  }

  // `gain` is a linear multiplier, 1 = the sample as rendered. Backing tracks
  // carry MIDI velocity so a bass line can ghost a note instead of playing
  // every note at the same weight, which is most of what separates a bass line
  // from a MIDI file. A node is only inserted when it would do something.
  private fire(buf: AudioBuffer, when?: number, gain = 1) {
    const src = this.ctx.createBufferSource();
    src.buffer = buf;
    if (gain === 1) {
      src.connect(this.ctx.destination);
    } else {
      const g = this.ctx.createGain();
      g.gain.value = gain;
      src.connect(g).connect(this.ctx.destination);
    }
    src.start(when);
  }

  play(family: string, id: string, note: number) {
    const cached = this.cache.get(`${family}/${id}/${note}`);
    if (cached) this.fire(cached);
    else this.load(family, id, note).then((b) => b && this.fire(b));
  }

  playAt(family: string, id: string, note: number, when: number, gain = 1) {
    const cached = this.cache.get(`${family}/${id}/${note}`);
    if (cached) this.fire(cached, when, gain);
  }
}
