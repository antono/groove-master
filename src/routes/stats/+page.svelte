<script lang="ts">
	// Practice history. Everything on this page is read from IndexedDB
	// ($lib/stats) and aggregated per local calendar day: one lesson run is a
	// record, one day is a point.
	//
	// Three views of the same log. The heatmap answers "am I showing up?" — a
	// fixed 53-week window, so its shape is comparable week to week. The trends
	// answer "am I getting better?" — four single-series charts over a range the
	// reader picks, sharing one filter row so they always describe the same slice.
	// Picking a cell or a point opens the third: one day, run by run.

	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import TrendChart, { type TrendPoint } from '$lib/trend-chart.svelte';
	import { allSessions, clearSessions, dayKey, type SessionStat } from '$lib/stats';

	let sessions: SessionStat[] = $state([]);
	let loading = $state(true);

	onMount(async () => {
		// Today, resolved on the client so the day is the reader's local one.
		selectedDay = dayKey(new Date());
		sessions = await allSessions();
		loading = false;
	});

	// ---- per-day aggregation ---------------------------------------------

	type DayAgg = {
		key: string;
		runs: number;
		notes: number; // targets presented
		hits: number;
		bpmSum: number; // weighted below by runs, not by notes: tempo is a property
		errSum: number; // of the run, and a long lesson is not a "more true" tempo
		errRuns: number; // runs that landed at least one hit, so avgAbsMs means something
		playMs: number; // time actually played that day
		at: number; // first run of the day, the point's x
	};

	function aggregate(list: SessionStat[]): Map<string, DayAgg> {
		const days = new Map<string, DayAgg>();
		for (const s of list) {
			let d = days.get(s.day);
			if (!d) {
				d = {
					key: s.day,
					runs: 0,
					notes: 0,
					hits: 0,
					bpmSum: 0,
					errSum: 0,
					errRuns: 0,
					playMs: 0,
					at: s.at
				};
				days.set(s.day, d);
			}
			d.runs++;
			d.notes += s.total;
			d.hits += s.hits;
			d.bpmSum += s.bpm;
			d.playMs += s.durationMs ?? 0;
			if (s.hits > 0) {
				d.errSum += s.avgAbsMs;
				d.errRuns++;
			}
			d.at = Math.min(d.at, s.at);
		}
		return days;
	}

	/** Compact practice time: "48s", "12m", "3h 20m". */
	function duration(ms: number): string {
		const total = Math.round(ms / 1000);
		if (total < 60) return `${total}s`;
		const mins = Math.round(total / 60);
		if (mins < 60) return `${mins}m`;
		return `${Math.floor(mins / 60)}h ${mins % 60}m`;
	}

	const byDay = $derived(aggregate(sessions));

	// ---- summary tiles (all time) ----------------------------------------

	/** Consecutive days practised, counting back from today. */
	function streaks(days: Map<string, DayAgg>): { current: number; best: number } {
		if (!days.size) return { current: 0, best: 0 };
		const keys = [...days.keys()].sort();
		let best = 1;
		let run = 1;
		for (let i = 1; i < keys.length; i++) {
			const prev = new Date(keys[i - 1] + 'T00:00');
			const cur = new Date(keys[i] + 'T00:00');
			prev.setDate(prev.getDate() + 1);
			run = dayKey(prev) === dayKey(cur) ? run + 1 : 1;
			best = Math.max(best, run);
		}
		// A streak stays alive on the day after its last run — today is not over
		// yet, so yesterday still counts as current.
		const today = new Date();
		const yesterday = new Date();
		yesterday.setDate(yesterday.getDate() - 1);
		const last = keys[keys.length - 1];
		const alive = last === dayKey(today) || last === dayKey(yesterday);
		return { current: alive ? run : 0, best };
	}

	// Scoped to the current range so the tiles, the charts and the tables always
	// describe the same slice. The streak is the exception: it is a property of
	// the whole history, and a "3 day streak" inside a one-day window is nonsense.
	const totals = $derived.by(() => {
		const list = inRange;
		const notes = list.reduce((a, s) => a + s.total, 0);
		const hits = list.reduce((a, s) => a + s.hits, 0);
		const scored = list.filter((s) => s.hits > 0);
		const { current, best } = streaks(byDay);
		return {
			runs: list.length,
			days: new Set(list.map((s) => s.day)).size,
			notes,
			hits,
			accuracy: notes ? hits / notes : 0,
			avgBpm: list.length ? list.reduce((a, s) => a + s.bpm, 0) / list.length : 0,
			bestBpm: list.reduce((a, s) => Math.max(a, s.bpm), 0),
			avgMs: scored.length ? scored.reduce((a, s) => a + s.avgAbsMs, 0) / scored.length : 0,
			playMs: list.reduce((a, s) => a + (s.durationMs ?? 0), 0),
			streak: current,
			bestStreak: best
		};
	});

	// ---- heatmap ----------------------------------------------------------

	const WEEKS = 53;
	const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

	type Cell = { key: string; date: Date; runs: number; agg: DayAgg | undefined; future: boolean };

	/** Monday-start week columns, ending with the week that contains today. */
	const calendar = $derived.by(() => {
		const today = new Date();
		today.setHours(0, 0, 0, 0);
		const end = new Date(today);
		end.setDate(end.getDate() + (6 - ((end.getDay() + 6) % 7))); // → that week's Sunday
		const cursor = new Date(end);
		cursor.setDate(cursor.getDate() - (WEEKS * 7 - 1));

		const weeks: Cell[][] = [];
		for (let w = 0; w < WEEKS; w++) {
			const week: Cell[] = [];
			for (let d = 0; d < 7; d++) {
				const date = new Date(cursor);
				const key = dayKey(date);
				const agg = byDay.get(key);
				week.push({ key, date, runs: agg?.runs ?? 0, agg, future: date > today });
				cursor.setDate(cursor.getDate() + 1);
			}
			weeks.push(week);
		}
		return weeks;
	});

	/** Month name over the first column that starts a new month. */
	const monthLabels = $derived.by(() => {
		const fmt = new Intl.DateTimeFormat(undefined, { month: 'short' });
		const out: { col: number; label: string }[] = [];
		let last = -1;
		calendar.forEach((week, col) => {
			const m = week[0].date.getMonth();
			if (m === last) return;
			last = m;
			// Skip a label with no room before the next one, and the trailing stub.
			if (col > WEEKS - 3) return;
			out.push({ col, label: fmt.format(week[0].date) });
		});
		return out;
	});

	/**
	 * Runs-per-day → ramp step. Four data steps of one hue (validated light-end
	 * contrast ≥ 2:1 against the card surface); step 0 is the *absence* of data,
	 * not a magnitude, so it is a flat swatch with a ring rather than a fifth step.
	 */
	function level(runs: number): number {
		if (runs <= 0) return 0;
		if (runs === 1) return 1;
		if (runs === 2) return 2;
		if (runs === 3) return 3;
		return 4;
	}

	const longDate = new Intl.DateTimeFormat(undefined, {
		weekday: 'short',
		month: 'short',
		day: 'numeric',
		year: 'numeric'
	});

	const TRACK = 14; // px per day, cell + gutter — mirrored in the CSS grid tracks

	let hoverCell: Cell | null = $state(null);
	let hoverPos = $state({ x: 0, y: 0 });

	// One hit layer over the whole grid rather than a handler per cell: an 11px
	// mark is far below a comfortable pointer target, so the nearest day within
	// its 14px track wins and the gutters stay live.
	function onGridMove(event: PointerEvent) {
		const rect = (event.currentTarget as HTMLElement).getBoundingClientRect();
		const col = Math.floor((event.clientX - rect.left) / TRACK);
		const row = Math.floor((event.clientY - rect.top) / TRACK);
		const cell = calendar[col]?.[row];
		if (!cell || cell.future) {
			hoverCell = null;
			return;
		}
		hoverCell = cell;
		hoverPos = { x: col * TRACK + TRACK / 2, y: row * TRACK };
	}

	// ---- single day --------------------------------------------------------
	//
	// Picking a cell (or a point on a trend) drills into that one day: the runs
	// it holds, and which pads carried them. The aggregates above answer "how is
	// it going"; this answers "what did I actually do on the 14th".

	let selectedDay: string | null = $state(null);

	/** Days with at least one run, ascending — what prev/next step through. */
	const practisedDays = $derived([...byDay.keys()].sort());

	const dayRuns = $derived(
		selectedDay ? sessions.filter((s) => s.day === selectedDay).sort((a, b) => a.at - b.at) : []
	);
	const daySummary = $derived(selectedDay ? (byDay.get(selectedDay) ?? null) : null);
	const dayDate = $derived(selectedDay ? new Date(selectedDay + 'T00:00') : null);

	/** Which pads the day went through, folded across its runs. */
	const dayPads = $derived.by(() => {
		const pads = new Map<
			number,
			{ note: number; name: string; total: number; hits: number; msSum: number; msHits: number }
		>();
		for (const s of dayRuns) {
			for (const l of s.lanes ?? []) {
				const p = pads.get(l.note) ?? {
					note: l.note,
					name: l.name,
					total: 0,
					hits: 0,
					msSum: 0,
					msHits: 0
				};
				p.total += l.total;
				p.hits += l.hits;
				// avgMs is already a mean over that lane's hits, so re-weight by hits
				// instead of averaging the averages — a 2-hit lane must not pull as
				// hard as a 20-hit one.
				p.msSum += l.avgMs * l.hits;
				p.msHits += l.hits;
				pads.set(l.note, p);
			}
		}
		return [...pads.values()].sort((a, b) => a.note - b.note);
	});

	// Step to the nearest *practised* day: walking one calendar day at a time
	// would mean clicking through a fortnight of blanks after a holiday.
	const prevDay = $derived(
		selectedDay ? [...practisedDays].reverse().find((d) => d < selectedDay!) : undefined
	);
	const nextDay = $derived(selectedDay ? practisedDays.find((d) => d > selectedDay!) : undefined);

	// ---- heatmap keyboard navigation ---------------------------------------
	//
	// The grid is one tab stop with a roving focus rather than 371, which is what
	// makes the day view reachable without a pointer.

	// Type argument rather than a variable annotation: with an inline object type
	// the latter is dropped, `focusPos` infers as plain `null`, and the truthy
	// check below narrows it to `never`.
	let focusPos = $state<{ col: number; row: number } | null>(null);
	const focusCell = $derived(focusPos ? (calendar[focusPos.col]?.[focusPos.row] ?? null) : null);

	/** Position of today in the grid — where focus lands on first entry. */
	const todayPos = $derived.by(() => {
		const key = dayKey(new Date());
		for (let col = 0; col < calendar.length; col++) {
			const row = calendar[col].findIndex((c) => c.key === key);
			if (row >= 0) return { col, row };
		}
		return { col: WEEKS - 1, row: 0 };
	});

	function onGridKey(event: KeyboardEvent) {
		const pos = focusPos ?? todayPos;
		let { col, row } = pos;
		switch (event.key) {
			case 'ArrowLeft': col--; break;
			case 'ArrowRight': col++; break;
			case 'ArrowUp': row--; break;
			case 'ArrowDown': row++; break;
			case 'Home': col = 0; row = 0; break;
			case 'End': ({ col, row } = todayPos); break;
			case 'Enter':
			case ' ':
				if (focusCell && !focusCell.future) {
					pickDay(focusCell.key);
					event.preventDefault();
				}
				return;
			case 'Escape':
				// Leave day mode, but keep the day selected so the ring stays put.
				if (range === 'day') range = 90;
				return;
			default:
				return;
		}
		// Days run down a column and continue at the top of the next, so stepping
		// off an edge wraps into the neighbouring week rather than sticking.
		if (row < 0) { row = 6; col--; }
		if (row > 6) { row = 0; col++; }
		const target = calendar[col]?.[row];
		if (!target || target.future) return;
		event.preventDefault();
		focusPos = { col, row };
	}

	// ---- trends ------------------------------------------------------------

	// A trailing window in days (0 = everything), or the single selected day.
	type Range = number | 'day';

	const RANGES = [
		{ label: '30d', value: 30 },
		{ label: '90d', value: 90 },
		{ label: '1y', value: 365 },
		{ label: 'All', value: 0 }
	];
	// Today by default: the page opens on the session you just played.
	let range = $state<Range>('day');

	// 'day' with nothing selected would scope everything to nothing, so the mode
	// only counts as on once a day is actually picked.
	const dayMode = $derived(range === 'day' && !!selectedDay);

	/** Picking a day anywhere on the page scopes the page to it. */
	function pickDay(key: string) {
		selectedDay = key;
		range = 'day';
	}

	function stepDay(dir: 1 | -1) {
		const to = dir > 0 ? nextDay : prevDay;
		if (to) selectedDay = to;
	}

	// The one slice every card below reads from. The heatmap is deliberately not
	// scoped by it: it is how you get to a day, so blanking it would strand you.
	const inRange = $derived.by(() => {
		if (range === 'day') return selectedDay ? sessions.filter((s) => s.day === selectedDay) : [];
		if (!range) return sessions;
		const cutoff = Date.now() - range * 86400000;
		return sessions.filter((s) => s.at >= cutoff);
	});

	/** One point per practised day, oldest first. */
	const trendDays = $derived.by(() => {
		const days = [...aggregate(inRange).values()];
		return days.sort((a, b) => a.at - b.at);
	});

	const pointFmt = new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric' });

	function runLabel(d: DayAgg) {
		return `${d.runs} ${d.runs === 1 ? 'run' : 'runs'}`;
	}

	// A single day aggregated per day is one point, which is not a trend. So in
	// day mode the x axis becomes the runs of that day — same charts, finer grain.
	const perLabel = $derived(dayMode ? 'per run' : 'per practice day');

	const bpmPoints: TrendPoint[] = $derived(
		dayMode
			? dayRuns.map((s) => ({
					x: s.at,
					y: s.bpm,
					label: clock.format(s.at),
					detail: s.lessonName
				}))
			: trendDays.map((d) => ({
					x: d.at,
					y: d.bpmSum / d.runs,
					label: pointFmt.format(d.at),
					detail: `${runLabel(d)} · ${d.notes} notes`
				}))
	);

	const msPoints: TrendPoint[] = $derived(
		dayMode
			? dayRuns
					.filter((s) => s.hits > 0)
					.map((s) => ({
						x: s.at,
						y: s.avgAbsMs,
						label: clock.format(s.at),
						detail: `${s.lessonName} · ${s.early} early / ${s.late} late`
					}))
			: trendDays
					.filter((d) => d.errRuns > 0)
					.map((d) => ({
						x: d.at,
						y: d.errSum / d.errRuns,
						label: pointFmt.format(d.at),
						detail: runLabel(d)
					}))
	);

	const timePoints: TrendPoint[] = $derived(
		dayMode
			? dayRuns.map((s) => ({
					x: s.at,
					y: (s.durationMs ?? 0) / 60000,
					label: clock.format(s.at),
					detail: `${s.lessonName} · ${duration(s.durationMs ?? 0)}`
				}))
			: trendDays.map((d) => ({
					x: d.at,
					y: d.playMs / 60000,
					label: pointFmt.format(d.at),
					detail: `${runLabel(d)} · ${duration(d.playMs)}`
				}))
	);

	const accPoints: TrendPoint[] = $derived(
		dayMode
			? dayRuns
					.filter((s) => s.total > 0)
					.map((s) => ({
						x: s.at,
						y: s.accuracy * 100,
						label: clock.format(s.at),
						detail: `${s.hits}/${s.total} notes · ${s.lessonName}`
					}))
			: trendDays
					.filter((d) => d.notes > 0)
					.map((d) => ({
						x: d.at,
						y: (d.hits / d.notes) * 100,
						label: pointFmt.format(d.at),
						detail: `${d.hits}/${d.notes} notes`
					}))
	);

	// In day mode a point is a run, not a day — there is nothing further to drill
	// into, so the charts stop being selectable.
	const onPoint = $derived(dayMode ? undefined : (p: TrendPoint) => pickDay(dayKey(p.x)));

	// ---- controllers & recent runs -----------------------------------------

	const controllers = $derived.by(() => {
		const seen = new Map<string, { key: string; name: string; runs: number; last: number }>();
		for (const s of sessions) {
			// Group on the port id where the run had a named controller: the same
			// hardware reports a different display name on macOS than on Linux, so
			// the id is the stabler identity. Runs with no controller all collapse
			// into one bucket — they have no identity to keep apart, and keying
			// those on the port id would list "No controller" once per lesson.
			const key = s.device ? (s.deviceId ?? s.device) : '';
			const c = seen.get(key) ?? { key, name: s.device ?? 'No controller', runs: 0, last: 0 };
			c.runs++;
			c.last = Math.max(c.last, s.at);
			seen.set(key, c);
		}
		return [...seen.values()].sort((a, b) => b.runs - a.runs);
	});

	const recent = $derived([...inRange].sort((a, b) => b.at - a.at).slice(0, 25));

	const stamp = new Intl.DateTimeFormat(undefined, {
		month: 'short',
		day: 'numeric',
		hour: '2-digit',
		minute: '2-digit'
	});

	// The day panel already names the date in its heading, so its rows carry the
	// time alone.
	const clock = new Intl.DateTimeFormat(undefined, { hour: '2-digit', minute: '2-digit' });

	// Short enough to sit in the filter row without wrapping it.
	const chipDate = new Intl.DateTimeFormat(undefined, {
		weekday: 'short',
		month: 'short',
		day: 'numeric'
	});

	let clearing = $state(false);

	async function onClear() {
		if (!confirm('Delete the whole practice history? This cannot be undone.')) return;
		clearing = true;
		await clearSessions();
		sessions = [];
		clearing = false;
	}

	const pct = (v: number) => Math.round(v * 100) + '%';
