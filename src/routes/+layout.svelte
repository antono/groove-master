<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import { base } from '$app/paths';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<div class="app">
	<nav class="nav">
		<a href="{base}/lessons">Lessons</a>
		<a href="{base}/settings">Settings</a>
	</nav>

	{@render children()}

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
	}

	.nav {
		display: flex;
		gap: 1.25rem;
		padding: 0.75rem 0;
		margin-bottom: 0.5rem;
		border-bottom: 1px solid #2a2a3a;
	}

	.nav a {
		font-family: monospace;
		font-size: 0.95rem;
		text-decoration: none;
		color: #9ab;
	}

	.nav a:hover {
		color: #cde;
	}

	.footer {
		margin-top: auto;
		padding: 1.5rem 0;
		display: flex;
		justify-content: center;
	}

	.badge {
		display: inline-flex;
		font-family:
			ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
		font-size: 0.7rem;
		line-height: 1;
		border-radius: 0.25rem;
		overflow: hidden;
		text-decoration: none;
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
