# padrill

A browser-based finger drumming trainer. Play along with interactive lessons to
build finger drumming skills, all in HTML — no native app required. Only finger
drumming is supported.

## Stack

- SvelteKit (Svelte 5) + TypeScript
- Vite

## Drum samples

- `soundfonts/Perfect_Drums.sf2` holds 12 GM-percussion kits (244 MB, not shipped
  to the browser).
- `python3 scripts/render-drums.py` pre-renders each kit's drums to
  `static/drums/kit<N>/<note>.oga` plus `static/drums/manifest.json`
  (kits + drum catalogue). Re-run after changing the SoundFont or layout.
- The grid uses two mappings: **controller note → cell** (Capture) and
  **cell → GM drum note** (per-cell dropdown). Both are saved per device in
  `localStorage`.

## Bass samples (backing track)

- Three CC0 (public-domain) FreePats basses live in `soundfonts/`
  (`LatelyBass.sf2`, `SynthBass1.sf2`, `SynthBass2.sf2`).
- `python3 scripts/render-bass.py` renders notes E1–C4 (MIDI 28–60) to
  `static/bass/<id>/<note>.oga` plus `static/bass/manifest.json`.
- **Any SoundFont whose samples are shipped must be credited in `THANKS.md`**
  (name, samples taken, license, authors).

## Commands

- `pnpm dev` — start dev server
- `pnpm build` — production build
- `pnpm preview` — preview the production build
- `pnpm check` — type-check with svelte-check
