<script lang="ts">
	// The per-page half of the link preview. The parts that never change — the
	// card image, the card type, the site name — live in +layout.svelte, so a
	// page only has to say what it is about.
	//
	// Both names for each field: og:* is what Facebook, Slack, Mastodon,
	// Discord and iMessage read; name="description" is what search engines read.
	// Twitter falls back to og:* when the twitter:* twins are absent, so they
	// aren't repeated here.
	import { page } from '$app/state';
	import { absolute } from '$lib/site';

	let { title, description }: { title: string; description: string } = $props();

	const url = $derived(absolute(page.url.pathname));
</script>

<svelte:head>
	<title>{title}</title>
	<meta name="description" content={description} />
	<link rel="canonical" href={url} />

	<meta property="og:title" content={title} />
	<meta property="og:description" content={description} />
	<meta property="og:url" content={url} />
</svelte:head>