</script>

<svelte:head>
	<title>Groove Academy — Practice stats</title>
</svelte:head>

{#if loading}
	<p class="muted">Loading your history…</p>
{:else if !sessions.length}
	<div class="card blank">
		<h2>Nothing recorded yet</h2>
		<p class="muted">
			Every scored run is logged here — tempo, timing and which pads you missed. Play a lesson to
			start the history.
		</p>
		<a class="cta" href="{base}/lessons">Browse lessons</a>
	</div>
{:else}
	<!-- One filter row above everything it scopes: tiles, trends, controllers and
	     the run table all read the same slice. The heatmap below is the exception
	     and says so — it is the navigator, not a scoped view. -->
	<div class="scope" role="group" aria-label="Range">
		<div class="ranges">
			{#if dayMode && dayDate}
				<div class="day-chip">
					<button onclick={() => stepDay(-1)} disabled={!prevDay} aria-label="Earlier day">‹</button>
					<span>{chipDate.format(dayDate)}</span>
					<button onclick={() => stepDay(1)} disabled={!nextDay} aria-label="Later day">›</button>
				</div>
			{:else}
				<button
					onclick={() => pickDay(practisedDays.at(-1) ?? dayKey(new Date()))}
					disabled={!practisedDays.length}>Day</button
				>
			{/if}
			{#each RANGES as r (r.label)}
				<button class:on={range === r.value} onclick={() => (range = r.value)}>{r.label}</button>
			{/each}
		</div>
	</div>

	<section class="tiles" aria-label="Totals for the selected range">
		<div class="tile">
			<span class="tile-value">{totals.runs}</span>
			<span class="tile-label">runs</span>
			<span class="tile-sub">over {totals.days} {totals.days === 1 ? 'day' : 'days'}</span>
		</div>
		<div class="tile">
			<span class="tile-value">{duration(totals.playMs)}</span>
			<span class="tile-label">time played</span>
			<span class="tile-sub">transport time</span>
		</div>
		<div class="tile">
			<span class="tile-value">{totals.streak}</span>
			<span class="tile-label">day streak</span>
			<span class="tile-sub">all time · best {totals.bestStreak}</span>
		</div>
		<div class="tile">
			<span class="tile-value">{Math.round(totals.avgBpm)}</span>
			<span class="tile-label">avg BPM</span>
			<span class="tile-sub">fastest {totals.bestBpm}</span>
		</div>
		<div class="tile">
			<span class="tile-value">{pct(totals.accuracy)}</span>
			<span class="tile-label">notes hit</span>
			<span class="tile-sub">{totals.hits} of {totals.notes}</span>
		</div>
		<div class="tile">
			<span class="tile-value">{Math.round(totals.avgMs)}</span>
			<span class="tile-label">avg error (ms)</span>
			<span class="tile-sub">across scored runs</span>
		</div>
	</section>

	<section class="card" aria-label="Practice history">
		<header class="card-head">
			<h2>Practice history</h2>
			<span class="muted small">last {WEEKS} weeks · pick a day</span>
		</header>

		<div class="heatmap-scroll">
			<div class="heatmap">
				<div class="months" style="--cols: {WEEKS}">
					{#each monthLabels as m (m.col)}
						<span style="grid-column: {m.col + 1}">{m.label}</span>
					{/each}
				</div>

				<div class="weekdays">
					{#each WEEKDAYS as d, i (d)}
						<span class:hidden={i % 2 === 1}>{d}</span>
					{/each}
				</div>

				<!-- A week is a column here, so each column is the logical row of seven
				     days. One tab stop with a roving focus, not 371: arrows move a day,
				     Enter opens it. Pointer hover and clicks go through the single hit
				     layer on the wrapper. -->
				<div
					class="grid"
					role="grid"
					tabindex="0"
					aria-label="Practice calendar, {WEEKS} weeks. Arrow keys move by day, Enter opens it."
					aria-activedescendant={focusCell ? `day-${focusCell.key}` : undefined}
					onpointermove={onGridMove}
					onpointerleave={() => (hoverCell = null)}
					onclick={() => hoverCell && pickDay(hoverCell.key)}
					onkeydown={onGridKey}
					onfocus={() => (focusPos ??= todayPos)}
				>
					{#each calendar as week, w (w)}
						<div class="week" role="row">
							{#each week as cell (cell.key)}
								<div
									id="day-{cell.key}"
									class="cell {cell.future ? 'future' : `l${level(cell.runs)}`}"
									class:focused={focusCell?.key === cell.key}
									class:picked={dayMode && selectedDay === cell.key}
									role="gridcell"
									aria-selected={cell.future ? undefined : dayMode && selectedDay === cell.key}
									aria-label={cell.future
										? undefined
										: `${longDate.format(cell.date)}: ${cell.runs} runs`}
									aria-hidden={cell.future ? 'true' : undefined}
								></div>
							{/each}
						</div>
					{/each}

					{#if hoverCell}
						<div class="tip" style="left: {hoverPos.x}px; top: {hoverPos.y}px">
							<strong>
								{hoverCell.runs
									? `${hoverCell.runs} ${hoverCell.runs === 1 ? 'run' : 'runs'}`
									: 'No practice'}
							</strong>
							<span>{longDate.format(hoverCell.date)}</span>
							{#if hoverCell.agg}
								<span class="detail">
									{duration(hoverCell.agg.playMs)} ·
									{hoverCell.agg.hits}/{hoverCell.agg.notes} notes ·
									{Math.round(hoverCell.agg.bpmSum / hoverCell.agg.runs)} BPM
								</span>
							{/if}
						</div>
					{/if}
				</div>
			</div>
		</div>

		<footer class="legend">
			<span class="muted small">Less</span>
			{#each [0, 1, 2, 3, 4] as l (l)}
				<span class="cell l{l}" aria-hidden="true"></span>
			{/each}
			<span class="muted small">More</span>
		</footer>
	</section>

	<section aria-label="Trends">
		<header class="card-head range-head">
			<h2>Trends</h2>
			<span class="muted small">{perLabel}</span>
		</header>

		<div class="charts">
			<div class="wide">
				<TrendChart
					title="Average tempo"
					unit="BPM"
					color="var(--gold)"
					height={210}
					points={bpmPoints}
					xFormat={dayMode ? (t) => clock.format(t) : undefined}
					onselect={onPoint}
				/>
			</div>
			<TrendChart
				title="Timing error"
				unit="ms"
				color="var(--cyan)"
				hint="lower is better"
				points={msPoints}
				xFormat={dayMode ? (t) => clock.format(t) : undefined}
				onselect={onPoint}
			/>
			<TrendChart
				title="Accuracy"
				unit="%"
				color="var(--green)"
				hint="notes hit"
				points={accPoints}
				xFormat={dayMode ? (t) => clock.format(t) : undefined}
				onselect={onPoint}
			/>
			<TrendChart
				title="Time played"
				unit="min"
				color="var(--violet)"
				points={timePoints}
				xFormat={dayMode ? (t) => clock.format(t) : undefined}
				onselect={onPoint}
			/>
		</div>
	</section>

	<section class="card" aria-label="Controllers">
		<header class="card-head"><h2>Controllers</h2></header>
		<ul class="controllers">
			{#each controllers as c (c.key)}
				<li>
					<span class="ctrl-name">{c.name}</span>
					<span class="muted small">{c.runs} {c.runs === 1 ? 'run' : 'runs'}</span>
				</li>
			{/each}
		</ul>
	</section>

	{#if dayMode && dayDate}
		<section class="card day" aria-label="Selected day">
			<header class="card-head">
				<h2>{longDate.format(dayDate)}</h2>
				<span class="muted small">this day only</span>
			</header>

			{#if daySummary}
				<p class="day-line">
					<strong>{runLabel(daySummary)}</strong>
					· {duration(daySummary.playMs)} played
					· {Math.round(daySummary.bpmSum / daySummary.runs)} BPM average
					· {daySummary.hits}/{daySummary.notes} notes
					{#if daySummary.errRuns}
						· {Math.round(daySummary.errSum / daySummary.errRuns)} ms average error
					{/if}
				</p>

				<div class="table-scroll">
					<table>
						<thead>
							<tr>
								<th>Time</th>
								<th>Lesson</th>
								<th class="num">BPM</th>
								<th class="num">Played</th>
								<th class="num">Hit</th>
								<th class="num">Avg error</th>
								<th>Grade</th>
								<th>Controller</th>
							</tr>
						</thead>
						<tbody>
							{#each dayRuns as s (s.id ?? s.at)}
								<tr>
									<td class="muted">{clock.format(s.at)}</td>
									<td>{s.lessonName}</td>
									<td class="num">{s.bpm}</td>
									<td class="num">{s.durationMs ? duration(s.durationMs) : '—'}</td>
									<td class="num">{s.hits}/{s.total}</td>
									<td class="num">{s.hits ? Math.round(s.avgAbsMs) + ' ms' : '—'}</td>
									<td><span class="grade">{s.grade}</span></td>
									<td class="muted">{s.device ?? '—'}</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>

				{#if dayPads.length}
					<h3>Pads</h3>
					<div class="table-scroll pads">
						<table>
							<thead>
								<tr><th>Pad</th><th class="num">Hit</th><th class="num">Avg error</th></tr>
							</thead>
							<tbody>
								{#each dayPads as p (p.note)}
									<tr>
										<td>{p.name}</td>
										<td class="num">{p.hits}/{p.total}</td>
										<td class="num">{p.msHits ? Math.round(p.msSum / p.msHits) + ' ms' : '—'}</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				{/if}
			{:else}
				<p class="muted">
					No practice on this day.
					{#if prevDay || nextDay}Step to the nearest day you played.{/if}
				</p>
			{/if}
		</section>
	{/if}

	{#if !dayMode}
	<section class="card" aria-label="Recent runs">
		<header class="card-head">
			<h2>Recent runs</h2>
			<span class="muted small">latest {recent.length}</span>
		</header>
		<div class="table-scroll">
			<table>
				<thead>
					<tr>
						<th>When</th>
						<th>Lesson</th>
						<th class="num">BPM</th>
						<th class="num">Played</th>
						<th class="num">Hit</th>
						<th class="num">Avg error</th>
						<th>Grade</th>
						<th>Controller</th>
					</tr>
				</thead>
				<tbody>
					{#each recent as s (s.id ?? s.at)}
						<tr>
							<td class="muted">{stamp.format(s.at)}</td>
							<td>{s.lessonName}</td>
							<td class="num">{s.bpm}</td>
							<td class="num">{s.durationMs ? duration(s.durationMs) : '—'}</td>
							<td class="num">{s.hits}/{s.total}</td>
							<td class="num">{s.hits ? Math.round(s.avgAbsMs) + ' ms' : '—'}</td>
							<td><span class="grade">{s.grade}</span></td>
							<td class="muted">{s.device ?? '—'}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
		<footer class="card-foot">
			<button class="danger" onclick={onClear} disabled={clearing}>Clear history</button>
		</footer>
	</section>
	{/if}
{/if}

<style>
	.muted {
		color: var(--text-muted);
	}

	.small {
		font-family: var(--font-mono);
		font-size: 0.72rem;
	}

	.card {
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--radius);
		padding: 1rem 1.1rem;
		margin-bottom: 1.25rem;
	}

	.card-head {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 1rem;
		margin-bottom: 0.75rem;
	}

	.blank {
		text-align: center;
		padding: 2.5rem 1.5rem;
	}

	.blank p {
		max-width: 34rem;
		margin: 0.5rem auto 1.25rem;
	}

	.cta {
		display: inline-block;
		background: var(--gold);
		color: #1a1505;
		font-weight: 650;
		text-decoration: none;
		padding: 0.55em 1.2em;
		border-radius: var(--radius-sm);
	}

	/* --- tiles ------------------------------------------------------------ */

	.tiles {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(9rem, 1fr));
		gap: 0.75rem;
		margin-bottom: 1.25rem;
	}

	.tile {
		display: flex;
		flex-direction: column;
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--radius);
		padding: 0.8rem 0.9rem;
	}

	.tile-value {
		font-family: var(--font-mono);
		font-size: 1.6rem;
		font-weight: 700;
		line-height: 1.1;
		letter-spacing: -0.02em;
	}

	.tile-label {
		font-size: 0.82rem;
		color: var(--text-muted);
	}

	.tile-sub {
		font-family: var(--font-mono);
		font-size: 0.68rem;
		color: var(--text-faint);
		margin-top: 0.2rem;
	}

	/* --- heatmap ----------------------------------------------------------- */

	.heatmap-scroll {
		overflow-x: auto;
		padding-bottom: 0.25rem;
	}

	.heatmap {
		display: grid;
		grid-template-columns: auto 1fr;
		grid-template-rows: auto auto;
		gap: 0.3rem;
		min-width: max-content;
	}

	.months {
		grid-column: 2;
		display: grid;
		grid-template-columns: repeat(var(--cols), 14px);
		font-family: var(--font-mono);
		font-size: 0.65rem;
		color: var(--text-faint);
		height: 0.9rem;
	}

	.months span {
		grid-row: 1;
		white-space: nowrap;
	}

	.weekdays {
		grid-column: 1;
		grid-row: 2;
		display: grid;
		grid-template-rows: repeat(7, 14px);
		align-items: center;
		font-family: var(--font-mono);
		font-size: 0.62rem;
		color: var(--text-faint);
		padding-right: 0.35rem;
	}

	.weekdays .hidden {
		visibility: hidden;
	}

	.grid {
		grid-column: 2;
		grid-row: 2;
		position: relative;
		display: grid;
		grid-auto-flow: column;
		grid-auto-columns: 14px;
	}

	.week {
		display: grid;
		grid-template-rows: repeat(7, 14px);
	}

	/* 11px mark in a 14px track — the 3px surface gap is what makes the grid
	   readable as separate days rather than one block. */
	.cell {
		width: 11px;
		height: 11px;
		border-radius: 2px;
	}

	.cell.future {
		visibility: hidden;
	}

	/* Step 0 is "no data": a flat swatch with a ring, not a fifth magnitude step. */
	.cell.l0 {
		background: #1c1e2e;
		box-shadow: inset 0 0 0 1px var(--border);
	}

	/* Validated one-hue sequential ramp (dark anchor → --green). */
	.cell.l1 {
		background: #265a47;
	}
	.cell.l2 {
		background: #337a5e;
	}
	.cell.l3 {
		background: #448f6c;
	}
	.cell.l4 {
		background: #55bb88;
	}

	/* Focus ring and selection sit outside the 11px mark so neither eats into it
	   nor shifts the grid. */
	.grid:focus-visible {
		outline: 2px solid var(--gold);
		outline-offset: 4px;
		border-radius: 3px;
	}

	.grid {
		cursor: pointer;
	}

	/* Only while the grid is being driven from the keyboard — after a click the
	   roving position is still tracked, but a second ring next to the picked day
	   is just noise. */
	.grid:focus-visible .cell.focused {
		box-shadow: 0 0 0 1px var(--bg), 0 0 0 2px var(--text-muted);
	}

	.cell.picked {
		box-shadow: 0 0 0 1px var(--bg), 0 0 0 2px var(--gold);
	}

	/* --- single day --------------------------------------------------------- */

	.day {
		border-color: var(--border-strong);
	}

	.day h3 {
		font-size: 0.85rem;
		font-weight: 650;
		color: var(--text-muted);
		margin: 1.1rem 0 0.15rem;
	}

	/* Three narrow columns do not need the full card width — stretched that far
	   the pad name and its numbers stop reading as one row. */
	.pads table {
		max-width: 32rem;
	}

	.day-line {
		margin: 0 0 0.9rem;
		font-size: 0.88rem;
		color: var(--text-muted);
	}

	.day-line strong {
		color: var(--text);
	}

	.legend {
		display: flex;
		align-items: center;
		justify-content: flex-end;
		gap: 0.25rem;
		margin-top: 0.6rem;
	}

	.legend .muted {
		margin: 0 0.35rem;
	}

	.tip {
		position: absolute;
		transform: translate(-50%, -100%) translateY(-0.4rem);
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

	/* --- trends ------------------------------------------------------------ */

	.range-head {
		margin-bottom: 0.75rem;
	}

	.scope {
		display: flex;
		justify-content: flex-end;
		margin-bottom: 1rem;
	}

	.ranges {
		display: flex;
		gap: 0.2rem;
	}

	/* The selected day reads as one control with the range chips, not as a label
	   floating beside them. */
	.day-chip {
		display: flex;
		align-items: stretch;
		margin-right: 0.35rem;
		border: 1px solid var(--gold-dim);
		border-radius: var(--radius-sm);
		background: var(--surface-2);
		overflow: hidden;
	}

	.day-chip span {
		display: flex;
		align-items: center;
		padding: 0 0.5em;
		font-family: var(--font-mono);
		font-size: 0.75rem;
		color: var(--gold);
		white-space: nowrap;
	}

	.day-chip button,
	.day-chip button:hover {
		border: 0;
		border-radius: 0;
		background: none;
		color: var(--text-muted);
		font-size: 0.8rem;
		line-height: 1;
		padding: 0.3em 0.55em;
	}

	.day-chip button:hover:not(:disabled) {
		color: var(--text);
		background: var(--surface-3);
	}

	.day-chip button:disabled {
		opacity: 0.35;
		cursor: default;
	}

	.ranges button {
		font-family: var(--font-mono);
		font-size: 0.75rem;
		color: var(--text-muted);
		background: var(--surface);
		border: 1px solid var(--border);
		padding: 0.3em 0.7em;
		border-radius: var(--radius-sm);
		cursor: pointer;
	}

	.ranges button:hover {
		color: var(--text);
		background: var(--surface-2);
	}

	.ranges button.on {
		color: var(--gold);
		border-color: var(--gold-dim);
		background: var(--surface-2);
	}

	.charts {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(19rem, 1fr));
		gap: 0.9rem;
		margin-bottom: 1.25rem;
	}

	.charts .wide {
		grid-column: 1 / -1;
	}

	/* --- controllers & table ------------------------------------------------ */

	.controllers {
		list-style: none;
		margin: 0;
		padding: 0;
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.controllers li {
		display: flex;
		align-items: baseline;
		gap: 0.5rem;
		background: var(--surface-2);
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		padding: 0.35rem 0.7rem;
	}

	.ctrl-name {
		font-size: 0.85rem;
	}

	.table-scroll {
		overflow-x: auto;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.85rem;
	}

	th,
	td {
		text-align: left;
		padding: 0.45rem 0.6rem 0.45rem 0;
		border-bottom: 1px solid var(--border);
		white-space: nowrap;
	}

	th {
		font-family: var(--font-mono);
		font-size: 0.7rem;
		font-weight: 500;
		color: var(--text-faint);
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}

	.num {
		text-align: right;
		font-family: var(--font-mono);
		padding-right: 1rem;
	}

	tbody tr:last-child td {
		border-bottom: none;
	}

	.grade {
		font-family: var(--font-mono);
		font-weight: 700;
		color: var(--gold);
	}

	.card-foot {
		display: flex;
		justify-content: flex-end;
		margin-top: 0.85rem;
	}

	.danger {
		font-family: var(--font-mono);
		font-size: 0.75rem;
		color: var(--text-muted);
		background: transparent;
		border: 1px solid var(--border);
		padding: 0.4em 0.9em;
		border-radius: var(--radius-sm);
		cursor: pointer;
	}

	.danger:hover:not(:disabled) {
		color: var(--red);
		border-color: var(--red);
	}

	.danger:disabled {
		opacity: 0.5;
		cursor: default;
	}
</style>
