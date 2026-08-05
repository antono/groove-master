// Transport buttons on a MIDI controller (Play / Stop), captured in the setup
// wizard and used by the lessons page to start and pause a run from the pads.
//
// Controllers disagree on what a transport button sends, so a binding is stored
// as whatever the button actually emitted:
//   - realtime: single-byte System Real-Time (0xFA Start, 0xFB Continue,
//     0xFC Stop) — what a controller with a real transport section usually sends
//   - cc:       a Control Change, the common case for pad units (press = value
//     >= 64, release = 0)
//   - note:     a plain note, used by pads whose buttons are just more pads
//
// Value/velocity is deliberately NOT part of the binding — it is the press, not
// the identity of the button.

export type MidiControl =
  | { kind: "realtime"; data1: number }
  | { kind: "cc"; channel: number; data1: number }
  | { kind: "note"; channel: number; data1: number };

/** A binding pair as saved per device. Either half may be unset. */
export type TransportBinding = {
  start: MidiControl | null;
  stop: MidiControl | null;
};

const RT_START = 0xfa;
const RT_CONTINUE = 0xfb;
const RT_STOP = 0xfc;

/**
 * Decode a raw MIDI message into a bindable control plus whether this message
 * is a *press*. Returns null for anything that can't be a button — clock
 * (0xF8), active sensing (0xFE), pitch bend, aftertouch, and so on — so the
 * caller never has to filter the realtime firehose itself.
 */
export function parseControl(
  data: Uint8Array | number[],
): { control: MidiControl; pressed: boolean } | null {
  if (!data || data.length === 0) return null;
  const status = data[0];

  if (status >= 0xf8) {
    // System Real-Time. Only the transport bytes are buttons; 0xF8 clock and
    // 0xFE active sensing arrive constantly and must be ignored.
    if (status !== RT_START && status !== RT_CONTINUE && status !== RT_STOP) {
      return null;
    }
    return { control: { kind: "realtime", data1: status }, pressed: true };
  }

  if (data.length < 3) return null;
  const cmd = status & 0xf0;
  const channel = status & 0x0f;
  const [, data1, data2] = data;

  if (cmd === 0x90) {
    return { control: { kind: "note", channel, data1 }, pressed: data2 > 0 };
  }
  if (cmd === 0x80) {
    return { control: { kind: "note", channel, data1 }, pressed: false };
  }
  if (cmd === 0xb0) {
    // Momentary buttons send 127 then 0; toggles send 127 / 0. Either way the
    // press is the high half.
    return { control: { kind: "cc", channel, data1 }, pressed: data2 >= 64 };
  }
  return null;
}

export function sameControl(
  a: MidiControl | null,
  b: MidiControl | null,
): boolean {
  if (!a || !b || a.kind !== b.kind || a.data1 !== b.data1) return false;
  if (a.kind === "realtime") return true;
  return a.channel === (b as { channel: number }).channel;
}

/** Human-readable name for a captured button, e.g. "CC 118 · ch 1". */
export function controlLabel(c: MidiControl | null): string {
  if (!c) return "not set";
  if (c.kind === "realtime") {
    if (c.data1 === RT_START) return "MIDI Start";
    if (c.data1 === RT_CONTINUE) return "MIDI Continue";
    return "MIDI Stop";
  }
  const ch = ` · ch ${c.channel + 1}`;
  return (c.kind === "cc" ? `CC ${c.data1}` : `Note ${c.data1}`) + ch;
}

/** Narrow an untrusted value (parsed from localStorage) to a MidiControl. */
export function asControl(value: unknown): MidiControl | null {
  if (!value || typeof value !== "object") return null;
  const v = value as Record<string, unknown>;
  if (typeof v.data1 !== "number") return null;
  if (v.kind === "realtime") return { kind: "realtime", data1: v.data1 };
  if ((v.kind === "cc" || v.kind === "note") && typeof v.channel === "number") {
    return { kind: v.kind, channel: v.channel, data1: v.data1 };
  }
  return null;
}

/** Read a saved binding out of a parsed device config. */
export function asBinding(value: unknown): TransportBinding {
  const v = (value ?? {}) as Record<string, unknown>;
  return { start: asControl(v.start), stop: asControl(v.stop) };
}
