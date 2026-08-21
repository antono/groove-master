<!--
  v0.2.0. The user-facing half of the changelog, written as prose — see
  CHANGELOG.md for the full split, internal work included.
-->
<script lang="ts">
	import { base } from '$app/paths';

	let { mastodon }: { mastodon: string } = $props();
</script>

<p>
	The last two releases were about what you play on: a kit, a keyboard, a phone screen.
	Which left the thing you play — the lessons themselves — as the thin part. Half the
	catalogue was slots with numbers and no music in them. Forty of those slots are now
	written: <strong>22 playable lessons become 62</strong>, and Foundations goes from two
	filled stages to five.
</p>

<h3>Foundations is a whole tier now</h3>
<p>
	Three new stages, and none of them asks for a faster hand than Stage 2 did.
</p>
<ul>
	<li>
		<strong>Space</strong> — the notes you do not play. Every pattern is a groove you
		already own with a beat, a half bar or a whole bar taken out of it, and coming back in
		exactly on time. It moves no difficulty at all, which is the point: silence is where a
		beginner's time actually falls apart, because inside a run of notes the hands cover
		for the clock.
	</li>
	<li>
		<strong>The Cymbals</strong> — ride, crash and open hat, on rhythms you have already
		played. The first hand travel that has a musical reason rather than a rhythmic one.
	</li>
	<li>
		<strong>Two Bars</strong> — form. Bar 2 answers bar 1, a crash marks the top of a
		four-bar phrase, and the last two beats hand it back to the beginning. Nothing finer
		than an 8th and nothing off the beat, so knowing <em>where you are</em> is the only new
		thing being asked of you.
	</li>
</ul>

<figure>
	<img
		src="{base}/news/2026-08-22-forty-new-lessons/foundations-five-stages.png"
		alt="The Foundations tier page, headed “Can you keep time and stack two hands?”, listing
		five stage cards: 1 Pulse, 2 The Backbeat, 3 Space, 4 The Cymbals, 5 Two Bars. Each has
		a description, an Open link and a 0/10 cleared count."
	/>
	<figcaption>
		Stages 3, 4 and 5 are new. The tier's question has not changed; it now gets a full
		answer.
	</figcaption>
</figure>

<h3>Sixteenths, triplets, and the shuffle</h3>
<p>
	Vocabulary's first stage — <strong>Subdivision &amp; the Grid</strong> — is written out
	too. It is the first time the grid gets finer than an 8th: 16ths, then triplets, then the
	feel between them, ending on the shuffle and the half-time shuffle.
</p>
<p>
	The triplet module builds toward that on purpose. "Broken Triplets" is the full triplet
	with every middle note dropped, so by the time you reach the shuffle you have already
	played it — a shuffle <em>is</em> a triplet with a hole in it, and the lesson before it
	makes that true rather than merely saying so.
</p>

<figure>
	<img
		src="{base}/news/2026-08-22-forty-new-lessons/the-shuffle.png"
		alt="The lesson “1.8 The Shuffle”. Its pattern chart shows a Closed HH lane of hats in
		tight pairs — the second of each pair pushed late — over a Snare lane on 2 and 4 and a
		Kick lane on 1 and 3, with Listen and Play buttons and five practice hints."
	/>
	<figcaption>
		The hats come in pairs and the second of each sits late. Everything under it is the
		rock beat you already play.
	</figcaption>
</figure>

<h3>And it installs</h3>
<p>
	Add Groove Academy to your home screen or dock and it opens in its own window, with no
	address bar and no browser furniture around the highway. Installing also pulls your kit,
	the basses and the lessons onto the device — about a megabyte — so a practice session
	survives the train going into a tunnel. A page you have never opened offline says so
	plainly instead of showing you a browser error.
</p>
<p>
	The layout underneath it is a phone layout now rather than a shrunk desktop one: the nav
	folds into a full-screen menu, tiers, stages, lessons and posts are tappable across their
	whole face, the result screen fills the screen with its buttons where your thumb already
	is, and nothing scrolls sideways on the narrowest phone we could find. Long-pressing the
	installed icon jumps straight to <strong>Continue lesson</strong>,
	<a href="{base}/stats">Stats</a> or News.
</p>

<figure>
	<img
		src="{base}/news/2026-08-22-forty-new-lessons/install-on-a-phone.png"
		alt="The lesson catalogue on a phone. A folded header with a menu button, a yellow
		“Continue — Kick on Every Beat” button, then full-width tier cards for Foundations and
		Vocabulary and greyed cards for Music and Mastery. A strip across the bottom reads
		“Install Groove Academy for offline practice” with Install and Not now buttons."
	/>
	<figcaption>
		The strip along the bottom is the offer, and it is an offer — Not now means not now.
	</figcaption>
</figure>

<h3>Also in this release</h3>
<ul>
	<li>
		<strong>The third lesson of every module was unreachable from the catalogue.</strong>
		"Stretch" is a curriculum word here — the hardest lesson of a module — and it is also
		the name of the rule that makes a card clickable all over. So the badge quietly laid a
		dead sheet over its own card, and every click on it went nowhere. Fixed.
	</li>
	<li>
		<strong>Cymbals have a colour of their own.</strong> A crash used to take the hi-hat's
		colour in one lesson and the snare's in the next, depending on how many lanes that
		lesson happened to have. Crash, ride and the rest now share the hat's hue in every
		lesson, because they are the same family of thing.
	</li>
	<li>
		<strong>The highway really does shrink in portrait.</strong> It was meant to and never
		did — the narrow setting was identical to the wide one. Notes now arrive from about
		three and a half beats away on a phone instead of two and a half. The transport display
		also used to hang off the left edge of a small screen; it drops its words for symbols
		when it has to.
	</li>
	<li>
		<strong>Nothing loads samples while you are playing.</strong> The background download
		that keeps your kit warm could fire in the middle of a run. It now steps aside for Play
		and for Listen, which lose nothing by it — a run fetches what it needs before its first
		beat anyway.
	</li>
</ul>

<p>
	Follow <a href={mastodon} target="_blank" rel="noopener">@groove_academy</a> for the next
	update, or go <a href="{base}/lessons">play something</a> — there is rather more of it
	than there was.
</p>
