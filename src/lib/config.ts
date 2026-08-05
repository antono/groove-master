// Saved pad/device configuration in localStorage.
//
//   padrill:<deviceId>      { notes, soundNotes, kit, deviceName, cols?, rows? }
//   padrill:selectedDevice  the deviceId last chosen
//
// Written by /settings and /onboarding, read by /lessons/[id] and the layout's
// background sample warm-up.

export const STORAGE_PREFIX = "padrill:";

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
