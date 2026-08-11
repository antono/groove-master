<!--
  One rendered news post: the date/title chrome plus the prose styling its body
  relies on.

  The body is a separate component, so scoped styles from the route would never
  reach it — the prose rules below are :global() under .entry for exactly that
  reason, and are the single place a post's typography is defined.
-->
<script lang="ts">
	import { formatDate, MASTODON, type NewsEntry } from '$lib/news';

	let { entry, heading = 'h1' }: { entry: NewsEntry; heading?: 'h1' | 'h2' } = $props();

	const Body = $derived(entry.body);
</script>

<article class="entry">
	<time datetime={entry.date}>{formatDate(entry.date)}</time>
	<!-- On its own page the post title is the page heading; in a listing it sits
	     under one, and must not be a second h1. -->
	{#if heading === 'h1'}
		<h1>{entry.title}</h1>
	{:else}
		<h2>{entry.title}</h2>
	{/if}
	<Body mastodon={MASTODON} />
</article>

<style>
	.entry {
		max-width: 40rem;
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--radius);
		padding: 1.5rem;
		margin-bottom: 1.25rem;
	}

	.entry time {
		font-family: var(--font-mono);
		font-size: 0.85rem;
		color: var(--text-faint);
	}

	.entry h1,
	.entry h2 {
		font-size: 1.35rem;
		margin: 0.35rem 0 1rem;
	}

	.entry :global(h3) {
		font-size: 1rem;
		font-weight: 650;
		margin: 1.5rem 0 0.25rem;
	}

	.entry :global(p),
	.entry :global(li) {
		color: var(--text-muted);
	}

	.entry :global(ul) {
		padding-left: 1.1rem;
	}

	.entry :global(li) {
		margin-bottom: 0.4rem;
	}

	.entry :global(li)::marker {
		color: var(--gold);
	}

	/* Screenshots. A post's figures sit flush to the column's edges — the app is
	   dark and so is the card, so an inset image reads as a panel of the page
	   rather than a picture of one; the border is what separates them. */
	.entry :global(figure) {
		margin: 1rem 0 1.25rem;
	}

	.entry :global(figure img) {
		display: block;
		width: 100%;
		height: auto;
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		background: var(--surface-2);
	}

	/* The caption says what to look at; alt text says what is there. Both are
	   needed and neither substitutes for the other. */
	.entry :global(figcaption) {
		margin-top: 0.5rem;
		font-size: 0.85rem;
		color: var(--text-faint);
	}

	.entry :global(.promise) {
		color: var(--text);
		border-left: 2px solid var(--gold);
		padding-left: 0.85rem;
	}
</style>
