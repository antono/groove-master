<script lang="ts">
	import { base } from '$app/paths';
</script>

<svelte:head>
	<title>Groove Academy — free drum lessons</title>
	<meta
		name="description"
		content="Free, interactive drum lessons in your browser. Built because Melodics can't be paid for from Belarus."
	/>
</svelte:head>

<section class="hero">
	<svg class="mark" viewBox="0 0 512 512" role="img" aria-label="Groove Academy">
		<g fill="none" stroke="currentColor" stroke-width="10" stroke-linejoin="round" stroke-linecap="round">
			<circle cx="256" cy="256" r="150" />
			<g fill="var(--bg)">
				<g transform="translate(256 256) rotate(34)">
					<path d="M -6 170 L 6 170 L 3 -158 L -3 -158 Z" />
					<circle cx="0" cy="-164" r="9" />
				</g>
				<g transform="translate(256 256) rotate(-34)">
					<path d="M -6 170 L 6 170 L 3 -158 L -3 -158 Z" />
					<circle cx="0" cy="-164" r="9" />
				</g>
			</g>
		</g>
		<g fill="currentColor" font-family="var(--font-sans)" font-weight="900" font-size="80" text-anchor="middle">
			<text x="181" y="284">G</text>
			<text x="331" y="284">A</text>
		</g>
		<g fill="currentColor" font-family="var(--font-sans)" font-weight="800" font-size="30" letter-spacing="4" text-anchor="middle">
			<text x="256" y="372">2026</text>
		</g>
	</svg>

	<h1>Groove Academy</h1>
	<p class="tagline">Free drum lessons that scroll by in your browser — bring a MIDI kit or tap the on-screen pads.</p>

	<div class="cta">
		<a class="btn primary" href="{base}/onboarding">Set up your kit</a>
		<a class="btn" href="{base}/lessons">Start playing</a>
	</div>
</section>

<section class="story">
	<h2>Why this exists</h2>
	<p>
		I built Groove Academy because I couldn't pay for
		<a href="https://melodics.com" target="_blank" rel="noopener">Melodics</a>
		from Belarus — the payment options simply don't reach here. Learning to drum
		shouldn't depend on having the right card in the right country.
	</p>
	<p>
		So here's the free version: a growing set of lessons, a note highway that plays
		in time, and your own kit or the on-screen pads. No account, no paywall — just
		sit down and play.
	</p>
	<p class="signoff">Sincerely yours,<br />Anton</p>
</section>

<style>
	.hero {
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
		padding: 2.5rem 0 3rem;
	}

	.mark {
		width: 132px;
		height: 132px;
		color: var(--gold);
		margin-bottom: 0.5rem;
	}

	.hero h1 {
		font-size: clamp(1.9rem, 6vw, 2.6rem);
		margin: 0.25rem 0 0.5rem;
	}

	.tagline {
		max-width: 34rem;
		color: var(--text-muted);
		font-size: 1.05rem;
		margin: 0 0 1.75rem;
	}

	.cta {
		display: flex;
		gap: 0.75rem;
		flex-wrap: wrap;
		justify-content: center;
	}

	.btn {
		display: inline-block;
		text-decoration: none;
		color: var(--text);
		background: var(--surface-2);
		border: 1px solid var(--border-strong);
		border-radius: var(--radius-sm);
		padding: 0.6em 1.4em;
		font-weight: 600;
		transition:
			background 120ms ease,
			border-color 120ms ease,
			transform 120ms ease;
	}

	.btn:hover {
		background: var(--surface-3);
		border-color: var(--text-faint);
	}

	.btn:active {
		transform: translateY(1px);
	}

	.btn.primary {
		background: var(--gold);
		border-color: var(--gold);
		color: #1a1505;
	}

	.btn.primary:hover {
		background: #f6cd5e;
		border-color: #f6cd5e;
	}

	.story {
		max-width: 40rem;
		margin: 0 auto;
		padding-bottom: 3rem;
	}

	.story p {
		color: var(--text-muted);
	}

	.signoff {
		margin-top: 1.5rem;
		font-style: italic;
		color: var(--text);
	}
</style>
