<!--
  A schematic of a lesson's drum pattern: one row per pad, notes placed at their
  exact beat (so triplets and swing read correctly, unlike a step grid).

  Pure SVG with a viewBox, so it scales to the container and stays crisp. Used on
  the lessons catalogue as a preview of what the highway will throw at you.
-->
<script lang="ts">
	import type { MidiNote } from '$lib/midi';
	import { laneColor } from '$lib/drum-colors';

	let {
		notes,
		lanes,
		lengthBeats,
		laneName = (n: number) => String(n),
		beatsPerBar = 4,
		playhead = null
	}: {
		notes: MidiNote[];
		lanes: number[];
		lengthBeats: number;
		laneName?: (note: number) => string;
		beatsPerBar?: number;
		/** Beat the in-place preview has reached; null when nothing is playing. */
		playhead?: number | null;
	} = $props();

	// SVG user units; the whole chart scales from these.
	const LABEL_W = 84;
	const ROW_H = 20;
	const BEAT_W = 24;
	const HEAD_H = 14; // bar-number strip above the rows
	const PAD_R = 6;
	const NOTE_H = 11;

	// Notes are sized to the tightest subdivision in the pattern, so a run of 8ths
	// (or 16ths) reads as separate hits instead of one solid bar.
	const noteW = $derived.by(() => {
		const byLane = new Map<number, number[]>();
		for (const n of notes) {
			const beats = byLane.get(n.note);
			if (beats) beats.push(n.beat);
			else byLane.set(n.note, [n.beat]);
		}
		let gap = Infinity;
		for (const beats of byLane.values()) {
			beats.sort((a, b) => a - b);
			for (let i = 1; i < beats.length; i++) gap = Math.min(gap, beats[i] - beats[i - 1]);
		}
		if (!Number.isFinite(gap)) return 12;
		return Math.max(4, Math.min(12, gap * BEAT_W - 3));
	});

	// Beat 0 sits INSET past the row's left edge so a down-beat note isn't sliced
	// in half by the first bar line.
	const INSET = 8;
	const rowW = $derived(INSET + lengthBeats * BEAT_W + INSET);
	const w = $derived(LABEL_W + rowW + PAD_R);

	// Breathing room above the bar numbers and below the last lane. It lives inside
	// the viewBox so it scales with the chart instead of fighting the frame's padding.
	const PAD_Y = 10;
	const top = PAD_Y + HEAD_H; // first lane's top edge
	const bottom = $derived(top + lanes.length * ROW_H);
	const h = $derived(bottom + PAD_Y);

	const x = (beat: number) => LABEL_W + INSET + beat * BEAT_W;
	const row = (note: number) => lanes.indexOf(note);
	const rowY = (note: number) => top + row(note) * ROW_H;

	const barStarts = $derived(
		Array.from({ length: Math.ceil(lengthBeats / beatsPerBar) }, (_, i) => i * beatsPerBar)
	);
	const beatLines = $derived(Array.from({ length: Math.ceil(lengthBeats) }, (_, i) => i));
	// Eighths only — sixteenth gridlines turn into mush at this size.
	const eighths = $derived(
		Array.from({ length: Math.ceil(lengthBeats * 2) }, (_, i) => i / 2).filter(
			(b) => !Number.isInteger(b)
		)
	);

	// How long, in beats, a note stays "popped" after the playhead reaches it. Beat
	// units so the flash tracks the tempo — brief at speed, longer when slow.
	const POP_BEATS = 0.2;
	const isPlaying = (beat: number) =>
		playhead != null && beat <= playhead && playhead < beat + POP_BEATS;
</script>

<svg class="chart" viewBox="0 0 {w} {h}" role="img" aria-label="Pattern chart">
	{#each lanes as note, i (note)}
		<rect
			class="row"
			class:odd={i % 2 === 1}
			x={LABEL_W}
			y={rowY(note)}
			width={rowW}
			height={ROW_H}
		/>
		<text class="label" x={LABEL_W - 8} y={rowY(note) + ROW_H / 2}>{laneName(note)}</text>
	{/each}

	{#each eighths as beat (beat)}
		<line class="grid eighth" x1={x(beat)} x2={x(beat)} y1={top} y2={bottom} />
	{/each}
	{#each beatLines as beat (beat)}
		<line class="grid beat" x1={x(beat)} x2={x(beat)} y1={top} y2={bottom} />
	{/each}
	{#each barStarts as beat, i (beat)}
		<line class="grid bar" x1={x(beat)} x2={x(beat)} y1={top - 6} y2={bottom} />
		<text class="bar-no" x={x(beat) + 3} y={top - 5}>{i + 1}</text>
	{/each}
	<line class="grid bar" x1={x(lengthBeats)} x2={x(lengthBeats)} y1={top} y2={bottom} />

	{#if playhead != null}
		<line class="playhead" x1={x(playhead)} x2={x(playhead)} y1={top - 6} y2={bottom} />
	{/if}

	{#each notes as n, i (i)}
		{#if row(n.note) >= 0}
			<rect
				class="note"
				class:playing={isPlaying(n.beat)}
				x={x(n.beat) - noteW / 2}
				y={rowY(n.note) + (ROW_H - NOTE_H) / 2}
				width={noteW}
				height={NOTE_H}
				rx={Math.min(3, noteW / 3)}
				style="color: {laneColor(n.note, row(n.note))}"
				fill="currentColor"
			/>
		{/if}
	{/each}
</svg>

<style>
	.chart {
		display: block;
		width: 100%;
		height: auto;
	}

	.row {
		fill: #101120;
	}

	.row.odd {
		fill: #14152a;
	}

	.label {
		fill: var(--text-muted);
		font-family: var(--font-mono);
		font-size: 9px;
		text-anchor: end;
		dominant-baseline: middle;
	}

	.bar-no {
		fill: var(--text-faint);
		font-family: var(--font-mono);
		font-size: 8px;
	}

	.grid {
		stroke-width: 1;
		shape-rendering: crispEdges;
	}

	.grid.eighth {
		stroke: #1c1e33;
	}

	.grid.beat {
		stroke: #262943;
	}

	.grid.bar {
		stroke: #3d4060;
	}

	.note {
		opacity: 0.9;
		transform-box: fill-box;
		transform-origin: center;
		transition:
			transform 0.12s ease,
			opacity 0.12s ease,
			filter 0.12s ease;
	}

	/* Pops as the playhead reaches it during Listen — brighter, bigger, and glowing
	   in its own family hue. */
	.note.playing {
		opacity: 1;
		transform: scale(1.5);
		filter: brightness(1.25) drop-shadow(0 0 3px currentColor);
	}

	.playhead {
		stroke: var(--gold);
		stroke-width: 2;
		filter: drop-shadow(0 0 3px var(--gold-dim));
	}
</style>
