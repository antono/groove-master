<script lang="ts">
	import { base } from '$app/paths';
	import {
		stagesForTier,
		stageRollup,
		tierRollup,
		type Manifest,
		type Tier
	} from '$lib/catalogue';
	import type { LessonProgress } from '$lib/progress';

	// The whole journey as a vertical spine: tiers, each opening onto its stages,
	// with the student's position marked and every node filled by how much of it
	// is cleared. Later, unwritten tiers/stages still appear as the road ahead.
	//
	// Fed entirely by props and holding no catalogue logic of its own, so if the
	// spine reads as too heavy it can be swapped for a plain bar list without
	// touching the pages. `here` names the current tier and/or stage by slug.
	let {
		tiers,
		manifest,
		progress,
		here = {}
	}: {
		tiers: Tier[];
		manifest: Manifest;
		progress: Map<string, LessonProgress>;
		here?: { tier?: string; stage?: string };
	} = $props();

	const pct = (r: { cleared: number; total: number }) =>
		r.total ? Math.round((r.cleared / r.total) * 100) : 0;
</script>

<nav class="spine" aria-label="Curriculum roadmap">
	{#each tiers as tier (tier.slug)}
		{@const stages = stagesForTier(tier, manifest)}
		{@const roll = tierRollup(tier, manifest, progress)}
		{@const locked = roll.total === 0}
		<div class="tier" class:current={here.tier === tier.slug} class:locked>
			<div class="node tier-node" style="--fill:{pct(roll)}%">
				{#if locked}
					<span class="dot" aria-hidden="true"></span>
					<span class="label">{tier.name}</span>
					<span class="tag">soon</span>
				{:else}
					<span class="dot" aria-hidden="true"></span>
					<a class="label" href="{base}/lessons/tier/{tier.slug}">{tier.name}</a>
					<span class="count">{roll.cleared}/{roll.total}</span>
				{/if}
			</div>

			{#if stages.length}
				<ol class="stages">
					{#each stages as stage (stage.slug)}
						{@const sr = stageRollup(stage, progress)}
						{@const slocked = sr.total === 0}
						<li
							class="node stage-node"
							class:current={here.stage === stage.slug}
							class:locked={slocked}
							style="--fill:{pct(sr)}%"
						>
							<span class="dot" aria-hidden="true"></span>
							{#if slocked}
								<span class="label"
									><span class="num">Stage {stage.tierNumber}</span>{stage.title}</span
								>
								<span class="tag">soon</span>
							{:else}
								<a class="label" href="{base}/lessons/stage/{stage.slug}"
									><span class="num">Stage {stage.tierNumber}</span>{stage.title}</a
								>
								<span class="count">{sr.cleared}/{sr.total}</span>
							{/if}
						</li>
					{/each}
				</ol>
			{/if}
		</div>
	{/each}
</nav>

<style>
	.spine {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.tier.locked {
		opacity: 0.5;
	}

	.node {
		position: relative;
		display: flex;
		align-items: baseline;
		gap: 0.6rem;
		padding: 0.3rem 0.1rem 0.3rem 1.4rem;
	}

	/* A vertical line down the spine, drawn behind the dots. */
	.node::before {
		content: '';
		position: absolute;
		left: 0.32rem;
		top: 0;
		bottom: 0;
		width: 2px;
		background: var(--border);
	}

	.dot {
		position: absolute;
		left: 0;
		top: 0.35rem;
		width: 0.7rem;
		height: 0.7rem;
		border-radius: 50%;
		border: 2px solid var(--border);
		background: var(--bg);
		/* Fill the dot from the bottom by how much of the scope is cleared. */
		background-image: linear-gradient(to top, var(--gold) var(--fill, 0%), transparent var(--fill, 0%));
	}

	.tier-node {
		font-size: 1rem;
		font-weight: 650;
	}

	.tier-node .dot {
		width: 0.85rem;
		height: 0.85rem;
		top: 0.3rem;
		left: -0.07rem;
	}

	.stages {
		margin: 0 0 0.4rem;
		padding: 0;
		list-style: none;
	}

	.stage-node {
		font-size: 0.9rem;
	}

	.label {
		color: var(--text);
		text-decoration: none;
	}

	a.label:hover {
		color: var(--gold);
	}

	.num {
		font-family: var(--font-mono);
		font-size: 0.7rem;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--text-muted);
		margin-right: 0.5rem;
	}

	/* You are here: the marked node's dot is ringed in gold and its label lifts. */
	.current > .node > .dot,
	.node.current .dot {
		border-color: var(--gold);
		box-shadow: 0 0 0 3px color-mix(in srgb, var(--gold) 25%, transparent);
	}

	.current > .tier-node .label,
	.stage-node.current .label {
		color: var(--gold);
	}

	.count {
		margin-left: auto;
		font-family: var(--font-mono);
		font-size: 0.75rem;
		color: var(--text-muted);
	}

	.tag {
		margin-left: auto;
		font-size: 0.68rem;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--text-muted);
	}
</style>
