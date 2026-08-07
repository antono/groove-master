// Hue by drum family, shared by the preview chart and the play highway so a pad
// is the same colour everywhere. Anything outside the common GM percussion falls
// back to cycling the accents by lane position.
//
// These are identity, not judgement: they say which drum a note is, and must
// stay clear of the colours that say how well it was hit. The --note-* tokens
// own the cool arc for exactly that reason — see the band rule in app.css
// before swapping any of them for a different hue.
export const FAMILY_HUES = ["var(--note-1)", "var(--note-2)", "var(--note-3)"];

const familyHue = new Map<number, string>([
  [35, FAMILY_HUES[2]], // acoustic bass drum
  [36, FAMILY_HUES[2]], // kick
  [38, FAMILY_HUES[1]], // snare
  [40, FAMILY_HUES[1]], // electric snare
  [42, FAMILY_HUES[0]], // closed hi-hat
  [44, FAMILY_HUES[0]], // pedal hi-hat
  [46, FAMILY_HUES[0]], // open hi-hat
]);

export function laneColor(note: number, laneIndex: number): string {
  const fallback =
    FAMILY_HUES[
      ((laneIndex % FAMILY_HUES.length) + FAMILY_HUES.length) %
        FAMILY_HUES.length
    ];
  return familyHue.get(note) ?? fallback;
}
