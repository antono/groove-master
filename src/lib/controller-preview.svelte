<!--
  The student's instrument, drawn from the Controller itself.

  This is the only thing in the app that draws pads. It replaced two components
  that each drew half of it — a capture grid in the wizard and a lesson-page
  schematic — written before there was a Controller to ask what the instrument
  was. Geometry comes from `controller.geometry`, so a 4×4 grid, an MD-90
  schematic and a custom kit are all this one component; the caller never picks
  a renderer.

  Three modes over the same geometry, so a pad is in the same place in setup as
  it is during a lesson:

    capture — one pad awaiting a press, captured pads showing their note
    map     — the lesson's drums named in their family hue, the rest blank
    play    — as map, sized up, shown during a run when there is room

  Pads the lesson doesn't use stay blank rather than hidden, so the picture
  keeps the shape of the real device.
-->
<script lang="ts">
  import { base } from '$app/paths';

  import type { Controller, Pad } from '$lib/controller.svelte';
  import { laneColor } from '$lib/drum-colors';
  import { noteName } from '$lib/note';

  type Mode = 'capture' | 'map' | 'play';

  let {
    controller,
    mode = 'map',
    /** capture: index of the pad awaiting a press, -1 when not capturing */
    captureIndex = -1,
    /** capture: pad index to flash as a visual echo of a press */
    hitIndex = null,
    /** map/play: the notes this lesson plays, in chart row order */
    lanes = [],
    /** map/play: GM notes sounding right now */
    lit = new Set<number>(),
    laneName = (n: number) => String(n),
    /** activate a captured pad to audition it */
    onpreview,
    size
  }: {
    controller: Controller;
    mode?: Mode;
    captureIndex?: number;
    hitIndex?: number | null;
    lanes?: number[];
    lit?: Set<number>;
    laneName?: (note: number) => string;
    onpreview?: (index: number) => void;
    size?: 'sm' | 'md' | 'lg';
  } = $props();

  const scale = $derived(size ?? (mode === 'map' ? 'sm' : 'lg'));
  const geometry = $derived(controller.geometry);
  const hatOpen = $derived(controller.hihatPosition === 'open');

  /**
   * A stateful hi-hat pad plays two notes, so it counts as "used" when the
   * lesson calls for either voice, and lights for either. Everything else is
   * simply its own sound.
   */
  function voices(pad: Pad): number[] {
    if (pad.role === 'hihat' && controller.hihat.mode === 'stateful') {
      return [controller.hihat.closed, controller.hihat.open];
    }
    // A two-note hi-hat is one drum wired to two notes; both are still it.
    if (pad.altNote != null) return [pad.sound, pad.altSound ?? 46];
    return [pad.sound];
  }

  type PadView = {
    pad: Pad;
    index: number;
    /** capture */
    state: 'pending' | 'current' | 'done';
    hit: boolean;
    /** map/play */
    row: number;
    lit: boolean;
    color: string | null;
    text: string;
  };

  const views = $derived.by<PadView[]>(() =>
    controller.pads.map((pad, index) => {
      const capture = mode === 'capture';
      const vs = voices(pad);
      // The lesson row this pad answers to, if any. A two-voice hi-hat takes
      // whichever of its voices the lesson actually calls for.
      const row = vs.reduce((best, n) => {
        const r = lanes.indexOf(n);
        return r >= 0 && (best < 0 || r < best) ? r : best;
      }, -1);
      const sounding = row >= 0 ? lanes[row] : pad.sound;
      return {
        pad,
        index,
        state: (pad.note != null
          ? 'done'
          : index === captureIndex
            ? 'current'
            : 'pending') as PadView['state'],
        hit: hitIndex === index,
        row,
        lit: !capture && vs.some((n) => lit.has(n)),
        color: !capture && row >= 0 ? laneColor(sounding, row) : null,
        // Before a drum is captured it says which drum it is, so the picture is
        // readable the moment it appears; afterwards it says what note it sends,
        // which is the thing you actually need to check.
        text: capture
          ? pad.note != null
            ? noteName(pad.note)
            : pad.label
          : row >= 0
            ? laneName(sounding)
            : ''
      };
    })
  );

  // One sentence for a screen reader, since the instrument itself is a picture.
  const summary = $derived.by(() => {
    if (mode === 'capture') {
      const done = views.filter((v) => v.state === 'done').length;
      return `${controller.name || 'Your controller'}: ${done} of ${views.length} pads mapped.`;
    }
    const used = views.filter((v) => v.row >= 0).map((v) => `${v.text} on ${v.pad.label}`);
    return used.length
      ? `Your controller: ${used.join(', ')}. ${views.length - used.length} other pads unused.`
      : 'Your controller: no pad mapped to this lesson.';
  });

  // --- schematic ------------------------------------------------------------
  //
  // The SVG is inlined so its drums can be marked by id. It is fetched from our
  // own static assets and nowhere else: inlining executes it as document
  // markup, so a submitted or user-supplied layout must never reach here.

  let svgText = $state('');
  let host = $state<HTMLDivElement | null>(null);

  $effect(() => {
    const src = geometry.kind === 'schematic' ? geometry.src : null;
    if (!src) {
      svgText = '';
      return;
    }
    let live = true;
    fetch(`${base}${src}`)
      .then((r) => (r.ok ? r.text() : ''))
      .then((t) => {
        if (live) svgText = t;
      })
      .catch(() => {
        // A missing schematic falls back to the neutral arrangement rather than
        // leaving the student with no picture at all.
        if (live) svgText = '';
      });
    return () => {
      live = false;
    };
  });

  /**
   * Mark up the inlined SVG. Attribute and class writes only — no measurement,
   * so this can run during a scrolling run without touching layout.
   */
  $effect(() => {
    const el = host;
    const vs = views;
    const open = hatOpen;
    if (!el || !svgText) return;
    for (const v of vs) {
      const g = el.querySelector<SVGGElement>(`#${CSS.escape(v.pad.id)}`);
      if (!g) continue;
      g.classList.toggle('used', v.row >= 0);
      g.classList.toggle('lit', v.lit);
      g.classList.toggle('current', mode === 'capture' && v.state === 'current');
      g.classList.toggle('captured', mode === 'capture' && v.state === 'done');
      g.classList.toggle('pending', mode === 'capture' && v.state === 'pending');
      g.classList.toggle('hit', v.hit);
      if (v.pad.role === 'hihat') g.classList.toggle('open', open);
      if (v.color) g.style.color = v.color;
      else g.style.removeProperty('color');
      const label = g.querySelector('.label');
      if (label) label.textContent = v.text;
    }
  });

  function onSchematicClick(event: MouseEvent) {
    if (!onpreview) return;
    const g = (event.target as Element | null)?.closest?.('.drum');
    if (!g?.id) return;
    const i = controller.pads.findIndex((p) => p.id === g.id);
    if (i >= 0 && controller.pads[i].note != null) onpreview(i);
  }

  // --- flat geometries ------------------------------------------------------

  const cols = $derived(
    geometry.kind === 'grid'
      ? geometry.cols
      : Math.max(1, Math.ceil(Math.sqrt(controller.pads.length || 1)))
  );
