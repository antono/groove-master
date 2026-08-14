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
 * The default virtual pad set — six essentials, so the grid stays small enough to
 * fit a phone (2×3) and every drum the curriculum actually leans on is reachable
 * out of the box. The lessons are overwhelmingly kick / snare / closed hat / open
 * hat, with the odd cymbal; toms are dropped to keep it to six. Order is the grid's
 * reading order laid out for a 3-wide desktop grid: top row the colour voices,
 * bottom row (home keys F G H) the groove core.
 */
const DEFAULT_PADS: { label: string; role: DrumRole; sound: number }[] = [
  { label: "Crash", role: "crash", sound: 49 },
  { label: "Ride", role: "ride", sound: 51 },
  { label: "Open hat", role: "hihat", sound: 46 },
  { label: "Kick", role: "kick", sound: 36 },
  { label: "Snare", role: "snare", sound: 38 },
  { label: "Hat", role: "hihat", sound: 42 },
];

/**
 * Keyboard layout by *physical* key position (`event.code`), not the printed
 * letter, so the same home-row shape holds on QWERTY, AZERTY or Dvorak and does
 * not depend on the OS keyboard language. Two rows of three, aligned pad-for-pad
 * with `DEFAULT_PADS`: the upper row (R T Y) is the colour voices, the home row
 * (F G H) is the groove core — kick, snare, closed hat under the fingers.
 */
const KEYBOARD_CODES = ["KeyR", "KeyT", "KeyY", "KeyF", "KeyG", "KeyH"];

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
  return (
    Controller.load(deviceId) ??
    Controller.virtual(deviceId, nameFor(deviceId), defaultPads())
  );
}

function nameFor(deviceId: string): string {
  return VIRTUAL_INPUTS.find((v) => v.id === deviceId)?.name ?? "Virtual";
}

/**
 * The GM note a physical key produces on this keyboard controller, or null if
 * the key is not a pad. Resolves `event.code` -> pad position -> that pad's
 * (editable) GM sound.
 */
export function keyboardGm(
  controller: Controller | null,
  code: string,
): number | null {
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

/** The pad index a physical key maps to, or -1 if the key is not a pad. */
export function keyboardIndexFor(code: string): number {
  return KEYBOARD_CODES.indexOf(code);
}
