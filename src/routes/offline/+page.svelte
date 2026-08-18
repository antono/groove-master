<script lang="ts">
	import { base } from '$app/paths';
	import PageMeta from '$lib/page-meta.svelte';

	// The floor under offline navigation. The service worker serves this when a
	// navigation fails and it holds no copy of the page asked for — which is any
	// route that was never visited and is not in the precached set.
	//
	// It exists so that the failure is the app saying so, in the app, with a way
	// out: a browser error page ends the session, and an installed app that shows
	// one does not feel installed.
</script>

<PageMeta title="Offline" description="You are offline." />

<h1>You are offline</h1>

<p class="lede">
	This page has not been saved to your device, so it needs a connection. Everything already
	downloaded still works — including your lessons, if you have practised them before.
</p>

<ul class="ways">
	<li><a href="{base}/lessons">Lessons</a></li>
	<li><a href="{base}/lessons/continue">Continue where you left off</a></li>
	<li><a href="{base}/stats">Practice stats</a></li>
</ul>

<style>
	.lede {
		max-width: 40rem;
		color: var(--text-muted);
	}

	.ways {
		list-style: none;
		margin: 1.5rem 0 0;
		padding: 0;
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.ways a {
		display: inline-block;
		padding: 0.6em 1em;
		border: 1px solid var(--border-strong);
		border-radius: var(--radius-sm);
		background: var(--surface-2);
		color: var(--text);
		text-decoration: none;
	}
</style>
