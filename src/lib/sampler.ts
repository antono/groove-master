// Generic pitched-sample player for backing tracks (bass, etc.).
// Samples live at static/<family>/<id>/<note>.oga (e.g. bass/lately/40.oga).

import { base } from "$app/paths";

export class Sampler {
  private cache = new Map<string, AudioBuffer>();

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
    try {
      const res = await fetch(this.url(family, id, note));
      const buf = await this.ctx.decodeAudioData(await res.arrayBuffer());
      this.cache.set(key, buf);
      return buf;
    } catch {
      return null;
    }
  }

  async preload(
    family: string,
    id: string,
    notes: Iterable<number>,
  ): Promise<void> {
    await Promise.all([...new Set(notes)].map((n) => this.load(family, id, n)));
  }

  private fire(buf: AudioBuffer) {
    const src = this.ctx.createBufferSource();
    src.buffer = buf;
    src.connect(this.ctx.destination);
    src.start();
  }

  play(family: string, id: string, note: number) {
    const cached = this.cache.get(`${family}/${id}/${note}`);
    if (cached) this.fire(cached);
    else this.load(family, id, note).then((b) => b && this.fire(b));
  }
}
