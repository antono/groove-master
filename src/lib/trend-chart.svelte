<script module lang="ts">
	// A single-series time trend, drawn as an SVG line over a recessive grid.
	//
	// One series per chart on purpose: BPM, timing error and accuracy are three
	// different scales, and overlaying them would mean a second y-axis. Three
	// small charts sharing one x-range say the same thing without the axis the
	// reader has to decode.
	//
	// Width comes from the element, not a viewBox, so strokes and text keep their
	// intended size instead of being scaled by preserveAspectRatio.

	export type TrendPoint = {
		/** Position on the time axis (epoch ms). */
		x: number;
		/** Value on the y axis, already in `unit`. */
		y: number;
		/** Tooltip heading, e.g. "Mar 14". */
		label: string;
		/** Tooltip second line — what the point is averaged over. */
		detail?: string;
	};
</script>

<script lang="ts">
	let {
		points,
		title,
		unit,
		color,
		format,
		height = 190,
		hint = '',
		onselect
	}: {
		points: TrendPoint[];
		title: string;
		unit: string;
		color: string;
		/** Overrides the step-derived default (see `fmt`). */
		format?: (v: number) => string;
		height?: number;
		hint?: string;
		/** Given, the plot becomes clickable and reports the point picked. */
		onselect?: (point: TrendPoint) => void;
	} = $props();

	const uid = $props.id();

	const PAD = { top: 14, right: 14, bottom: 22, left: 46 };
	const DOT = 4; // radius; 8px across, the floor for a hoverable marker
	// Past this many points the markers merge into a smear, so the line carries the
	// shape alone and only the hovered point gets a dot.
	const MAX_DOTS = 45;

	let width = $state(0);

	const plotW = $derived(Math.max(0, width - PAD.left - PAD.right));
	const plotH = $derived(Math.max(0, height - PAD.top - PAD.bottom));

	/** Round a value domain out to friendly tick boundaries. */
	function niceScale(
		lo: number,
		hi: number
	): { min: number; max: number; step: number; ticks: number[] } {
		if (!Number.isFinite(lo) || !Number.isFinite(hi))
			return { min: 0, max: 1, step: 1, ticks: [0, 1] };
		// A flat series has no range of its own — give it one so the line sits
		// mid-plot instead of collapsing onto an edge.
		if (hi - lo < 1e-9) {
			lo -= Math.abs(lo) * 0.1 || 1;
			hi += Math.abs(hi) * 0.1 || 1;
		}
		const raw = (hi - lo) / 3;
		const mag = Math.pow(10, Math.floor(Math.log10(raw)));
		const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= raw) ?? 10 * mag;
		const min = Math.floor(lo / step) * step;
		const max = Math.ceil(hi / step) * step;
		const ticks: number[] = [];
		// Accumulate in integer multiples: repeated += step drifts on values like 2.5.
		for (let i = 0; min + i * step <= max + step * 1e-6; i++) ticks.push(min + i * step);
		return { min, max, step, ticks };
	}

	const yScale = $derived(
		niceScale(Math.min(...points.map((p) => p.y)), Math.max(...points.map((p) => p.y)))
	);

	// Enough decimals to keep every tick distinct. Rounding to integers is right
	// for a BPM axis and wrong for a 0–2 minute one, where it prints "0 1 1 2".
	const fmt = $derived(
		format ??
			((v: number) => v.toFixed(yScale.step >= 1 ? 0 : Math.ceil(-Math.log10(yScale.step))))
	);

	// Time axis. A single point has no span, so it is pinned mid-plot rather than
	// dividing by a zero range.
	const xMin = $derived(points.length ? points[0].x : 0);
	const xMax = $derived(points.length ? points[points.length - 1].x : 1);

	const xAt = $derived((x: number) =>
		xMax === xMin ? PAD.left + plotW / 2 : PAD.left + ((x - xMin) / (xMax - xMin)) * plotW
	);
	const yAt = $derived(
		(y: number) =>
			PAD.top + plotH - ((y - yScale.min) / (yScale.max - yScale.min || 1)) * plotH
	);

	const coords = $derived(points.map((p) => ({ ...p, cx: xAt(p.x), cy: yAt(p.y) })));
	const path = $derived(coords.map((c, i) => `${i ? 'L' : 'M'}${c.cx} ${c.cy}`).join(' '));

	const dateFmt = new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric' });

	// Hover: nearest point on the x axis, so the whole plot height is a hit target
	// rather than the dot itself.
	let active: number | null = $state(null);

	function onMove(event: PointerEvent) {
		if (!coords.length) return;
		const rect = (event.currentTarget as HTMLElement).getBoundingClientRect();
		const x = event.clientX - rect.left;
		let best = 0;
		for (let i = 1; i < coords.length; i++) {
			if (Math.abs(coords[i].cx - x) < Math.abs(coords[best].cx - x)) best = i;
		}
		active = best;
	}

	function onKey(event: KeyboardEvent) {
		if (!onselect || !coords.length) return;
		if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
			const step = event.key === 'ArrowRight' ? 1 : -1;
			// From cold, an arrow starts at the newest point — the end of a trend is
			// what the reader is looking at.
			const from = active ?? (step > 0 ? -1 : coords.length);
			active = Math.max(0, Math.min(coords.length - 1, from + step));
			event.preventDefault();
		} else if (event.key === 'Enter' || event.key === ' ') {
			if (active != null) {
				onselect(coords[active]);
				event.preventDefault();
			}
		} else if (event.key === 'Escape') {
			active = null;
		}
	}

	const hovered = $derived(active != null ? coords[active] : null);
	// Flip the tooltip to the left of the cursor near the right edge so it never
	// spills out of the card.
	const tipRight = $derived(hovered ? hovered.cx > PAD.left + plotW * 0.6 : false);
