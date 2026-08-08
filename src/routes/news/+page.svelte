<script lang="ts">
	import { base } from '$app/paths';
	import PageMeta from '$lib/page-meta.svelte';
	import { formatDate, MASTODON, NEWS } from '$lib/news';
</script>

<PageMeta
	title="News — Groove Academy"
	description="What's new in Groove Academy, and what's coming next."
/>

<h1>News</h1>
<p class="lede">
	What changed, what's coming, what's still rough. Also on
	<a href={MASTODON} target="_blank" rel="noopener">Mastodon</a>.
</p>

<!-- Summaries, not bodies: every post has its own page, and this list is what
     tells you which one you want. Newest first — NEWS is stored in that order. -->
<ol class="feed">
	{#each NEWS as entry (entry.slug)}
		<li>
			<a class="entry" href="{base}/news/{entry.slug}">
				<time datetime={entry.date}>{formatDate(entry.date)}</time>
				<h2>{entry.title}</h2>
				<p>{entry.summary}</p>
				<span class="more">Read <span aria-hidden="true">→</span></span>
			</a>
		</li>
	{/each}
</ol>

<style>
	.lede {
		color: var(--text-muted);
		max-width: 40rem;
		margin: -0.5rem 0 2rem;
	}

	.feed {
		list-style: none;
		margin: 0;
		padding: 0;
		max-width: 40rem;
	}

	/* The whole card is the link — a headline that is clickable but a summary
	   that is not gives the same destination two hit targets and one dead zone. */
	.entry {
		display: block;
		padding: 1.5rem;
		margin-bottom: 1.25rem;
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--radius);
		color: inherit;
		text-decoration: none;
		transition:
			border-color 120ms ease,
			background 120ms ease;
	}

	.entry:hover {
		border-color: var(--gold-dim);
		background: var(--surface-2);
	}

	.entry time {
		font-family: var(--font-mono);
		font-size: 0.85rem;
		color: var(--text-faint);
	}

	.entry h2 {
		font-size: 1.35rem;
		margin: 0.35rem 0 0.6rem;
		color: var(--text);
	}

	.entry p {
		margin: 0;
		color: var(--text-muted);
	}

	.more {
		display: inline-block;
		margin-top: 0.85rem;
		font-size: 0.9rem;
		font-weight: 650;
		color: var(--gold);
	}

	.entry:hover .more span {
		margin-left: 0.15rem;
	}
</style>
