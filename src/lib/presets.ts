// Device presets. A preset only supplies the *grid dimensions* (and a friendly
// name) for a recognised controller — the actual pad notes are always recorded
// during the capture step, because physical layouts and note maps vary by
// firmware/bank. This keeps autodetect useful without asserting hardware facts
// we can't guarantee.
//
// Grid is capped at 4×4 for now (see MAX_COLS / MAX_ROWS). Add rows/cols later
// by bumping those and appending presets.

export const MAX_COLS = 4;
export const MAX_ROWS = 4;

export type Preset = {
  id: string;
  label: string;
  /** matched (case-insensitive) against the MIDI input name */
  match: RegExp;
  cols: number;
  rows: number;
};

export const PRESETS: Preset[] = [
  { id: "mpd218", label: "Akai MPD218", match: /mpd\s?218/i, cols: 4, rows: 4 },
  { id: "mpd226", label: "Akai MPD226", match: /mpd\s?226/i, cols: 4, rows: 4 },
  {
    id: "mpk-mini",
    label: "Akai MPK Mini",
    match: /mpk\s?mini/i,
    cols: 4,
    rows: 2,
  },
  {
    id: "launchkey-mini",
    label: "Novation Launchkey Mini",
    match: /launchkey\s?mini/i,
    cols: 4,
    rows: 2,
  },
  {
    id: "launchpad",
    label: "Novation Launchpad",
    match: /launchpad/i,
    cols: 4,
    rows: 4,
  },
  {
    id: "maschine",
    label: "NI Maschine",
    match: /maschine/i,
    cols: 4,
    rows: 4,
  },
  { id: "atom", label: "PreSonus ATOM", match: /atom/i, cols: 4, rows: 4 },
];

/** First preset whose name pattern matches, or null. */
export function matchPreset(name: string | null | undefined): Preset | null {
  if (!name) return null;
  return PRESETS.find((p) => p.match.test(name)) ?? null;
}
