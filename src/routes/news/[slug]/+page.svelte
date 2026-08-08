<script lang="ts">
	import { base } from '$app/paths';
	import PageMeta from '$lib/page-meta.svelte';
	import NewsArticle from '$lib/news-article.svelte';
	import { findNews } from '$lib/news';

	let { data } = $props();

	// The load has already 404'd on an unknown slug, so this always resolves;
	// it is looked up here because a component cannot be passed through `data`.
	const entry = $derived(findNews(data.slug)!);
</script>

<PageMeta title="{entry.title} — Groove Academy" description={entry.summary} />

<a class="back" href="{base}/news">← All news</a>

<NewsArticle {entry} heading="h1" />

<style>
	.back {
		display: inline-block;
		margin: 0.75rem 0 1rem;
		font-family: var(--font-mono);
		font-size: 0.8rem;
		color: var(--text-muted);
		text-decoration: none;
	}

	.back:hover {
		color: var(--text);
	}
</style>
