<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import favicon from '$lib/assets/favicon.svg';
	import { base } from '$app/paths';
	import { page } from '$app/state';

	import { savedKit } from '$lib/config';
	import { warmKit } from '$lib/drums';

	let { children } = $props();

	// Pull the current kit's samples into the service-worker cache while the page
	// is idle, so the first pad press is never waiting on a download. After the
	// first visit these are all cache hits, so it costs nothing to repeat.
	onMount(() => {
		const warm = () => warmKit(savedKit());
		if (typeof requestIdleCallback === 'function') {
			const handle = requestIdleCallback(warm, { timeout: 3000 });
			return () => cancelIdleCallback(handle);
		}
		const timer = setTimeout(warm, 1500);
		return () => clearTimeout(timer);
	});

	// Debug pages are only linked for people who opted in with
	// `localStorage.debug = 1` in the console; the routes stay reachable by URL.
	let showDebug = $state(false);
	onMount(() => {
		try {
			showDebug = Boolean(localStorage.getItem('debug'));
		} catch {
			// No storage (private mode) — stay hidden.
		}
	});

	const links = $derived([
		{ href: `${base}/lessons`, route: '/lessons', label: 'Lessons' },
		{ href: `${base}/stats`, route: '/stats', label: 'Stats' },
		{ href: `${base}/onboarding`, route: '/onboarding', label: 'Setup' },
		...(showDebug ? [{ href: `${base}/debug`, route: '/debug', label: 'Debug' }] : [])
	]);

	// base is relative during SSR ("./…"), so match on the route id instead.
	const active = (route: string) => page.route.id?.startsWith(route) ?? false;
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<div class="app">
	<header class="header">
		<a class="brand" href="{base}/lessons">
			<span class="brand-mark" aria-hidden="true">▦</span>
			<span class="brand-name">Groove Master</span>
		</a>
		<nav class="nav">
			{#each links as link (link.href)}
				<a href={link.href} class:active={active(link.route)}>{link.label}</a>
			{/each}
		</nav>
	</header>

	<main class="main">
		{@render children()}
	</main>
</div>

<style>
	.app {
		display: flex;
		min-height: 100vh;
		flex-direction: column;
		max-width: 1080px;
		margin: 0 auto;
		padding: 0 1.25rem;
	}

	.header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		padding: 0.85rem 0;
		margin-bottom: 1rem;
		border-bottom: 1px solid var(--border);
	}

	.brand {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		text-decoration: none;
		color: var(--text);
	}

	.brand-mark {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 1.9rem;
		height: 1.9rem;
		border-radius: 0.5rem;
		background: var(--gold);
		color: #1a1505;
		font-size: 1.05rem;
		line-height: 1;
	}

	.brand-name {
		font-weight: 700;
		letter-spacing: -0.01em;
	}

	.nav {
		display: flex;
		gap: 0.35rem;
		flex-wrap: wrap;
		justify-content: flex-end;
	}

	/* On a narrow phone the brand and three links do not fit on one line, and the
	   header was pushing the whole page into a sideways scroll rather than giving
	   way. Let the header wrap and the links tighten instead. */
	@media (max-width: 26rem) {
		.header {
			flex-wrap: wrap;
			gap: 0.5rem;
		}

		.nav a {
			padding: 0.35em 0.5em;
		}
	}

	.nav a {
		font-family: var(--font-mono);
		font-size: 0.9rem;
		text-decoration: none;
		color: var(--text-muted);
		padding: 0.35em 0.75em;
		border-radius: var(--radius-sm);
		transition:
			color 120ms ease,
			background 120ms ease;
	}

	.nav a:hover {
		color: var(--text);
		background: var(--surface-2);
	}

	.nav a.active {
		color: var(--gold);
		background: var(--surface-2);
	}

	.main {
		flex: 1;
	}
</style>
