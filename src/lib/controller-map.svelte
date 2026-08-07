<!--
  A schematic of the student's own controller, laid out exactly as their pads
  are (the grid captured by the setup wizard, in the same left-to-right,
  top-to-bottom order they pressed them in).

  It sits beside the pattern chart so the two answer each other: the chart says
  *when*, the controller says *where*. Pads the lesson uses carry their drum's
  name in that drum's family hue — the same hue the chart and the highway give
  it — and the rest stay blank rather than hidden, so the picture keeps the
  shape of the real device. A pad lights the moment its drum sounds.
-->
<script lang="ts">
	import { laneColor } from '$lib/drum-colors';

	let {
		cols,
		rows,
		drums,
		lanes,
		lit,
		laneName = (n: number) => String(n)
	}: {
		cols: number;
		rows: number;
		/** GM drum note each pad triggers (L→R, T→B); null = pad not mapped */
		drums: (number | null)[];
		/** notes this lesson actually plays, in chart row order */
		lanes: number[];
		/** GM notes sounding right now */
		lit: Set<number>;
		laneName?: (note: number) => string;
	} = $props();

	const total = $derived(cols * rows);
	const laneRow = (note: number | null) => (note == null ? -1 : lanes.indexOf(note));

	// One sentence for a screen reader, since the grid itself is a picture.
	const summary = $derived.by(() => {
		const used = drums
			.map((note, i) => ({ note, i }))
			.filter(({ note }) => laneRow(note) >= 0)
			.map(({ note, i }) => `${laneName(note as number)} on pad ${i + 1}`);
		return used.length
			? `Your controller: ${used.join(', ')}. ${total - used.length} other pads unused.`
			: 'Your controller: no pad mapped to this lesson.';
	});
</script>

<div
	class="pads"
	style="grid-template-columns: repeat({cols}, var(--pad-sz));"
	role="img"
	aria-label={summary}
>
	{#each Array(total) as _, i (i)}
		{@const note = drums[i] ?? null}
		{@const row = laneRow(note)}
		<div
			class="pad"
			class:used={row >= 0}
			class:lit={note != null && lit.has(note)}
			style={row >= 0 ? `color: ${laneColor(note as number, row)}` : ''}
		>
			{#if row >= 0}<span class="name">{laneName(note as number)}</span>{/if}
		</div>
	{/each}
</div>

<style>
	.pads {
		--pad-sz: 2.6rem;
		display: grid;
		grid-auto-rows: var(--pad-sz);
		gap: 0.3rem;
	}

	.pad {
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
	.pad.used {
		border-color: currentColor;
		background: color-mix(in srgb, currentColor 14%, #101120);
	}

	/* Its drum is sounding right now — the pad flares and sinks, as if struck. */
	.pad.lit {
		background: currentColor;
		box-shadow: 0 0 10px currentColor;
		transform: scale(0.93);
	}

	.pad.lit .name {
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

	/* Too narrow to letter a pad. The hue does the work instead: it is the same one
	   the chart gives that lane an inch to the right, so the pairing still reads. */
	@media (max-width: 46rem) {
		.pads {
			--pad-sz: 1.9rem;
			gap: 0.22rem;
		}

		.name {
			display: none;
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.pad {
			transition: none;
		}

		.pad.lit {
			transform: none;
		}
	}
</style>
