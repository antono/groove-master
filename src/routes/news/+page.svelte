<script lang="ts">
	import { base } from '$app/paths';
	import PageMeta from '$lib/page-meta.svelte';

	const MASTODON = 'https://mastodon.social/@groove_academy';
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

<!-- Newest first. One <article> per entry — the list is short enough that markup
     beats a data file, and each post gets to shape its own body. -->
<article class="entry">
	<time datetime="2026-08-07">7 August 2026</time>
	<h2>Groove Academy On Air!</h2>

	<p>
		After a week of development, Groove Academy is live. Lessons scroll, your hits
		are scored, and your practice history is kept. Here's where things stand.
	</p>

	<h3>What is Groove Academy?</h3>
	<p>
		A free finger drumming trainer that runs in the browser — nothing to install.
		Notes come down a scrolling highway in time with a backing track, you play them
		on your MIDI pads or the on-screen grid, and every hit is scored on how close it
		landed. The <a href="{base}/lessons">lessons</a> build up from a single kick to
		full patterns, and <a href="{base}/stats">stats</a> keep track of whether you're
		actually getting better.
	</p>

	<h3>What works today</h3>
	<p>
		MIDI pads are the supported controller. Drum kits technically already work —
		the notes come through and lessons play fine — but the mapping UI in setup was
		drawn for a pad grid, so it looks wrong for a kit. Proper drum support is on
		the list.
	</p>

	<h3>How it works</h3>
	<p>
		Offline first. Everything you do — practice history, kit mapping, the tempo each
		lesson was last played at — is stored in your browser, not on a server. There's
		no account to make and nothing to sync before you can play. Full offline mode,
		where the whole app keeps working with the network off, is still work in
		progress.
	</p>
	<p>
		Optional cloud sync is planned for later, for people who practise on more than
		one machine. Optional is the point: opting out will always leave you with a
		working app.
	</p>

	<h3>The promise</h3>
	<p class="promise">Lessons will always be available without registration.</p>

	<p>
		Follow <a href={MASTODON} target="_blank" rel="noopener">@groove_academy</a> for
		the next update, or just go
		<a href="{base}/lessons">play something</a>.
	</p>
</article>

<style>
	.lede {
		color: var(--text-muted);
		max-width: 40rem;
		margin: -0.5rem 0 2rem;
	}

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

	.entry h2 {
		font-size: 1.35rem;
		margin: 0.35rem 0 1rem;
	}

	.entry h3 {
		font-size: 1rem;
		font-weight: 650;
		margin: 1.5rem 0 0.25rem;
	}

	.entry p {
		color: var(--text-muted);
	}

	.promise {
		color: var(--text);
		border-left: 2px solid var(--gold);
		padding-left: 0.85rem;
	}
</style>
