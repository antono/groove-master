// MIDI note-number helpers.

const NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"];

/** e.g. 60 -> "C4" (scientific pitch, middle C = C4). */
export function noteName(m: number): string {
  if (m == null || Number.isNaN(m)) return "—";
  return NAMES[((m % 12) + 12) % 12] + (Math.floor(m / 12) - 1);
}
