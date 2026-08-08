<!--
  The launch announcement. Body only — the date and title are chrome, and come
  from the entry in ./index.ts so the listing and the post page cannot disagree
  about them.
-->
<script lang="ts">
	import { base } from '$app/paths';

	let { mastodon }: { mastodon: string } = $props();
</script>

<p>
	After a week of development, Groove Academy is live. Lessons scroll, your hits are
	scored, and your practice history is kept. Here's where things stand.
</p>

<h3>What is Groove Academy?</h3>
<p>
	A free finger drumming trainer that runs in the browser — nothing to install. Notes
	come down a scrolling highway in time with a backing track, you play them on your
	MIDI pads or the on-screen grid, and every hit is scored on how close it landed. The
	<a href="{base}/lessons">lessons</a> build up from a single kick to full patterns, and
	<a href="{base}/stats">stats</a> keep track of whether you're actually getting better.
</p>

<h3>What works today</h3>
<p>
	MIDI pads are the supported controller. Drum kits technically already work — the notes
	come through and lessons play fine — but the mapping UI in setup was drawn for a pad
	grid, so it looks wrong for a kit. Proper drum support is on the list.
</p>

<h3>How it works</h3>
<p>
	Offline first. Everything you do — practice history, kit mapping, the tempo each lesson
	was last played at — is stored in your browser, not on a server. There's no account to
	make and nothing to sync before you can play. Full offline mode, where the whole app
	keeps working with the network off, is still work in progress.
</p>
<p>
	Optional cloud sync is planned for later, for people who practise on more than one
	machine. Optional is the point: opting out will always leave you with a working app.
</p>

<h3>The promise</h3>
<p class="promise">Lessons will always be available without registration.</p>

<p>
	Follow <a href={mastodon} target="_blank" rel="noopener">@groove_academy</a> for the next
	update, or just go <a href="{base}/lessons">play something</a>.
</p>
