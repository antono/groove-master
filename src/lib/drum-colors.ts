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
  // The rest of the cymbals share the hat's hue, because they are the same
  // family and there are only three. Leaving them to the fallback made a drum's
  // colour depend on how many lanes the *lesson* had: a crash was the hat hue in
  // "Crash on 1" (top lane) and the snare's in "Crash, then Ride" (second lane),
  // which is precisely what a hue-by-family map exists to prevent.
  [49, FAMILY_HUES[0]], // crash
  [51, FAMILY_HUES[0]], // ride
  [52, FAMILY_HUES[0]], // china
  [53, FAMILY_HUES[0]], // ride bell
  [55, FAMILY_HUES[0]], // splash
  [57, FAMILY_HUES[0]], // crash 2
  [59, FAMILY_HUES[0]], // ride 2
]);

export function laneColor(note: number, laneIndex: number): string {
  const fallback =
    FAMILY_HUES[
      ((laneIndex % FAMILY_HUES.length) + FAMILY_HUES.length) %
        FAMILY_HUES.length
    ];
  return familyHue.get(note) ?? fallback;
}