</script>

<figure class="chart">
	<figcaption>
		<span class="title">{title}</span>
		<span class="unit">{unit}</span>
		{#if hint}<span class="hint">{hint}</span>{/if}
	</figcaption>

	<!-- The plot itself is a picture; when `onselect` is given, a transparent
	     button is laid over it to carry the interaction. That keeps the role
	     static (a real <button>, so focus, Enter and Space come for free) instead
	     of a div that changes role at runtime, and leaves the size binding on a
	     plain container. Pointer events bubble from the overlay, so hover still
	     drives the tooltip. -->
	<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
	<div
		class="plot"
		style="height: {height}px"
		bind:clientWidth={width}
		role="img"
		aria-label="{title} in {unit}, {points.length} points"
		onpointermove={onMove}
		onpointerleave={() => (active = null)}
	>
		{#if width > 0 && points.length}
			<svg {width} {height} aria-hidden="true">
				<defs>
					<linearGradient id="fade-{uid}" x1="0" y1="0" x2="0" y2="1">
						<stop offset="0%" style="stop-color: {color}" stop-opacity="0.22" />
						<stop offset="100%" style="stop-color: {color}" stop-opacity="0" />
					</linearGradient>
				</defs>

				{#each yScale.ticks as t (t)}
					<line class="grid" x1={PAD.left} x2={width - PAD.right} y1={yAt(t)} y2={yAt(t)} />
					<text class="axis" x={PAD.left - 8} y={yAt(t)} text-anchor="end" dominant-baseline="middle">
						{fmt(t)}
					</text>
				{/each}

				{#if coords.length > 1}
					<path
						d="{path} L{coords[coords.length - 1].cx} {PAD.top + plotH} L{coords[0]
							.cx} {PAD.top + plotH} Z"
						fill="url(#fade-{uid})"
					/>
				{/if}

				<path d={path} fill="none" style="stroke: {color}" stroke-width="2" stroke-linejoin="round"
					stroke-linecap="round" />

				{#if coords.length <= MAX_DOTS}
					{#each coords as c, i (i)}
						<!-- 2px surface ring keeps a dot legible where the line runs under it -->
						<circle cx={c.cx} cy={c.cy} r={DOT} style="fill: {color}" stroke="var(--surface)" stroke-width="2" />
					{/each}
				{/if}

				{#if hovered}
					<line class="crosshair" x1={hovered.cx} x2={hovered.cx} y1={PAD.top} y2={PAD.top + plotH} />
					<circle cx={hovered.cx} cy={hovered.cy} r={DOT + 2} style="fill: {color}" stroke="var(--surface)"
						stroke-width="2" />
				{/if}

				<text class="axis" x={PAD.left} y={height - 6}>{dateFmt.format(xMin)}</text>
				{#if xMax !== xMin}
					<text class="axis" x={width - PAD.right} y={height - 6} text-anchor="end">
						{dateFmt.format(xMax)}
					</text>
				{/if}
			</svg>

			{#if hovered}
				<div
					class="tip"
					class:left={tipRight}
					style="left: {hovered.cx}px; top: {Math.max(4, hovered.cy - 12)}px"
				>
					<strong>{fmt(hovered.y)} {unit}</strong>
					<span>{hovered.label}</span>
					{#if hovered.detail}<span class="detail">{hovered.detail}</span>{/if}
				</div>
			{/if}
		{:else if width > 0}
			<p class="empty">No runs in this range yet.</p>
		{/if}

		{#if onselect && points.length}
			<button
				type="button"
				class="hit"
				aria-label="Open a day from {title}. Arrow keys move between points, Enter opens the one selected."
				onclick={() => hovered && onselect(hovered)}
				onkeydown={onKey}
			></button>
		{/if}
	</div>
</figure>

<style>
	.chart {
		margin: 0;
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--radius);
		padding: 0.9rem 1rem 0.6rem;
	}

	figcaption {
		display: flex;
		align-items: baseline;
		gap: 0.5rem;
		margin-bottom: 0.35rem;
	}

	.title {
		font-weight: 650;
		font-size: 0.95rem;
		letter-spacing: -0.01em;
	}

	.unit,
	.hint {
		font-family: var(--font-mono);
		font-size: 0.72rem;
		color: var(--text-faint);
	}

	.hint {
		margin-left: auto;
	}

	.plot {
		position: relative;
		touch-action: pan-y;
	}

	/* Transparent interaction layer over the marks. Below the tooltip (z-index 2)
	   so it never covers it, above the svg so the click always lands. */
	.hit {
		position: absolute;
		inset: 0;
		z-index: 1;
		padding: 0;
		border: 0;
		background: none;
		cursor: pointer;
	}

	.hit:focus-visible {
		outline: 2px solid var(--gold);
		outline-offset: 3px;
		border-radius: var(--radius-sm);
	}

	svg {
		display: block;
		overflow: visible;
	}

	/* Grid and axis text stay recessive — the line is the only thing with weight. */
	.grid {
		stroke: var(--border);
		stroke-width: 1;
	}

	.crosshair {
		stroke: var(--border-strong);
		stroke-width: 1;
		stroke-dasharray: 3 3;
	}

	.axis {
		fill: var(--text-faint);
		font-family: var(--font-mono);
		font-size: 0.65rem;
	}

	.tip {
		position: absolute;
		transform: translate(0.6rem, -100%);
		pointer-events: none;
		display: flex;
		flex-direction: column;
		gap: 0.05rem;
		white-space: nowrap;
		background: var(--surface-3);
		border: 1px solid var(--border-strong);
		border-radius: var(--radius-sm);
		padding: 0.4rem 0.55rem;
		font-size: 0.75rem;
		line-height: 1.35;
		box-shadow: 0 6px 18px rgba(0, 0, 0, 0.45);
		z-index: 2;
	}

	.tip.left {
		transform: translate(-100%, -100%) translateX(-0.6rem);
	}

	/* Values and labels wear text tokens; the line beside them carries identity. */
	.tip strong {
		font-family: var(--font-mono);
		color: var(--text);
	}

	.tip span {
		color: var(--text-muted);
	}

	.tip .detail {
		color: var(--text-faint);
	}

	.empty {
		margin: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
		color: var(--text-faint);
		font-size: 0.85rem;
	}
</style>