</script>

{#if geometry.kind === 'schematic' && svgText}
  <!--
    Clicking a drum auditions it. The keyboard path is the button list below,
    not this handler: drums are `<g>`s inside an inlined asset, so they cannot
    carry focus themselves.
  -->
  <!-- svelte-ignore a11y_click_events_have_key_events -->
  <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
  <div
    class="kit {mode} {scale}"
    bind:this={host}
    role="img"
    aria-label={summary}
    onclick={onSchematicClick}
  >
    <!-- first-party asset only; see the note above -->
    {@html svgText}
  </div>
  {#if mode === 'capture' && onpreview}
    <ul class="audition">
      {#each views.filter((v) => v.state === 'done') as v (v.pad.id)}
        <li>
          <button type="button" onclick={() => onpreview?.(v.index)}>
            {v.pad.label} — {v.text}
          </button>
        </li>
      {/each}
    </ul>
  {/if}
{:else if mode === 'capture'}
  <div
    class="grid capture {scale}"
    style="grid-template-columns: repeat({cols}, minmax(0, 1fr));"
    role="group"
    aria-label={summary}
  >
    {#each views as v (v.pad.id)}
      <button
        type="button"
        class="pad"
        data-state={v.state}
        data-hit={v.hit}
        disabled={v.state !== 'done' || !onpreview}
        aria-label="{v.pad.label}{v.pad.note != null ? ' — ' + noteName(v.pad.note) : ', not set'}"
        onclick={() => onpreview?.(v.index)}
      >
        <span class="num">{v.pad.label}</span>
        {#if v.state === 'done'}
          <span class="note">{v.text}</span>
        {:else if v.state === 'current'}
          <span class="press">press</span>
        {:else}
          <span class="dot">·</span>
        {/if}
      </button>
    {/each}
  </div>
{:else}
  <div
    class="pads {mode} {scale}"
    style="grid-template-columns: repeat({cols}, var(--pad-sz));"
    role="img"
    aria-label={summary}
  >
    {#each views as v (v.pad.id)}
      <div
        class="pad"
        class:used={v.row >= 0}
        class:lit={v.lit}
        style={v.color ? `color: ${v.color}` : ''}
      >
        {#if v.text}<span class="name">{v.text}</span>{/if}
      </div>
    {/each}
  </div>
{/if}

<style>
  /* --- map / play: the flat pad picture -------------------------------- */

  .pads {
    --pad-sz: 2.6rem;
    display: grid;
    grid-auto-rows: var(--pad-sz);
    gap: 0.3rem;
  }

  .pads.md {
    --pad-sz: 3.4rem;
  }

  .pads.lg {
    --pad-sz: 4.2rem;
  }

  .pads .pad {
    display: grid;
    place-items: center;
    padding: 0.15rem;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    background: #101120; /* the chart's own row fill, so the two read as one panel */
    transition:
      background-color 90ms ease,
      box-shadow 90ms ease,
      transform 90ms ease;
  }

  /* A pad this lesson calls for: tinted and outlined in its drum's family hue. */
  .pads .pad.used {
    border-color: currentColor;
    background: color-mix(in srgb, currentColor 14%, #101120);
  }

  /* Its drum is sounding right now — the pad flares and sinks, as if struck. */
  .pads .pad.lit {
    background: currentColor;
    box-shadow: 0 0 10px currentColor;
    transform: scale(0.93);
  }

  .pads .pad.lit .name {
    color: #0b0c16;
  }

  .name {
    font-family: var(--font-mono);
    font-size: 0.5rem;
    line-height: 1.15;
    text-align: center;
    text-wrap: balance;
    color: currentColor;
  }

  .pads.lg .name,
  .pads.md .name {
    font-size: 0.62rem;
  }

  /* Too narrow to letter a pad. The hue does the work instead: it is the same one
     the chart gives that lane an inch to the right, so the pairing still reads. */
  @media (max-width: 46rem) {
    .pads {
      --pad-sz: 1.9rem;
      gap: 0.22rem;
    }

    .pads .name {
      display: none;
    }
  }

  /* --- capture: the wizard's pads --------------------------------------- */

  .grid {
    display: grid;
    gap: 0.9rem;
    width: 100%;
    max-width: var(--pad-grid-max, 420px);
    margin: 0 auto;
  }

  /* Soft, extruded pad surface: paired light/dark shadows so it reads as
     "raised"; pressing inverts to inset. */
  .grid .pad {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.3rem;
    aspect-ratio: 1;
    padding: 0.5rem;
    border-radius: var(--radius);
    border: 1px solid transparent;
    background: var(--surface-2);
    box-shadow:
      6px 6px 16px var(--pad-shadow-dark),
      -6px -6px 14px var(--pad-shadow-light);
    font-family: var(--font-mono);
    color: var(--text);
    user-select: none;
    transition:
      box-shadow 160ms cubic-bezier(0.2, 0, 0, 1),
      transform 160ms cubic-bezier(0.2, 0, 0, 1),
      border-color 160ms ease,
      opacity 160ms ease;
  }

  /* override the global button hover — pads keep their own surface */
  .grid .pad:hover:not(:disabled) {
    background: var(--surface-2);
    border-color: var(--cyan-dim);
  }

  .grid .pad:disabled {
    cursor: default;
    opacity: 1;
  }

  .grid .pad[data-state='pending'] {
    opacity: 0.5;
  }

  .grid .pad[data-state='current'] {
    opacity: 1;
    border-color: var(--gold);
    animation: pad-pulse 1.4s ease-in-out infinite;
  }

  .grid .pad[data-state='done'] {
    border-color: var(--green-dim);
  }

  .grid .pad[data-state='done']:not(:disabled) {
    cursor: pointer;
  }

  .grid .pad[data-hit='true'],
  .grid .pad[data-state='done']:not(:disabled):active {
    transform: translateY(2px) scale(0.97);
    box-shadow:
      inset 5px 5px 12px var(--pad-shadow-dark),
      inset -4px -4px 10px var(--pad-shadow-light);
    border-color: var(--cyan);
  }

  @keyframes pad-pulse {
    0%,
    100% {
      box-shadow:
        0 0 0 3px var(--gold-dim),
        6px 6px 16px var(--pad-shadow-dark),
        -6px -6px 14px var(--pad-shadow-light);
    }
    50% {
      box-shadow:
        0 0 0 7px rgba(240, 192, 64, 0.12),
        6px 6px 16px var(--pad-shadow-dark),
        -6px -6px 14px var(--pad-shadow-light);
    }
  }

  .num {
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--text-faint);
    text-align: center;
  }

  .note {
    font-size: 1rem;
    font-weight: 700;
    color: var(--green);
  }

  .press {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--gold);
  }

  .dot {
    color: var(--text-faint);
  }

  /* --- schematic -------------------------------------------------------- */

  .kit {
    width: 100%;
    max-width: var(--kit-max, 420px);
    margin: 0 auto;
  }

  .kit.sm {
    --kit-max: 190px;
  }

  .kit.md {
    --kit-max: 300px;
  }

  .kit :global(svg) {
    display: block;
    width: 100%;
    height: auto;
  }

  /* The keyboard half of "click a drum to hear it": out of the way until
     tabbed to, then a normal row of buttons. */
  .audition {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    justify-content: center;
    margin: 0.75rem 0 0;
    padding: 0;
    list-style: none;
  }

  .audition button {
    padding: 0.15em 0.5em;
    font-family: var(--font-mono);
    font-size: 0.7rem;
    opacity: 0.55;
  }

  .audition button:hover,
  .audition button:focus-visible {
    opacity: 1;
  }

  /* The asset carries no colour of its own — all of it is here. */
  .kit :global(.body rect),
  .kit :global(.body path) {
    fill: var(--surface-2);
    stroke: var(--border);
    stroke-width: 1.5;
  }

  .kit :global(.body .grille),
  .kit :global(.body .panel) {
    fill: var(--surface-3);
    stroke: none;
  }

  .kit :global(.drum .rim) {
    fill: var(--surface-3);
    stroke: var(--border-strong);
    stroke-width: 1.5;
  }

  .kit :global(.drum .head) {
    fill: #101120;
    stroke: var(--border);
    stroke-width: 1;
    transition:
      fill 90ms ease,
      stroke 90ms ease;
  }

  .kit :global(.drum .hat-top) {
    fill: none;
    stroke: var(--border-strong);
    stroke-width: 1.5;
    transition: transform 140ms cubic-bezier(0.2, 0, 0, 1);
  }

  /* Pedal up: the top cymbal lifts, so the picture shows the pedal the student
     is actually holding. */
  .kit :global(.drum.open .hat-top) {
    transform: translateY(-7px);
  }

  .kit :global(.drum .label) {
    fill: var(--text-faint);
    font-family: var(--font-mono);
    font-size: 12px;
    text-anchor: middle;
    pointer-events: none;
  }

  /* used by this lesson */
  .kit :global(.drum.used .head) {
    fill: color-mix(in srgb, currentColor 18%, #101120);
    stroke: currentColor;
  }

  .kit :global(.drum.used .label) {
    fill: currentColor;
  }

  /* sounding right now */
  .kit :global(.drum.lit .head) {
    fill: currentColor;
    stroke: currentColor;
  }

  .kit :global(.drum.lit .label) {
    fill: #0b0c16;
  }

  /* capture states */
  .kit :global(.drum.pending .head) {
    opacity: 0.45;
  }

  .kit :global(.drum.current .head) {
    stroke: var(--gold);
    stroke-width: 2.5;
    animation: drum-pulse 1.4s ease-in-out infinite;
  }

  .kit :global(.drum.captured .head) {
    stroke: var(--green-dim);
  }

  .kit :global(.drum.captured .label) {
    fill: var(--green);
  }

  .kit :global(.drum.hit .head) {
    fill: var(--cyan);
  }

  @keyframes drum-pulse {
    50% {
      stroke: var(--gold-dim);
    }
  }

  /* Every animation here is decoration over a state that is already carried by
     colour, so switching them off loses nothing. */
  @media (prefers-reduced-motion: reduce) {
    .pads .pad,
    .grid .pad,
    .grid .pad[data-state='current'],
    .kit :global(.drum .head),
    .kit :global(.drum .hat-top) {
      animation: none;
      transition: none;
    }

    .pads .pad.lit {
      transform: none;
    }

    .kit :global(.drum.current .head) {
      animation: none;
    }
  }
</style>
