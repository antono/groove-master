// Device presets and kit profiles — the two kinds of controller this app knows
// how to be set up against.
//
// Neither ever asserts a MIDI note. A grid preset supplies dimensions, a kit
// profile supplies geometry and drum roles, and the notes are always recorded
// during the capture step, because physical layouts and note maps vary by
// firmware, bank, and (on a drum module) whatever the last owner assigned from
// the front panel. This keeps autodetect useful without asserting hardware
// facts we can't guarantee.
//
// A profile describes a *model*. What a particular student's instrument turned
// out to be belongs to their Controller (see controller.svelte.ts).
//
// Grid is capped at 4×4 for now (see MAX_COLS / MAX_ROWS). Add rows/cols later
// by bumping those and appending presets.

export const MAX_COLS = 4;
export const MAX_ROWS = 4;

/**
 * Grid cell -> GM drum note for a full 4×4. Bottom row = groove core; smaller
 * grids take the *tail* so kick/snare/hats stay on the bottom row.
 */
export const DEFAULT_GRID_SOUNDS = [
  39, 56, 54, 55, 49, 51, 53, 52, 45, 47, 50, 44, 36, 38, 42, 46,
];

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

/**
 * What a port calls itself, cleaned up and with the manufacturer folded in.
 *
 * Two reasons this exists. Drum modules are frequently OEM hardware sold under
 * someone else's name and their port name says nothing useful — a Millenium
 * MD-90 announces itself as `"e-drum"` by `"Medeli"`, who actually built it — so
 * the maker is often the only identifying half and matching on the name alone
 * cannot work.
 *
 * And port strings are not clean. That same module appends U+202D (a bidirectional
 * override) to its manufacturer; such characters are invisible, survive a copy,
 * and will happily flip the direction of any text rendered after them. They are
 * stripped here so neither a regex nor a page has to think about it.
 */
export function deviceIdentity(
  name: string | null | undefined,
  manufacturer?: string | null,
): string {
  return (
    `${name ?? ""} ${manufacturer ?? ""}`
      .normalize("NFKC")
      // zero-width and bidi formatting characters
      .replace(/[​-‏‪-‮⁦-⁩﻿]/g, "")
      .replace(/\s+/g, " ")
      .trim()
  );
}

/** A device's display name, free of the control characters some ports carry. */
export function cleanDeviceName(name: string | null | undefined): string {
  return deviceIdentity(name).trim() || "Unknown device";
}

/** First preset whose pattern matches the device identity, or null. */
export function matchPreset(
  name: string | null | undefined,
  manufacturer?: string | null,
): Preset | null {
  const id = deviceIdentity(name, manufacturer);
  if (!id) return null;
  return PRESETS.find((p) => p.match.test(id)) ?? null;
}

// --- electronic kits -------------------------------------------------------

/**
 * What a pad stands for. This is identity, not sound: a student may assign an
 * unusual GM note to their hi-hat and it is still the kit's hi-hat, which is
 * what pedal handling and the playability check reason about.
 */
export type DrumRole =
  | "kick"
  | "snare"
  | "tom"
  | "hihat"
  | "crash"
  | "ride"
  | "perc";

export const ROLE_LABELS: Record<DrumRole, string> = {
  kick: "Kick",
  snare: "Snare",
  tom: "Tom",
  hihat: "Hi-hat",
  crash: "Crash",
  ride: "Ride",
  perc: "Percussion",
};

export type KitPad = {
  /** must match an element id in the profile's schematic */
  id: string;
  label: string;
  role: DrumRole;
  /** suggested GM percussion note; the student may change it */
  sound: number;
  /** this one arrives via a footswitch jack rather than a pad */
  pedal?: "kick" | "hihat";
};

export type KitProfile = {
  id: string;
  label: string;
  /** matched (case-insensitive) against `deviceIdentity()` — name + maker */
  match: RegExp;
  /**
   * Set when the port identity narrows the device only to a *family* — an OEM
   * module sold under several brands, all announcing themselves identically.
   * The wizard then offers the profile without asserting the model, because a
   * port that cannot tell them apart means only the student can.
   */
  family?: string;
  /**
   * Path under static/ to a schematic whose drums are `<g id>`s matching the
   * pad ids. First-party assets only — the preview inlines this, so a
   * user-supplied file must never reach it. null = draw the neutral layout.
   */
  schematic: string | null;
  /** in the order the wizard walks them */
  pads: KitPad[];
};

export const KIT_PROFILES: KitProfile[] = [
  {
    // Tabletop module: seven velocity pads reading as a snare, three toms, a
    // hi-hat and two cymbals, plus jacks for a kick and a hi-hat footswitch.
    // The hi-hat sits oddly to the right of the snare rather than out to the
    // side — that is the real instrument, so that is what the schematic shows.
    //
    // It does not announce itself as an MD-90, or as a Millenium at all: the
    // port is `"e-drum"` by `"Medeli"`, the OEM behind Thomann's Millenium line.
    // So the maker is what identifies it, and only to the family — hence
    // `family` below, and hence the wizard asking rather than telling.
    id: "millenium-md-90",
    label: "Millenium MD-90",
    match: /\bmedeli\b|\be-?drum\b/i,
    family: "Medeli e-drum module",
    schematic: "/kits/millenium-md-90.svg",
    pads: [
      { id: "snare", label: "Snare", role: "snare", sound: 38 },
      { id: "hihat", label: "Hi-hat", role: "hihat", sound: 42 },
      { id: "tom-1", label: "Tom 1", role: "tom", sound: 48 },
      { id: "tom-2", label: "Tom 2", role: "tom", sound: 47 },
      { id: "tom-3", label: "Floor tom", role: "tom", sound: 45 },
      { id: "crash", label: "Crash", role: "crash", sound: 49 },
      { id: "ride", label: "Ride", role: "ride", sound: 51 },
      {
        id: "kick",
        label: "Kick pedal",
        role: "kick",
        sound: 36,
        pedal: "kick",
      },
    ],
  },
];

/** First kit profile whose pattern matches the device identity, or null. */
export function matchKit(
  name: string | null | undefined,
  manufacturer?: string | null,
): KitProfile | null {
  const id = deviceIdentity(name, manufacturer);
  if (!id) return null;
  return KIT_PROFILES.find((p) => p.match.test(id)) ?? null;
}

export function kitProfile(id: string | null | undefined): KitProfile | null {
  if (!id) return null;
  return KIT_PROFILES.find((p) => p.id === id) ?? null;
}

export type DeviceMatch =
  | { kind: "edrum"; profile: KitProfile }
  | { kind: "grid"; preset: Preset }
  | null;

/**
 * One lookup answering "grid preset, kit profile, or neither" for a port name.
 * Kits are tried first: they are the more specific claim, and a kit that also
 * happened to match a grid pattern should still be set up as a kit.
 */
export function matchDevice(
  name: string | null | undefined,
  manufacturer?: string | null,
): DeviceMatch {
  const profile = matchKit(name, manufacturer);
  if (profile) return { kind: "edrum", profile };
  const preset = matchPreset(name, manufacturer);
  if (preset) return { kind: "grid", preset };
  return null;
}
