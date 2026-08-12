<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import PageMeta from '$lib/page-meta.svelte';
	import JourneySpine from '$lib/journey-spine.svelte';
	import { allSessions } from '$lib/stats';
	import { progressByLesson, type LessonProgress } from '$lib/progress';
	import { continueTarget, tierRollup, type Tier } from '$lib/catalogue';
	import type { PageData } from './$types';

	// The landing is the top of the drill-down: only the four tiers, each with the
	// one question it answers. Stages, modules and lesson cards live one and two
	// levels in — the point is that a student sees the whole shape of the journey
	// before any of its detail. The manifest metadata arrives from the shared
	// layout load; practice history is read client-side and is pure decoration on
	// the tiles, so the page never blocks on it.
	let { data }: { data: PageData } = $props();

	let progress = $state(new Map<string, LessonProgress>());

	onMount(() => {
		void allSessions().then((runs) => {
			progress = progressByLesson(runs);
		});
	});

	const manifest = $derived(data.manifest);
	const tiers = $derived<Tier[]>(manifest?.tiers ?? []);
	const continueId = $derived(manifest ? continueTarget(manifest, progress) : null);
	const continueName = $derived(
		continueId ? manifest?.lessons.find((l) => l.id === continueId)?.name : null
	);
</script>

<PageMeta
	title="Groove Academy — Lessons"
	description="A finger-drumming path in four tiers: keep time, build a vocabulary, play real music, make it your own. Pick a tier to see its stages."
/>

<h1>Lessons</h1>
<p class="lede">
	The path runs in four tiers, each answering one question you can feel. Open a tier to see its
	stages, and a stage for its lessons.
</p>

{#if data.manifestError || !manifest}
	<p class="muted">No lessons yet. Run <code>python3 scripts/make-lessons.py</code>.</p>
{:else}
	{#if continueId}
		<a class="continue" href="{base}/lessons/{continueId}">
			Continue{#if continueName}<span class="continue-name"> — {continueName}</span>{/if} →
		</a>
	{/if}

	<div class="layout">
		<section class="tiers" aria-label="Tiers">
			{#if tiers.length}
				{#each tiers as tier (tier.slug)}
					{@const roll = tierRollup(tier, manifest, progress)}
					{@const locked = roll.total === 0}
					<article class="tier" class:locked>
						{#if locked}
							<h2>{tier.name}</h2>
							<p class="question">{tier.question}</p>
							<span class="state">Not yet available</span>
						{:else}
							<h2><a href="{base}/lessons/tier/{tier.slug}">{tier.name}</a></h2>
							<p class="question">{tier.question}</p>
							<div class="foot">
								<a class="enter" href="{base}/lessons/tier/{tier.slug}">Enter →</a>
								<span class="count">{roll.cleared}/{roll.total} cleared</span>
							</div>
						{/if}
					</article>
				{/each}
			{:else}
				<!-- A manifest from before tiers existed: fall back to one untitled
				     grouping of every stage, so the catalogue still works. -->
				{#each manifest.stages as stage (stage.slug)}
					<article class="tier">
						<h2><a href="{base}/lessons/stage/{stage.slug}">Stage {stage.number} · {stage.title}</a></h2>
						<p class="question">{stage.goal}</p>
					</article>
				{/each}
			{/if}
		</section>

		{#if tiers.length}
			<aside class="roadmap" aria-label="Roadmap">
				<JourneySpine {tiers} {manifest} {progress} />
			</aside>
		{/if}
	</div>
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

	.continue {
		display: inline-block;
		margin: 0 0 1.75rem;
		padding: 0.55em 1.2em;
		border-radius: var(--radius-sm);
		background: var(--gold);
		border: 1px solid var(--gold);
		color: #1a1505;
		font-weight: 650;
		text-decoration: none;
	}

	.continue:hover {
		background: #f6cd5e;
	}

	.continue-name {
		font-weight: 500;
	}

	.layout {
		display: grid;
		grid-template-columns: minmax(0, 1fr);
		gap: 2.5rem;
	}

	/* Roadmap sits beside the tiers on wide screens, below them when it can't. */
	@media (min-width: 60rem) {
		.layout {
			grid-template-columns: minmax(0, 1fr) 20rem;
			align-items: start;
		}
	}

	.tiers {
		display: grid;
		gap: 1rem;
	}

	.tier {
		padding: 1.25rem 1.4rem;
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--radius);
	}

	.tier.locked {
		border-style: dashed;
		background: none;
		opacity: 0.55;
	}

	.tier h2 {
		margin: 0 0 0.35rem;
		font-size: 1.25rem;
	}

	.tier h2 a {
		color: var(--text);
		text-decoration: none;
	}

	.tier h2 a:hover {
		color: var(--gold);
	}

	.question {
		margin: 0 0 1rem;
		color: var(--text-muted);
	}

	.foot {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.75rem;
	}

	.enter {
		color: var(--gold);
		text-decoration: none;
		font-weight: 600;
	}

	.count {
		font-family: var(--font-mono);
		font-size: 0.8rem;
		color: var(--text-muted);
	}

	.state {
		font-size: 0.72rem;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--text-muted);
	}

	.roadmap {
		padding: 1.25rem 1.1rem;
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--radius);
	}
</style>
