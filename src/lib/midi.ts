// Minimal Standard MIDI File parser — enough to drive the lessons highway.
//
// A lesson MIDI may hold several tracks. Their role is decided by the track
// name (FF 03 meta) and channel:
//   - "drums", or any track on the percussion channel (10) -> PLAYABLE:
//     these notes are shown on the highway and scored.
//   - "family:id" (e.g. "bass:lately")               -> BACKING:
//     auto-played from static/<family>/<id>/<note>.oga, never shown or scored.

export type MidiNote = { beat: number; note: number };
export type BackingTrack = { family: string; id: string; notes: MidiNote[] };

export type ParsedMidi = {
  ppq: number;
  bpm: number;
  notes: MidiNote[]; // playable (scored) notes
  backing: BackingTrack[]; // auto-played accompaniment
  lengthBeats: number;
};

export function parseMidi(buf: ArrayBuffer): ParsedMidi {
  const d = new DataView(buf);
  let p = 0;

  const tag = () =>
    String.fromCharCode(
      d.getUint8(p++),
      d.getUint8(p++),
      d.getUint8(p++),
      d.getUint8(p++),
    );
  const u32 = () => {
    const v = d.getUint32(p);
    p += 4;
    return v;
  };
  const u16 = () => {
    const v = d.getUint16(p);
    p += 2;
    return v;
  };

  if (tag() !== "MThd") throw new Error("Not a MIDI file");
  u32(); // header length (always 6)
  u16(); // format
  const ntracks = u16();
  const ppq = u16(); // assume metrical timing (positive)

  function varlen() {
    let v = 0;
    for (;;) {
      const b = d.getUint8(p++);
      v = (v << 7) | (b & 0x7f);
      if (!(b & 0x80)) break;
    }
    return v;
  }

  const playable: MidiNote[] = [];
  const backing: BackingTrack[] = [];
  let bpm = 120;
  let maxTick = 0;

  for (let t = 0; t < ntracks; t++) {
    if (tag() !== "MTrk") break;
    const len = u32();
    const end = p + len;
    let tick = 0;
    let running = 0;
    let name = "";
    let usesPercussion = false;
    const trackNotes: MidiNote[] = [];

    while (p < end) {
      tick += varlen();
      let statusByte = d.getUint8(p);
      if (statusByte & 0x80) p++;
      else statusByte = running; // running status
      running = statusByte;

      const cmd = statusByte & 0xf0;
      const chan = statusByte & 0x0f;
      if (statusByte === 0xff) {
        const type = d.getUint8(p++);
        const mlen = varlen();
        if (type === 0x03) {
          let s = "";
          for (let k = 0; k < mlen; k++)
            s += String.fromCharCode(d.getUint8(p + k));
          name = s;
        } else if (type === 0x51 && mlen === 3) {
          const us =
            (d.getUint8(p) << 16) |
            (d.getUint8(p + 1) << 8) |
            d.getUint8(p + 2);
          bpm = Math.round(60_000_000 / us);
        }
        p += mlen;
      } else if (statusByte === 0xf0 || statusByte === 0xf7) {
        p += varlen();
      } else if (cmd === 0x90) {
        const note = d.getUint8(p++);
        const vel = d.getUint8(p++);
        if (chan === 9) usesPercussion = true;
        if (vel > 0) trackNotes.push({ beat: tick / ppq, note });
        if (tick > maxTick) maxTick = tick;
      } else if (cmd === 0x80 || cmd === 0xa0 || cmd === 0xb0 || cmd === 0xe0) {
        p += 2;
      } else if (cmd === 0xc0 || cmd === 0xd0) {
        p += 1;
      } else {
        p++; // unknown — skip a byte defensively
      }
    }
    p = end;

    if (!trackNotes.length) continue;
    const colon = name.indexOf(":");
    if (colon > 0 && !usesPercussion) {
      // backing track: "family:id"
      backing.push({
        family: name.slice(0, colon).trim(),
        id: name.slice(colon + 1).trim(),
        notes: trackNotes.sort((a, b) => a.beat - b.beat),
      });
    } else {
      playable.push(...trackNotes);
    }
  }

  playable.sort((a, b) => a.beat - b.beat);
  // Round the length up to a whole bar (4 beats) so the loop stays musical.
  const lengthBeats = Math.max(4, Math.ceil(maxTick / ppq / 4) * 4);
  return { ppq, bpm, notes: playable, backing, lengthBeats };
}
