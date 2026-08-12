<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import PageMeta from '$lib/page-meta.svelte';
	import Breadcrumbs from '$lib/breadcrumbs.svelte';
	import JourneySpine from '$lib/journey-spine.svelte';
	import { allSessions } from '$lib/stats';
	import { progressByLesson, type LessonProgress } from '$lib/progress';
	import { stagesForTier, stageRollup } from '$lib/catalogue';
	import type { PageData } from './$types';

	// One tier's stages. The tier's question sits up top so a student knows what
	// this whole leg of the journey is for; each stage carries its own goal and
	// progress and links on to its lessons.
	let { data }: { data: PageData } = $props();

	let progress = $state(new Map<string, LessonProgress>());

	onMount(() => {
		void allSessions().then((runs) => {
			progress = progressByLesson(runs);
		});
	});

	const tier = $derived(data.tier);
	const manifest = $derived(data.manifest!);
	const stages = $derived(stagesForTier(tier, manifest));
</script>

<PageMeta
	title="Groove Academy — {tier.name}"
	description={tier.question}
/>

<Breadcrumbs crumbs={[{ label: 'Lessons', href: `${base}/lessons` }, { label: tier.name }]} />

<h1>{tier.name}</h1>
<p class="question">{tier.question}</p>

<div class="layout">
	<section class="stages" aria-label="Stages">
		{#if stages.length}
			{#each stages as stage (stage.slug)}
				{@const roll = stageRollup(stage, progress)}
				{@const locked = roll.total === 0}
				<article class="stage" class:locked>
					<div class="head">
						<span class="num">Stage {stage.tierNumber}</span>
						{#if locked}
							<h2>{stage.title}</h2>
						{:else}
							<h2><a href="{base}/lessons/stage/{stage.slug}">{stage.title}</a></h2>
						{/if}
					</div>
					<p class="goal">{stage.goal}</p>
					<div class="foot">
						{#if locked}
							<span class="state">Not yet available</span>
						{:else}
							<a class="enter" href="{base}/lessons/stage/{stage.slug}">Open →</a>
							<span class="count">{roll.cleared}/{roll.total} cleared</span>
						{/if}
					</div>
				</article>
			{/each}
		{:else}
			<p class="muted">No stages here yet.</p>
		{/if}
	</section>

	<aside class="roadmap" aria-label="Roadmap">
		<JourneySpine tiers={manifest.tiers ?? []} {manifest} {progress} here={{ tier: tier.slug }} />
	</aside>
</div>

<style>
	.question {
		max-width: 46rem;
		margin: -0.5rem 0 1.75rem;
		color: var(--text-muted);
		font-size: 1.05rem;
	}

	.muted {
		color: var(--text-muted);
	}

	.layout {
		display: grid;
		grid-template-columns: minmax(0, 1fr);
		gap: 2.5rem;
	}

	@media (min-width: 60rem) {
		.layout {
			grid-template-columns: minmax(0, 1fr) 20rem;
			align-items: start;
		}
	}

	.stages {
		display: grid;
		gap: 1rem;
	}

	.stage {
		padding: 1.2rem 1.4rem;
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--radius);
	}

	.stage.locked {
		border-style: dashed;
		background: none;
		opacity: 0.55;
	}

	.head {
		display: flex;
		align-items: baseline;
		gap: 0.6rem;
	}

	.num {
		font-family: var(--font-mono);
		font-size: 0.7rem;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--gold);
	}

	.stage h2 {
		margin: 0;
		font-size: 1.15rem;
	}

	.stage h2 a {
		color: var(--text);
		text-decoration: none;
	}

	.stage h2 a:hover {
		color: var(--gold);
	}

	.goal {
		margin: 0.4rem 0 1rem;
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
