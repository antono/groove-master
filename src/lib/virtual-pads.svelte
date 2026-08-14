<script lang="ts">
	// The on-screen pad grid — the touch source's instrument, and the only way to
	// play a lesson on a phone or tablet with no Web MIDI. A tap resolves straight
	// to the pad's GM note and is dispatched exactly like a MIDI hit; the fire is on
	// `pointerdown` (attack on press, not release). `touch-action: none` plus
	// `preventDefault` kill the synthetic-click delay, double-tap zoom and
	// scroll-on-drag so a fast two-hand pattern doesn't pan the page.
	import type { Controller } from '$lib/controller.svelte';
	import { keyLabelFor } from '$lib/virtual-input';
	import { laneColor } from '$lib/drum-colors';

	let {
		controller,
		onhit,
		lit = new Set<number>(),
		cue = new Set<number>(),
		overlay = false,
		compact = false,
		keys = false,
		lanes = []
	}: {
		controller: Controller;
		onhit: (gm: number) => void;
		lit?: Set<number>;
		/** GM notes with a target approaching the hit line — pads to light "get ready". */
		cue?: Set<number>;
		overlay?: boolean;
		/** Schematic size, to sit beside the chart in the Listen block like a device preview. */
		compact?: boolean;
		/** Show the keyboard key on each pad — only meaningful for the keyboard source. */
		keys?: boolean;
		/** GM notes the current lesson uses, so those pads read as the ones to play. */
		lanes?: number[];
	} = $props();

	const used = $derived(new Set(lanes));
	// A note's position in the lesson's lanes — the same index the chart and highway
	// colour it by, so a pad comes out the exact colour of its note.
	const laneOf = $derived(new Map(lanes.map((n, idx) => [n, idx])));

	// The pad's colour, identical to the note's on the chart: `laneColor` keyed by
	// this sound's lane index when the lesson uses it, falling back to the pad's own
	// position for pads the lesson never plays (which have no note to match).
	function padColor(sound: number, i: number): string {
		return laneColor(sound, laneOf.get(sound) ?? i);
	}

	// A pad struck a moment ago — its own brief flash, so a press blinks the note's
	// colour and returns, independent of the (longer) scored-hit `lit` state.
	let struck = $state<Set<string>>(new Set());
	const flashTimers = new Map<string, ReturnType<typeof setTimeout>>();

	function hit(e: PointerEvent, gm: number, id: string) {
		// Attack on press. preventDefault stops the tap turning into a synthetic
		// click, a text selection, or a focus scroll — the pad only ever plays.
		e.preventDefault();
		// A tapped button keeps focus and would sit there looking "selected"; release
		// it so the only lasting state is the note colour.
		(e.currentTarget as HTMLElement | null)?.blur?.();
		onhit(gm);
		// Blink: on for one frame, off again. The 20ms CSS transition eases both
		// edges, so a press is a quick pulse, never a stuck highlight.
		struck = new Set(struck).add(id);
		clearTimeout(flashTimers.get(id));
		flashTimers.set(
			id,
			setTimeout(() => {
				struck = new Set([...struck].filter((x) => x !== id));
			}, 20)
		);
	}

	// A pad is an instrument, not a document: no right-click / long-press menu,
	// ever, so a fast repeated tap can never surface one.
	function noMenu(e: Event) {
		e.preventDefault();
	}
</script>

<div
	class="pads"
	class:overlay
	class:compact
	role="group"
	aria-label="On-screen drum pads"
	oncontextmenu={noMenu}
