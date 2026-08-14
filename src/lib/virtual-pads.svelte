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
		overlay = false,
		keys = false,
		lanes = []
	}: {
		controller: Controller;
		onhit: (gm: number) => void;
		lit?: Set<number>;
		overlay?: boolean;
		/** Show the keyboard key on each pad — only meaningful for the keyboard source. */
		keys?: boolean;
		/** GM notes the current lesson uses, so those pads read as the ones to play. */
		lanes?: number[];
	} = $props();

	const cols = $derived(controller.geometry.kind === 'grid' ? controller.geometry.cols : 4);
	const used = $derived(new Set(lanes));

	function hit(e: PointerEvent, gm: number) {
		e.preventDefault();
		onhit(gm);
	}
</script>

<div
	class="pads"
	class:overlay
	style="grid-template-columns: repeat({cols}, 1fr)"
	role="group"
	aria-label="On-screen drum pads"
>
	{#each controller.pads as pad, i (pad.id)}
		<button
			class="pad"
			class:lit={lit.has(pad.sound)}
			class:used={used.has(pad.sound)}
			class:idle={used.size > 0 && !used.has(pad.sound)}
			data-role={pad.role}
			style="--pad-color: {laneColor(pad.sound, i)}"
			onpointerdown={(e) => hit(e, pad.sound)}
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
		gap: 0.5rem;
		width: 100%;
		touch-action: none;
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
		/* The pad wears its drum's colour — the same hue the note lanes use, so a pad
		   reads as the note it plays. A tint on the face, the full colour on press. */
		border: 1px solid color-mix(in srgb, var(--pad-color) 55%, transparent);
		border-radius: 0.6rem;
		background: color-mix(in srgb, var(--pad-color) 14%, var(--surface-2, #26262b));
		color: var(--text, #e8e8ea);
		font: inherit;
		cursor: pointer;
		user-select: none;
		-webkit-user-select: none;
		touch-action: none;
		transition: transform 0.04s ease, background 0.08s ease;
	}

	.pad:active,
	.pad.lit {
		background: var(--pad-color);
		border-color: var(--pad-color);
		color: #10131a;
		transform: scale(0.97);
	}

	/* The pads the lesson actually asks for stand out; the rest recede so a beginner
	   sees at a glance which to play, without the others disappearing entirely. */
	.pad.used {
		border-width: 2px;
		box-shadow: 0 0 0 1px color-mix(in srgb, var(--pad-color) 45%, transparent);
	}

	.pad.idle {
		opacity: 0.5;
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
</style>
