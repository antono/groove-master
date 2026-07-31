// Melodic feedback for pad capture.
//
// As the user presses pads left→right, top→bottom, we play a descending
// A-natural-minor scale so the first (top-left) pad is the highest note and the
// last (bottom-right) pad is the lowest — a pleasant "waterfall" that makes the
// otherwise-tedious mapping feel musical. Pure WebAudio (no samples needed).

// A natural minor descending from A5, enough degrees for a 4×4 grid (16 pads):
// A5 G5 F5 E5 D5 C5 B4 A4 G4 F4 E4 D4 C4 B3 A3 G3
const A_MINOR_DESCENDING = [
  81, 79, 77, 76, 74, 72, 71, 69, 67, 65, 64, 62, 60, 59, 57, 55,
];

const midiToFreq = (m: number) => 440 * Math.pow(2, (m - 69) / 12);

let ctx: AudioContext | null = null;

function audio(): AudioContext | null {
  if (typeof window === "undefined") return null;
  if (!ctx) ctx = new AudioContext();
  return ctx;
}

/** Resume the context after a user gesture (autoplay policy). */
export async function unlockAudio() {
  await audio()?.resume();
}

/**
 * Play the scale degree for pad `index` within a grid of `total` pads.
 * The scale is stretched/clamped so it always descends across the whole grid.
 */
export function playScaleTone(index: number, total: number) {
  const ac = audio();
  if (!ac) return;

  // Map pad index onto the descending scale; for grids smaller than 16 we
  // sample evenly so the top pad is highest and the bottom pad is lowest.
  const span = Math.min(total, A_MINOR_DESCENDING.length);
  const pos = total <= 1 ? 0 : Math.round((index / (total - 1)) * (span - 1));
  const note = A_MINOR_DESCENDING[Math.max(0, Math.min(span - 1, pos))];
  playFreq(ac, midiToFreq(note));
}

/** Simple plucked-ish tone with a soft attack/decay envelope. */
function playFreq(ac: AudioContext, freq: number) {
  const now = ac.currentTime;
  const osc = ac.createOscillator();
  const gain = ac.createGain();
  const osc2 = ac.createOscillator();

  osc.type = "triangle";
  osc2.type = "sine";
  osc.frequency.value = freq;
  osc2.frequency.value = freq * 2; // gentle upper octave for shimmer

  gain.gain.setValueAtTime(0.0001, now);
  gain.gain.exponentialRampToValueAtTime(0.22, now + 0.012);
  gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.5);

  osc.connect(gain);
  osc2.connect(gain);
  gain.connect(ac.destination);

  osc.start(now);
  osc2.start(now);
  osc.stop(now + 0.55);
  osc2.stop(now + 0.55);
}