>
	{#each controller.pads as pad, i (pad.id)}
		<button
			class="pad"
			class:lit={lit.has(pad.sound)}
			class:struck={struck.has(pad.id)}
			class:cue={cue.has(pad.sound)}
			class:used={used.has(pad.sound)}
			class:idle={used.size > 0 && !used.has(pad.sound)}
			data-role={pad.role}
			style="--pad-color: {padColor(pad.sound, i)}"
			onpointerdown={(e) => hit(e, pad.sound, pad.id)}
			aria-label={pad.label}
		>
			<span class="label">{pad.label}</span>
			{#if keys && keyLabelFor(i)}<span class="key">{keyLabelFor(i)}</span>{/if}
		</button>
	{/each}
</div>

<style>
	.pads {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 0.5rem;
		width: 100%;
		/* The grid is an instrument surface: no scrolling, zooming, selecting or
		   long-press callouts — only taps. */
		touch-action: none;
		user-select: none;
		-webkit-user-select: none;
		-webkit-touch-callout: none;
	}

	/* On a narrow screen the pads go two-up and square — big, honest targets for a
	   thumb rather than a cramped row of slivers. Not in compact: there the grid is
	   a fixed-size schematic beside the chart, and shrinks with it instead. */
	@media (max-width: 560px) {
		.pads:not(.overlay):not(.compact) {
			grid-template-columns: repeat(2, 1fr);
		}
		.pads:not(.overlay):not(.compact) .pad {
			aspect-ratio: 1;
			min-height: 0;
		}
	}

	/* Compact — a small square schematic that sits beside the chart in the Listen
	   block, mirroring the drum-controller preview's dimensions so a virtual source
	   reads like any other device, coloured and named and still tappable. */
	.pads.compact {
		grid-template-columns: repeat(3, var(--pad-sz, 2.6rem));
		grid-auto-rows: var(--pad-sz, 2.6rem);
		gap: 0.3rem;
		width: max-content;
	}

	.pads.compact .pad {
		min-height: 0;
		padding: 0.15rem;
		border-radius: var(--radius-sm, 0.4rem);
		gap: 0.05rem;
	}

	.pads.compact .label {
		font-size: 0.5rem;
		line-height: 1.05;
	}

	.pads.compact .key {
		font-size: 0.5rem;
	}

	/* On a phone the schematic goes 2×3 — vertical, so six pads still fit beside the
	   chart without spilling off the edge. */
	@media (max-width: 46rem) {
		.pads.compact {
			grid-template-columns: repeat(2, var(--pad-sz));
			--pad-sz: 1.9rem;
			gap: 0.22rem;
		}
		.pads.compact .label {
			font-size: 0.44rem;
		}
	}

	.pad {
		/* A comfortable minimum target so a fast tap doesn't miss on a phone. */
		min-height: 4.5rem;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 0.15rem;
		padding: 0.5rem;
		/* The pad IS its note: the exact same colour the chart and highway paint the
		   note, so a pad and its note read as one thing. */
		border: 1px solid var(--pad-color);
		border-radius: 0.6rem;
		background: var(--pad-color);
		color: #10131a;
		font: inherit;
		cursor: pointer;
		/* Kill everything a press could do besides play: text selection, the tap
		   highlight flash, drag-out, and the iOS long-press callout. */
		user-select: none;
		-webkit-user-select: none;
		-webkit-touch-callout: none;
		-webkit-tap-highlight-color: transparent;
		-webkit-user-drag: none;
		touch-action: none;
		/* 20ms both edges: a press eases in and back out as a quick pulse. */
		transition: transform 0.02s ease, filter 0.02s ease, box-shadow 0.02s ease;
	}

	/* A tap must leave nothing behind — no focus ring sitting there looking selected.
	   (The pads are played by touch and by their keys, never tabbed to, so there is
	   no keyboard-focus affordance to lose.) */
	.pad:focus {
		outline: none;
	}

	/* The global button :hover/:active would repaint the pad grey and nudge it — and
	   on a touchscreen those states STICK until you tap elsewhere, which is exactly
	   the pad "staying selected" after release. A pad is always its note colour; the
	   only press feedback is the brief struck/lit pulse below. */
	.pad:hover:not(:disabled),
	.pad:active:not(:disabled) {
		background: var(--pad-color);
		border-color: var(--pad-color);
		transform: none;
	}

	/* Struck (own brief press pulse) or lit (a scored/keyboard hit): the note-coloured
	   pad brightens and lifts, keeping its hue — never a different, sticky colour. */
	.pad.struck,
	.pad.lit {
		filter: brightness(1.35);
		transform: scale(0.96);
		box-shadow: 0 0 0.6rem color-mix(in srgb, var(--pad-color) 70%, transparent);
	}

	/* The pads the lesson actually asks for stand out; the rest recede so a beginner
	   sees at a glance which to play, without the others disappearing entirely. */
	.pad.used {
		outline: 2px solid var(--text, #e8e8ea);
		outline-offset: 1px;
	}

	.pad.idle {
		opacity: 0.4;
	}

	/* Get-ready cue: a note for this pad is nearing the hit line. A bright ring and
	   glow say "this one next", ahead of the strike so a finger has time to move. A
	   cued pad is never idle — it is exactly the one to play. */
	.pad.cue {
		outline: 3px solid #fff;
		outline-offset: -1px;
		box-shadow: 0 0 0.9rem color-mix(in srgb, var(--pad-color) 65%, white);
		opacity: 1;
	}

	.label {
		font-weight: 600;
		font-size: 0.9rem;
		text-align: center;
	}

	.key {
		font-size: 0.65rem;
		opacity: 0.55;
		font-variant: small-caps;
		letter-spacing: 0.05em;
	}

	/* During a run the grid floats over the highway, low and wide, so the scrolling
	   notes stay visible while the student taps. */
	.overlay {
		position: fixed;
		left: 0;
		right: 0;
		bottom: 0;
		/* Above the fullscreen highway (z-index 50) so the pads are visible and
		   tappable during a run, not painted over by the track. */
		z-index: 60;
		gap: 0.35rem;
		padding: 0.5rem max(0.5rem, env(safe-area-inset-left)) calc(0.5rem + env(safe-area-inset-bottom));
		background: color-mix(in srgb, var(--bg, #16161a) 82%, transparent);
		backdrop-filter: blur(4px);
	}

	.overlay .pad {
		min-height: 3.25rem;
	}

	/* On a narrow screen the pad bar goes 2×3 — vertical — matching the Listen-block
	   preview so the same six pads sit the same way in both places. */
	@media (max-width: 46rem) {
		.overlay {
			grid-template-columns: repeat(2, 1fr);
		}
	}

	/* And when that screen is also tall, the pads grow into the lower half the
	   pushed-up strip freed. */
	@media (orientation: portrait) {
		.overlay .pad {
			min-height: min(15vh, 7rem);
		}
	}
</style>
