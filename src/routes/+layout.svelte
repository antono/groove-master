<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import favicon from '$lib/assets/favicon.svg';
	import { base } from '$app/paths';
	import { page } from '$app/state';

	import { savedKit } from '$lib/config';
	import { warmKit } from '$lib/drums';

	let { children } = $props();

	const MASTODON = 'https://mastodon.social/@groove_academy';

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
		{ href: `${base}/`, route: '/', label: 'About', exact: true },
		{ href: `${base}/lessons`, route: '/lessons', label: 'Lessons' },
		{ href: `${base}/stats`, route: '/stats', label: 'Stats' },
		{ href: `${base}/onboarding`, route: '/onboarding', label: 'Setup' },
		{ href: `${base}/news`, route: '/news', label: 'News' },
		...(showDebug ? [{ href: `${base}/debug`, route: '/debug', label: 'Debug' }] : [])
	]);

	// base is relative during SSR ("./…"), so match on the route id instead.
	// The About link points at "/", which would prefix-match everything, so it
	// only lights up on an exact match.
	const active = (link: { route: string; exact?: boolean }) =>
		link.exact ? page.route.id === link.route : (page.route.id?.startsWith(link.route) ?? false);
</script>

<svelte:head>
	<link rel="icon" href={favicon} type="image/svg+xml" />
	<!-- Raster fallbacks for the two places an SVG icon isn't picked up: older
	     browsers, and the iOS home screen. Both are rendered from the same file. -->
	<link rel="alternate icon" href="{base}/favicon-32.png" sizes="32x32" />
	<link rel="apple-touch-icon" href="{base}/apple-touch-icon.png" />
</svelte:head>

<div class="app">
	<header class="header">
		<a class="brand" href="{base}/">
			<img class="brand-mark" src={favicon} alt="" width="512" height="512" />
			<span class="brand-name">Groove Academy</span>
		</a>
		<nav class="nav">
			{#each links as link (link.href)}
				<a href={link.href} class:active={active(link)}>{link.label}</a>
			{/each}
		</nav>
	</header>

	<main class="main">
		{@render children()}
	</main>

	<footer class="footer">
		<!-- rel="me" is load-bearing, not decoration: Mastodon fetches the URL in the
		     profile's Website field and only shows it as verified if it finds a link
		     back to the account. That URL is the site root, so this lives in the
		     layout rather than on /news alone. -->
		<a href={MASTODON} target="_blank" rel="me noopener">Mastodon</a>
	</footer>
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

	/* The small-size variant of the mark — the same file the tab icon uses, which
	   is the one that stays legible at this size. It draws its own gold tile and
	   rounded corners, so nothing here paints behind it. */
	.brand-mark {
		display: block;
		width: 1.9rem;
		height: 1.9rem;
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

	.footer {
		display: flex;
		justify-content: center;
		padding: 2rem 0 1.25rem;
		margin-top: 2rem;
		border-top: 1px solid var(--border);
	}

	.footer a {
		font-family: var(--font-mono);
		font-size: 0.85rem;
		text-decoration: none;
		color: var(--text-faint);
		transition: color 120ms ease;
	}

	.footer a:hover {
		color: var(--gold);
	}
</style>
