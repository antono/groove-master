<script lang="ts">
	import { base } from '$app/paths';

	const pages = [
		{
			href: `${base}/debug/settings`,
			label: 'Settings',
			blurb: 'Pad grid, device mapping, kit choice and transport buttons.'
		},
		{
			href: `${base}/debug/levels`,
			label: 'Levels',
			blurb: 'Sample level workbench — measure peaks and export trims for LEVELS.'
		}
	];
</script>

<svelte:head>
	<title>Groove Master — Debug</title>
</svelte:head>

<h1>Debug</h1>
<p class="lede">
	Workbench pages. They stay out of the top menu unless <code>localStorage.debug</code> is set.
</p>

<ul class="list">
	{#each pages as p (p.href)}
		<li>
			<a href={p.href}>{p.label}</a>
			<span class="blurb">{p.blurb}</span>
		</li>
	{/each}
</ul>

<style>
	.lede {
		max-width: 46rem;
		margin: -0.5rem 0 1.5rem;
		color: var(--text-muted);
	}

	.list {
		display: grid;
		gap: 0.75rem;
		margin: 0;
		padding: 0;
		list-style: none;
		max-width: 46rem;
	}

	.list li {
		display: flex;
		flex-direction: column;
		gap: 0.2rem;
		padding: 0.85rem 1rem;
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		background: var(--surface);
	}

	.list a {
		font-weight: 600;
	}

	.blurb {
		color: var(--text-muted);
		font-size: 0.9rem;
	}
</style>
