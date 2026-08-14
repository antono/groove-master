// Virtual controllers — a computer keyboard and an on-screen pad grid, so a
// lesson is playable with no MIDI hardware and on a touchscreen that has no Web
// MIDI at all.
//
// Both are ordinary selectable input sources: they carry a reserved id/name that
// slots into the same `selectedId` selection and `{ device, deviceId }` stats
// record a Web MIDI port would. A virtual source has no controller note to
// capture, so it resolves pad -> GM directly (see `dispatchHit` on the lesson
// page) and never enters `Controller.handle()`. Its mapping is the cell -> GM
// half only, stored under its reserved id like any device and edited with the
// same per-pad dropdown.
//
// The reserved ids contain a ":" on purpose: `Controller.list()` skips those, so
// a virtual source is never double-listed in the device chooser — it is appended
// to the input list explicitly, here.

import { Controller, type Pad } from "$lib/controller.svelte";
import type { DrumRole } from "$lib/presets";

export const VIRTUAL_KEYBOARD_ID = "virtual:keyboard";
export const VIRTUAL_TOUCH_ID = "virtual:touch";

export const VIRTUAL_INPUTS: { id: string; name: string }[] = [
  { id: VIRTUAL_KEYBOARD_ID, name: "Keyboard" },
  { id: VIRTUAL_TOUCH_ID, name: "On-screen pads" },
];

export function isVirtualId(id: string | null | undefined): boolean {
  return id === VIRTUAL_KEYBOARD_ID || id === VIRTUAL_TOUCH_ID;
}

/**
 * The default virtual pad set — the finger-drumming core (kick, snare, both
 * hats) plus toms, crash and ride, so every lane the curriculum uses is
 * reachable out of the box. Order is the on-screen grid's reading order: top row
 * first (colour/cymbals/toms), bottom row the groove core, mirroring how
 * `DEFAULT_GRID_SOUNDS` keeps kick/snare/hats along the bottom.
 */
const DEFAULT_PADS: { label: string; role: DrumRole; sound: number }[] = [
  { label: "Crash", role: "crash", sound: 49 },
  { label: "Tom", role: "tom", sound: 48 },
  { label: "Tom", role: "tom", sound: 45 },
  { label: "Ride", role: "ride", sound: 51 },
  { label: "Kick", role: "kick", sound: 36 },
  { label: "Snare", role: "snare", sound: 38 },
  { label: "Hat", role: "hihat", sound: 42 },
  { label: "Open hat", role: "hihat", sound: 46 },
];

/**
 * Keyboard layout by *physical* key position (`event.code`), not the printed
 * letter, so the same home-row shape holds on QWERTY, AZERTY or Dvorak and does
 * not depend on the OS keyboard language. Two rows of four, aligned pad-for-pad
 * with `DEFAULT_PADS`: the top row (R T Y U) is the colour voices, the home row
 * (F G H J) is the groove core.
 */
const KEYBOARD_CODES = ["KeyR", "KeyT", "KeyY", "KeyU", "KeyF", "KeyG", "KeyH", "KeyJ"];

/** `event.code` values that drive the transport while the keyboard is active. */
export const TRANSPORT_START_CODE = "Space";
export const TRANSPORT_STOP_CODE = "Escape";

function defaultPads(): Pad[] {
  return DEFAULT_PADS.map((p, i) => ({
    id: `pad-${i}`,
    label: p.label,
    role: p.role,
    note: null, // Controller.virtual fills a synthetic note
    sound: p.sound,
  }));
}

/**
 * The controller for a virtual source: its stored mapping if the student has
 * edited one, otherwise the built-in default so first use needs no setup.
 */
export function loadVirtualController(deviceId: string): Controller {
  return Controller.load(deviceId) ?? Controller.virtual(deviceId, nameFor(deviceId), defaultPads());
}

function nameFor(deviceId: string): string {
  return VIRTUAL_INPUTS.find((v) => v.id === deviceId)?.name ?? "Virtual";
}

/**
 * The GM note a physical key produces on this keyboard controller, or null if
 * the key is not a pad. Resolves `event.code` -> pad position -> that pad's
 * (editable) GM sound.
 */
export function keyboardGm(controller: Controller | null, code: string): number | null {
  if (!controller) return null;
  const i = KEYBOARD_CODES.indexOf(code);
  if (i === -1) return null;
  return controller.pads[i]?.sound ?? null;
}

/** The key label to show on a pad, for the on-screen legend. Empty if unbound. */
export function keyLabelFor(index: number): string {
  const code = KEYBOARD_CODES[index];
  return code?.startsWith("Key") ? code.slice(3) : "";
}
