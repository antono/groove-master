<!--
  v0.0.3. The user-facing half of the changelog, written as prose — see
  CHANGELOG.md for the full split, internal work included.
-->
<script lang="ts">
	import { base } from '$app/paths';

	let { mastodon }: { mastodon: string } = $props();
</script>

<p>
	Until now everything you did here lived in one browser on one machine. Clear your history
	and your practice went with it. There is now an optional account, and with it your
	progress and your stats follow you between devices. Plus a drummer's words between
	lessons, and a practice heatmap that fits the window it is drawn in.
</p>

<h3>An account, if you want one</h3>
<p>
	Sign in with your email and no password — you get a link, you click it, you are in.
	After that your earned tempos and every scored run back themselves up in the background
	and come back on any device you sign in on.
</p>

<figure>
	<img
		src="{base}/news/2026-08-11-practice-on-every-device/account-sign-in.png"
		alt="The Account page: a heading, the line “Sign in to back up your progress and stats
		and pick up on any device. Optional — the app works fully without an account.”, an
		email field and an “Email me a link” button."
	/>
	<figcaption>Signing in is one field and no password. Skipping it costs you nothing.</figcaption>
</figure>

<p>
	<strong>Optional is meant literally.</strong> Signed out, the app is exactly what it was:
	everything still works, still offline, still yours. Signing out later keeps what is on
	that device — it only stops the backing up. And when you sign in for the first time,
	whatever you had already practised on that device is adopted into the account rather
	than being ignored or overwritten.
</p>
<p>
	Two devices cannot undo each other. A lesson's tempo ceiling takes the higher of the
	two, unlocked lessons are pooled, and runs are appended rather than replaced — so a
	week on the laptop and a week on the tablet add up to two weeks of history instead of
	whichever synced last.
</p>

<h3>A drummer's words between lessons</h3>
<p>
	Press <em>Next lesson</em> on a result screen and, before the next lesson loads, you get
	one line from someone who has spent their life doing this.
</p>

<figure>
	<img
		src="{base}/news/2026-08-11-practice-on-every-device/quote-of-the-day.png"
		alt="A full-screen quote: “The drums are the backbone of a band.” attributed to
		Questlove, with Like and Dislike buttons underneath and a “Never show quotes”
		checkbox below them."
	/>
	<figcaption>
		The author's name is underlined because it does something: it tells you who they are
		and where the line is from.
	</figcaption>
</figure>

<p>
	Fifty-eight of them so far, and you will not see the same one twice until you have seen
	them all. <em>Like</em> or <em>Dislike</em> carries you on to the lesson, so rating one
	costs no extra click — and if you would rather just get on with practising, <em>Never
	show quotes</em> ends them permanently.
</p>

<h3>A heatmap that fits your window</h3>
<p>
	The practice heatmap on <a href="{base}/stats">Stats</a> always drew a full year of
	weeks, whatever it had room for, so on a laptop it was tight and on a phone it was
	unreadable. It now draws the weeks that actually fit — a year on a wide screen, around
	eighteen on a narrow one — and tells you how many it is showing, so you are never
	guessing what you are looking at. Hovering a day used to lose the corner of its tooltip
	on the first and last columns; that tooltip is no longer trapped inside the strip.
</p>

<h3>Fixes</h3>
<ul>
	<li>
		<strong>Lessons and Stats could come up blank.</strong> The storage that keeps your
		history needed an upgrade for the sync work, and having the site open in a second tab
		blocked it — the page then waited on that upgrade forever. It no longer waits, and
		Lessons no longer needs your history to draw its cards at all.
	</li>
	<li>
		The Quote of the Day shipped a few days ago but never actually appeared — it was
		built and then not connected to the button that was supposed to open it.
	</li>
</ul>

<p>
	Follow <a href={mastodon} target="_blank" rel="noopener">@groove_academy</a> for the next
	update, or go <a href="{base}/lessons">play something</a>.
</p>
