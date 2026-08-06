// Saved pad/device configuration in localStorage.
//
//   groove-master:<deviceId>      { notes, soundNotes, kit, deviceName, cols?, rows?,
//                             transport? }  — transport is { start, stop }, the
//                             controller's Play/Stop buttons (see
//                             transport-control.ts); either half may be null.
//   groove-master:selectedDevice  the deviceId last chosen
//   groove-master:maxbpm:<lessonId>  highest BPM the student may select there
//   groove-master:tier:<lessonId>    the rung last chosen on that lesson
//   groove-master:lessons-unlocked   ids of the lessons opened so far
//
// Written by /onboarding and /debug/settings, read by /lessons/[id] and the layout's
// background sample warm-up. The per-lesson tempo is both written and read by
// /lessons/[id] alone.
//
// Practice history is not here — it lives in IndexedDB (see stats.ts), which is
// what an append-only log with per-run detail wants. localStorage keeps only the
// small settings that have to be readable synchronously during render.

export const STORAGE_PREFIX = "groove-master:";

export const DEFAULT_KIT = 1;

/** The saved kit for the last-selected device, or DEFAULT_KIT. */
export function savedKit(): number {
  try {
    const deviceId = localStorage.getItem(STORAGE_PREFIX + "selectedDevice");
    if (!deviceId) return DEFAULT_KIT;
    const raw = localStorage.getItem(STORAGE_PREFIX + deviceId);
    if (!raw) return DEFAULT_KIT;
    const kit = JSON.parse(raw).kit;
    return typeof kit === "number" ? kit : DEFAULT_KIT;
  } catch {
    // No storage (private mode) or malformed JSON — the default still works.
    return DEFAULT_KIT;
  }
}
