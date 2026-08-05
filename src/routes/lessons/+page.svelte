<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { parseMidi } from '$lib/midi';
	import LessonChart from '$lib/lesson-chart.svelte';

	type Lesson = {
		id: string;
		name: string;
		file: string;
		bpm: number;
		bars: number;
		summary?: string;
		description?: string;
	};

	// What the schematic needs, derived from each lesson's MIDI.
	type Preview = {
		lanes: number[];
		notes: { beat: number; note: number }[];
		lengthBeats: number;
	};

	let lessons: Lesson[] = $state([]);
	let previews = $state(new Map<string, Preview>());
	let drumNames = $state(new Map<number, string>());
	let loading = $state(true);
	let error = $state('');

	const laneName = (n: number) => drumNames.get(n) ?? String(n);

	// The catalogue reads the same MIDI the highway plays, so a chart can never
	// drift from the lesson it previews.
	async function loadPreview(lesson: Lesson): Promise<Preview | null> {
		try {
			const res = await fetch(`${base}/lessons/${lesson.file}`);
			const midi = parseMidi(await res.arrayBuffer());
			return {
				lanes: [...new Set(midi.notes.map((n) => n.note))].sort((a, b) => b - a),
				notes: midi.notes,
				lengthBeats: midi.lengthBeats
			};
		} catch {
			return null;
		}
	}

	onMount(async () => {
		try {
			const [lRes, dRes] = await Promise.all([
				fetch(`${base}/lessons/manifest.json`),
				fetch(`${base}/drums/manifest.json`)
			]);
			lessons = (await lRes.json()).lessons ?? [];
			const drums = (await dRes.json()).drums ?? [];
			drumNames = new Map(drums.map((d: { note: number; name: string }) => [d.note, d.name]));
		} catch {
			error = 'Could not load lessons — run make-lessons.py & render-drums.py';
			loading = false;
			return;
		}
		const entries = await Promise.all(
			lessons.map(async (l) => [l.id, await loadPreview(l)] as const)
		);
		previews = new Map(entries.filter((e): e is [string, Preview] => e[1] !== null));
		loading = false;
	});
</script>

<svelte:head>
	<title>Padrill — Lessons</title>
</svelte:head>

<h1>Lessons</h1>
<p class="lede">
	Each lesson is a short looping groove. The chart shows what scrolls toward the hit line — one row
	per pad, one column per beat.
</p>

{#if error}
	<p class="warn">{error}</p>
{:else if loading}
	<p class="muted">Loading lessons…</p>
{:else if !lessons.length}
	<p class="muted">No lessons yet. Run <code>python3 scripts/make-lessons.py</code>.</p>
{:else}
	<ul class="grid">
		{#each lessons as lesson (lesson.id)}
			{@const preview = previews.get(lesson.id)}
			<li class="card">
				<div class="card-head">
					<h2><a href="{base}/lessons/{lesson.id}">{lesson.name}</a></h2>
					<span class="tempo">{lesson.bpm} BPM</span>
				</div>

				<p class="summary">{lesson.summary ?? lesson.description ?? ''}</p>

				{#if preview}
					<div class="chart-frame">
						<LessonChart
							notes={preview.notes}
							lanes={preview.lanes}
							lengthBeats={preview.lengthBeats}
							{laneName}
						/>
					</div>
				{:else}
					<p class="warn">Could not read {lesson.file}</p>
				{/if}

				<a class="cta" href="{base}/lessons/{lesson.id}">Practice →</a>
			</li>
		{/each}
	</ul>
{/if}

<style>
	.lede {
		max-width: 46rem;
		margin: -0.5rem 0 1.5rem;
		color: var(--text-muted);
	}

	.muted {
		color: var(--text-muted);
	}

	.warn {
		color: var(--gold);
		font-size: 0.9rem;
	}

	.grid {
		display: grid;
		gap: 1rem;
		grid-template-columns: repeat(auto-fill, minmax(min(100%, 26rem), 1fr));
		margin: 0;
		padding: 0;
		list-style: none;
	}

	.card {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		padding: 1.1rem 1.25rem 1.25rem;
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--radius);
	}

	.card-head {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 0.75rem;
	}

	.card h2 {
		margin: 0;
	}

	.card h2 a {
		color: var(--text);
		text-decoration: none;
	}

	.card h2 a:hover {
		color: var(--gold);
	}

	.tempo {
		font-family: var(--font-mono);
		font-size: 0.8rem;
		color: var(--gold);
		white-space: nowrap;
	}

	.summary {
		margin: 0;
		font-size: 0.92rem;
		line-height: 1.55;
		color: var(--text-muted);
	}

	.chart-frame {
		padding: 0.5rem 0.6rem;
		background: var(--bg);
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
	}

	.cta {
		align-self: start;
		margin-top: auto;
		padding: 0.5em 1.1em;
		border-radius: var(--radius-sm);
		background: var(--gold);
		border: 1px solid var(--gold);
		color: #1a1505;
		font-weight: 650;
		font-size: 0.92rem;
		text-decoration: none;
	}

	.cta:hover {
		background: #f6cd5e;
	}
</style>
