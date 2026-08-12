<script lang="ts">
	// The path from Lessons down to the current level, shown at the top of every
	// level below the landing so location is read before content. The last crumb
	// is where you are and carries no link.
	type Crumb = { label: string; href?: string };
	let { crumbs }: { crumbs: Crumb[] } = $props();
</script>

<nav class="breadcrumbs" aria-label="Breadcrumb">
	<ol>
		{#each crumbs as crumb, i (i)}
			<li>
				{#if crumb.href && i < crumbs.length - 1}
					<a href={crumb.href}>{crumb.label}</a>
				{:else}
					<span aria-current="page">{crumb.label}</span>
				{/if}
			</li>
		{/each}
	</ol>
</nav>

<style>
	.breadcrumbs {
		margin: 0 0 1.25rem;
	}

	ol {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 0.4rem;
		margin: 0;
		padding: 0;
		list-style: none;
		font-size: 0.85rem;
	}

	/* The separator lives in ::before so it never lands before the root crumb. */
	li + li::before {
		content: "›";
		margin-right: 0.4rem;
		color: var(--text-muted);
	}

	li {
		display: inline-flex;
		align-items: baseline;
		color: var(--text-muted);
	}

	a {
		color: var(--text-muted);
		text-decoration: none;
	}

	a:hover {
		color: var(--gold);
	}

	span[aria-current="page"] {
		color: var(--text);
	}
</style>
