# Note-highway jitter — root cause analysis

**Symptom.** The scrolling note highway stutters visibly on a Linux laptop,
slightly on an M1 Mac, and is perfectly smooth on an Android 9 Mi Pad 4 — a far
older and weaker device. Investigated 18–19 August 2026.

**Verdict.** Not an application bug. The scroll is delivered to the compositor
correctly and the machine fails to present it. The cause is **GPU power
management**: on battery, the integrated GPU idles at 300 MHz of a 950 MHz
ceiling with a 100 MHz floor, and a 60 Hz composite occasionally overruns the
16.7 ms deadline at that clock. One genuine code defect was found along the way
(an idle callback firing mid-run) and fixed, but it was not what was being seen.

**Status.** Strongly indicated, one confirmation outstanding — see
[Outstanding](#outstanding).

## Why this is hard to see

`startScroll()` in `src/routes/lessons/[id]/+page.svelte` hands the whole run to
the compositor as a single `linear` transform transition. There is no per-frame
JavaScript. That is the right design, and it means the usual suspects — GC,
reactivity, main-thread work — are excluded by construction.

What remains is **frame pacing**: whether frames are _presented_ at even
intervals, not whether they are produced fast enough. Constant-velocity motion of
high-contrast vertical marks is the most unforgiving stimulus for this. At 120 BPM
with `PX_PER_BEAT = 110` the strip moves ~3.7 CSS px per 60 Hz frame, so a frame
presented 4 ms late lands ~1 px off — a 25% velocity error the eye integrates as
wobble. The same error inside a fade is invisible. **The highway is a far more
sensitive jitter detector than anything else in the app**, which is why nothing
else looks broken while it does.

## The machine

|                |                                                  |
| -------------- | ------------------------------------------------ |
| GPU            | Intel Iris Xe (ADL GT2), Mesa 26.1.6, `i915`     |
| Kernel / shell | 6.18.40 / GNOME Shell 50.2, Wayland              |
| Panel          | `eDP-1`, 2560×1600 @ 60.000 Hz, internal, single |
| Display scale  | 1.6666666 (logical 1536×960), `dpr` 1.6667       |
| Browser        | Chrome 151.0.7922.71, `--ozone-platform=wayland` |

## What it was not

Every row was eliminated by measurement, not by argument.

| Hypothesis                                                   | Killed by                                                                                                                                                                                 |
| ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Software rendering / GPU blocklisted                         | `chrome://gpu`: compositing **and** rasterization hardware accelerated                                                                                                                    |
| Fractional scaling, device-pixel snapping                    | Still stutters at forced `dpr` 2. Measured steps were 3.02/3.04/3.06/3.08 device px — never integer, so motion is true subpixel                                                           |
| Floating-point precision                                     | No mechanism; the position deltas vary smoothly in the third decimal                                                                                                                      |
| Vsync clock mismatch with Mutter                             | Drops are **clustered**, not evenly spaced. A clock beat is periodic; this is bursty, which means work. Clean frames were tight at 16.62 ms mean                                          |
| Oversized composited layer / tile churn                      | The strip layer measured 1261 × ~52 px — smaller than a control that stayed smooth                                                                                                        |
| Repaints inside the animating layer                          | Disabling note `transition`, `box-shadow` and the `pop` animation changed nothing                                                                                                         |
| Layer fragmentation from `contain`                           | Removing `contain: layout paint` from `.note` changed nothing                                                                                                                             |
| The transform being overwritten mid-run                      | All four `updateStrip()` call sites are `togglePause`/`stop`/`finish`/`exitReport`; none run during a scroll. `beatPos` is a plain `let`, not `$state`, so the `$effect` does not re-fire |
| The note elements at all                                     | `display: none` on every `.note` — barlines alone still stutter                                                                                                                           |
| Chrome                                                       | Firefox stutters identically                                                                                                                                                              |
| Window mode                                                  | Fullscreen stutters identically                                                                                                                                                           |
| Direct Rendering Display Compositor disabled / ANGLE-over-GL | `--ozone-platform=x11` made no difference (see the caveat below)                                                                                                                          |

The dump does show `Direct Rendering Display Compositor: Disabled` and Vulkan off
(`'--ozone-platform=wayland' is not compatible with Vulkan`). Both are real, both
cost an extra per-frame copy, and neither is the cause.

## Root cause

A standalone static HTML file containing nothing but six independently animated
`<div>`s — no app, no audio, no framework — stutters on this machine, and **all
six hitch on the same frame**. Synchronous whole-surface misses across
independent layers means the frame is missing its presentation deadline, not that
any layer is doing too much work.

The power state at the time:

```
gt_cur_freq_mhz = 300      (min 100, max 950)
power profile   = balanced
governor        = powersave    EPP = balance_power
battery         = 43%, discharging
x86_pkg_temp    = 50C          <- not thermal; this is policy
```

A smooth 60 Hz scroll is a light but relentless workload: light enough that the
GPU governor never ramps, sustained enough that at 300 MHz a composite
occasionally misses the deadline. Power-state transitions are bursty, which
matches the clustering. Moving to AC power markedly reduced the drops.

This also explains the original ranking. The Mi Pad 4 pins clocks for a
foreground animating app and never downclocks mid-animation — old and slow, but
_consistent_, which is the only property constant-velocity scroll cares about.
The M1's GPU floor sits above what compositing needs. The laptop on battery drops
its iGPU to under a third of its ceiling.

### Two traps

`powerprofilesctl set performance` moves the **CPU** energy-performance
preference only. It leaves `gt_min_freq_mhz` at 100 and the GPU still idling at 300. Verify the GPU floor directly; do not infer it from the profile name.

On a Wayland session `--ozone-platform=x11` runs Chrome under **XWayland**, which
Mutter still composites. It changes the browser's windowing backend, not the
desktop compositing path — so it is not a test of the compositor hypothesis,
though it was used as one during this investigation.

## The one real code fix

`warmLessonSamples()` warms the service-worker cache on `requestIdleCallback`
with `{ timeout: 3000 }`. That timeout fires whether or not the page ever went
idle, so starting a run within three seconds of loading a lesson let a few dozen
fetches burst through the service worker mid-scroll.

It is now cancellable, cancels on lesson switch, bails if `playing || demoing`,
and is cancelled at the top of `play()` and `toggleListen()` — **before** their
awaits, since `playing` only goes true once the preload resolves. Nothing is
lost: `play()` already awaits a full preload of exactly those URLs, so a run
warms them itself.

Measured effect: **10 dropped rAF frames in 5.01 s → 1 in 291 frames.** Real, and
worth keeping. It was not the visible jitter.

## How to measure this again

Paste into the console **while a run is already scrolling** — starting early
fills the sample with stationary frames.

```js
(() => {
  const strip = document.querySelector(".strip");
  const f = [],
    xs = [];
  let t0 = 0;
  const x = () => new DOMMatrixReadOnly(getComputedStyle(strip).transform).m41;
  const tick = (t) => {
    if (!t0) t0 = t;
    f.push(t);
    xs.push(x());
    t - t0 < 5000 ? requestAnimationFrame(tick) : report();
  };
  function report() {
    const dt = f.slice(1).map((t, i) => t - f[i]);
    const dx = xs
      .slice(1)
      .map((v, i) => Math.abs(v - xs[i]) * devicePixelRatio);
    const moving = dx
      .map((v, i) => ({ v, dt: dt[i] }))
      .filter((m) => m.v > 0.01 && m.v < 100);
    console.log(
      "dpr",
      devicePixelRatio,
      "frames",
      f.length,
      "drops>20ms",
      moving.filter((m) => m.dt > 20).length,
      "devpx/frame",
      (moving.reduce((s, m) => s + m.v, 0) / moving.length).toFixed(3),
    );
    console.log(moving.map((m) => m.dt.toFixed(1)).join(" "));
  }
  requestAnimationFrame(tick);
})();
```

**This measures the main thread, not presentation.** A composited transform keeps
scrolling while the main thread stalls, and the reverse is also true — in the
final runs `rAF` held a steady 16.7 ms while Frame Rendering Stats showed heavy
red and yellow. Always corroborate with DevTools → Rendering → **Frame Rendering
Stats**, and with a Performance trace's **Frames** track.

Useful system checks:

```bash
cat /sys/class/drm/card1/gt_{min,max,cur,act}_freq_mhz   # GPU clock and floor
powerprofilesctl get                                     # CPU profile only
cat /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference
```

## Outstanding

Pin the GPU floor and re-test. This is the step that turns "strongly indicated"
into confirmed:

```bash
sudo tee /sys/class/drm/card1/gt_min_freq_mhz <<< 950   # restore with 100
```

If that removes the remaining drops, the durable fix is a udev rule raising the
floor to something modest — 300–450, not the full 950, which would cost battery
for no benefit:

```nix
services.udev.extraRules = ''
  ACTION=="add", SUBSYSTEM=="drm", KERNEL=="card*", ATTR{gt_min_freq_mhz}="450"
'';
```

If it changes nothing, the remaining suspect is Mutter's frame scheduling in
GNOME 50, and the next test is a different compositor — a large detour for
something that by then affects every animation on the machine equally.

## Method notes

Two process failures are worth recording, because both cost real time.

**A misread control measurement sent four rounds of investigation the wrong way.**
A control element running the same animation beside the highway was reported
smooth while the highway stuttered, which pointed hard at application code. The
standalone bisect later showed both were stuttering — the highway's denser,
higher-contrast marks simply made the same hitch far more visible. Everything
between those two observations was wasted.

**Eliminate from the outside in.** The sequence that actually worked was:
strip the app away entirely (static HTML) → strip the browser away (Firefox) →
strip the window manager away (fullscreen) → read the hardware state. Reaching
for CSS-level explanations first meant repeatedly predicting Blink's compositing
decisions, which is unreliable. Prefer a bisect that identifies a cause by
construction over a hypothesis that has to be right.
