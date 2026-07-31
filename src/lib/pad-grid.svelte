<script lang="ts">
	import { noteName } from '$lib/note';

	type Props = {
		cols: number;
		rows: number;
		/** captured MIDI note per pad (L→R, T→B); null = not yet captured */
		captured: (number | null)[];
		/** index of the pad currently awaiting a press, or -1 when not capturing */
		captureIndex?: number;
		/** pad index to flash as "hit" (visual echo of a press) */
		hitIndex?: number | null;
		/** click a captured pad to preview it */
		onpreview?: (index: number) => void;
	};

	let { cols, rows, captured, captureIndex = -1, hitIndex = null, onpreview }: Props = $props();

	const total = $derived(cols * rows);

	function padState(i: number): 'pending' | 'current' | 'done' {
		if (captured[i] != null) return 'done';
		if (i === captureIndex) return 'current';
		return 'pending';
	}
</script>

<div
	class="grid"
	style="grid-template-columns: repeat({cols}, minmax(0, 1fr));"
	role="group"
	aria-label="Pad grid {cols} by {rows}"
>
	{#each Array(total) as _, i (i)}
		{@const st = padState(i)}
		<button
			type="button"
			class="pad"
			data-state={st}
			data-hit={hitIndex === i}
			disabled={st !== 'done' || !onpreview}
			aria-label={'Pad ' +
				(i + 1) +
				(captured[i] != null ? ' — ' + noteName(captured[i] as number) : ', not set')}
			onclick={() => onpreview?.(i)}
		>
			<span class="num">{i + 1}</span>
			{#if st === 'done'}
				<span class="note">{noteName(captured[i] as number)}</span>
			{:else if st === 'current'}
				<span class="press">press</span>
			{:else}
				<span class="dot">·</span>
			{/if}
		</button>
	{/each}
</div>

<style>
	.grid {
		display: grid;
		gap: 0.9rem;
		width: 100%;
		max-width: var(--pad-grid-max, 420px);
		margin: 0 auto;
	}

	/* Soft, extruded pad surface: paired light/dark shadows so it reads as
	   "raised"; pressing inverts to inset. */
	.pad {
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
	.pad:hover:not(:disabled) {
		background: var(--surface-2);
		border-color: var(--cyan-dim);
	}

	.pad:disabled {
		cursor: default;
		opacity: 1;
	}

	.pad[data-state='pending'] {
		opacity: 0.5;
	}

	.pad[data-state='current'] {
		opacity: 1;
		border-color: var(--gold);
		animation: pad-pulse 1.4s ease-in-out infinite;
	}

	.pad[data-state='done'] {
		border-color: var(--green-dim);
	}

	.pad[data-state='done']:not(:disabled) {
		cursor: pointer;
	}

	.pad[data-hit='true'],
	.pad[data-state='done']:not(:disabled):active {
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

	@media (prefers-reduced-motion: reduce) {
		.pad,
		.pad[data-state='current'] {
			animation: none;
			transition: none;
		}
	}

	.num {
		font-size: 0.75rem;
		font-weight: 600;
		color: var(--text-faint);
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
</style>
