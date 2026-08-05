<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { parseMidi } from '$lib/midi';
	import LessonChart from '$lib/lesson-chart.svelte';

	// The catalogue renders the curriculum's own shape: stages hold modules, and a
	// module is always three lessons — plain, core, stretch. A module slot that
	// has not been written yet still appears, greyed out, so the road ahead is
	// visible rather than implied by a gap in the numbering.
	type Lesson = {
		id: string;
		number: string;
		name: string;
		file: string;
		bpm: number;
		bars: number;
		summary?: string;
		description?: string;
	};
	type Slot = { id: string; number: string; name: string; tier: string; planned: boolean };
	type Module = { slug: string; title: string; subtitle: string; lessons: Slot[] };
	type Stage = {
		slug: string;
		number: number;
		title: string;
		goal: string;
		modules: Module[];
		closing: Slot | null;
	};

	// What the schematic needs, derived from each lesson's MIDI.
	type Preview = {
		lanes: number[];
		notes: { beat: number; note: number }[];
		lengthBeats: number;
	};

	let stages: Stage[] = $state([]);
	let lessons = $state(new Map<string, Lesson>());
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
		let list: Lesson[] = [];
		try {
			const [lRes, dRes] = await Promise.all([
				fetch(`${base}/lessons/manifest.json`),
				fetch(`${base}/drums/manifest.json`)
			]);
			const manifest = await lRes.json();
			stages = manifest.stages ?? [];
			list = manifest.lessons ?? [];
			lessons = new Map(list.map((l) => [l.id, l]));
			const drums = (await dRes.json()).drums ?? [];
			drumNames = new Map(drums.map((d: { note: number; name: string }) => [d.note, d.name]));
		} catch {
			error = 'Could not load lessons — run make-lessons.py & render-drums.py';
			loading = false;
			return;
		}
		const entries = await Promise.all(list.map(async (l) => [l.id, await loadPreview(l)] as const));
		previews = new Map(entries.filter((e): e is [string, Preview] => e[1] !== null));
		loading = false;
	});
</script>

{#snippet card(slot: Slot)}
	{@const lesson = lessons.get(slot.id)}
	{@const preview = previews.get(slot.id)}
	<li class="card" class:planned={!lesson}>
		<div class="card-head">
			<span class="number">{slot.number}</span>
			<h3>
				{#if lesson}
					<a href="{base}/lessons/{slot.id}">{slot.name}</a>
				{:else}
					{slot.name}
				{/if}
			</h3>
			<span class="tier {slot.tier}">{slot.tier}</span>
		</div>

		{#if lesson}
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
			<div class="card-foot">
				<a class="cta" href="{base}/lessons/{slot.id}">Practice →</a>
				<span class="tempo">{lesson.bpm} BPM</span>
			</div>
		{:else}
			<p class="summary">Not written yet.</p>
		{/if}
	</li>
{/snippet}

<svelte:head>
	<title>Padrill — Lessons</title>
</svelte:head>

<h1>Lessons</h1>
<p class="lede">
	Each lesson is a short looping groove, and every module is three of them: <strong>plain</strong>
	strips a technique to nothing else, <strong>core</strong> is how it is actually played, and
	<strong>stretch</strong> pushes it as far as it usefully goes. The chart shows what scrolls toward
	the hit line — one row per pad, one column per beat.
</p>

{#if error}
	<p class="warn">{error}</p>
{:else if loading}
	<p class="muted">Loading lessons…</p>
{:else if !stages.length}
	<p class="muted">No lessons yet. Run <code>python3 scripts/make-lessons.py</code>.</p>
{:else}
	{#each stages as stage (stage.slug)}
		<section class="stage">
			<h2><span class="number">Stage {stage.number}</span>{stage.title}</h2>
			<p class="goal">{stage.goal}</p>

			{#each stage.modules as mod (mod.slug)}
				<h3 class="module">{mod.title}<span class="subtitle">{mod.subtitle}</span></h3>
				<ul class="grid">
					{#each mod.lessons as slot (slot.id)}
						{@render card(slot)}
					{/each}
				</ul>
			{/each}

			{#if stage.closing}
				<h3 class="module checkpoint">
					Checkpoint<span class="subtitle">
						a bar of each — switching between patterns is what makes them stick
					</span>
				</h3>
				<ul class="grid">
					{@render card(stage.closing)}
				</ul>
			{/if}
		</section>
	{/each}
{/if}

<style>
	.lede {
		max-width: 46rem;
		margin: -0.5rem 0 2rem;
		color: var(--text-muted);
	}

	.muted {
		color: var(--text-muted);
	}

	.warn {
		color: var(--gold);
		font-size: 0.9rem;
	}

	.stage {
		margin-bottom: 3rem;
	}

	.stage h2 {
		margin: 0 0 0.35rem;
	}

	.stage h2 .number {
		display: block;
		font-family: var(--font-mono);
		font-size: 0.7rem;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--gold);
	}

	.goal {
		max-width: 46rem;
		margin: 0 0 1.5rem;
		color: var(--text-muted);
		font-size: 0.95rem;
	}

	.module {
		display: flex;
		align-items: baseline;
		gap: 0.75rem;
		flex-wrap: wrap;
		margin: 0 0 0.75rem;
		padding-bottom: 0.4rem;
		border-bottom: 1px solid var(--border);
		font-size: 1.02rem;
	}

	.module .subtitle {
		color: var(--text-muted);
		font-size: 0.85rem;
		font-weight: 400;
	}

	.grid {
		display: grid;
		gap: 1rem;
		grid-template-columns: repeat(auto-fill, minmax(min(100%, 24rem), 1fr));
		margin: 0 0 2rem;
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

	/* A slot that is designed but not written. Present so the shape of the module
	   is visible, dimmed so it is never mistaken for something playable. */
	.card.planned {
		border-style: dashed;
		background: none;
		opacity: 0.55;
	}

	.card-head {
		display: flex;
		align-items: baseline;
		gap: 0.6rem;
	}

	.card-head .number {
		font-family: var(--font-mono);
		font-size: 0.8rem;
		color: var(--text-muted);
	}

	.card h3 {
		margin: 0;
		font-size: 1rem;
		flex: 1;
	}

	.card h3 a {
		color: var(--text);
		text-decoration: none;
	}

	.card h3 a:hover {
		color: var(--gold);
	}

	/* Where the lesson sits inside its module — the one thing that says how hard
	   it is relative to its neighbours. */
	.tier {
		padding: 0.15em 0.5em;
		border: 1px solid var(--border);
		border-radius: 999px;
		font-size: 0.68rem;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--text-muted);
		white-space: nowrap;
	}

	.tier.core {
		color: var(--cyan);
		border-color: color-mix(in srgb, var(--cyan) 45%, transparent);
	}

	.tier.stretch,
	.tier.checkpoint {
		color: var(--gold);
		border-color: color-mix(in srgb, var(--gold) 45%, transparent);
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

	.card-foot {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.75rem;
		margin-top: auto;
	}

	.cta {
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

	.tempo {
		font-family: var(--font-mono);
		font-size: 0.8rem;
		color: var(--text-muted);
	}
</style>
