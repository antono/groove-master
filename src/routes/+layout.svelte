<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { base } from '$app/paths';
	import { page } from '$app/state';

	let { children } = $props();

	const links = [
		{ href: `${base}/lessons`, route: '/lessons', label: 'Lessons' },
		{ href: `${base}/settings`, route: '/settings', label: 'Settings' },
		{ href: `${base}/onboarding`, route: '/onboarding', label: 'Setup' }
	];

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
			<span class="brand-name">Padrill</span>
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

	<footer class="footer">
		<a
			class="badge"
			href="https://www.wtfpl.net/about/"
			target="_blank"
			rel="license noopener noreferrer"
			title="Do What The Fuck You Want To Public License, Version 2"
		>
			<span class="badge-label">license</span>
			<span class="badge-value">WTFPL</span>
		</a>
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
		margin-top: auto;
		padding: 2rem 0 1.5rem;
		display: flex;
		justify-content: center;
	}

	.badge {
		display: inline-flex;
		font-family: var(--font-mono);
		font-size: 0.7rem;
		line-height: 1;
		border-radius: 0.25rem;
		overflow: hidden;
		text-decoration: none;
		opacity: 0.75;
		transition: opacity 120ms ease;
	}

	.badge:hover {
		opacity: 1;
	}

	.badge-label,
	.badge-value {
		padding: 0.4em 0.6em;
	}

	.badge-label {
		background: #555;
		color: #fff;
	}

	.badge-value {
		background: #4c1;
		color: #fff;
		font-weight: bold;
	}
</style>
