<!--
  v0.0.2. The user-facing half of the changelog, written as prose — see
  CHANGELOG.md for the full split, internal work included.
-->
<script lang="ts">
	import { base } from '$app/paths';

	let { mastodon }: { mastodon: string } = $props();
</script>

<p>
	The first week after launch went on how lessons <em>sound</em> rather than what they
	teach. A pattern used to stop; now it ends. Plus a new lesson, a highway you can resize,
	and colours that mean one thing each.
</p>

<h3>Lessons finish instead of stopping</h3>
<p>
	Every pattern now lands on the bar line that follows it. Whatever you play on beat one
	sounds once more at the very end, and the bass arrives on the root note underneath it —
	after the drums have stopped, so you hear it on its own. Before this a run simply ran
	out of notes and the backing was left hanging mid-phrase.
</p>

<h3>A hi-hat to lean on</h3>
<p>
	Four early lessons had no hi-hat in them at all, which left you counting in silence
	between your own hits. Those now have one ticking underneath — audible, but not yours
	to play and never scored. On a kit the hat is the voice that never stops and everything
	else is heard against it; that is what it is doing here.
</p>

<h3>Pick your highway size</h3>
<p>
	The scrolling highway was always fullscreen. A button in the transport bar now cycles
	<strong>compact</strong>, <strong>medium</strong> and <strong>full</strong>: a thin band
	with only the notes moving, the same band at double height, or lanes stretched to fill
	the screen. It is safe to change mid-run and is remembered across lessons.
</p>

<h3>Colours that mean one thing</h3>
<p>
	Notes are coloured by which drum they are, and then recoloured by how well you hit them.
	Those two vocabularies overlapped: an unplayed kick was the <em>exact</em> shade of green
	as a well-timed one. Drum colours have moved to blues, violets and pinks, and green,
	amber and red now mean nothing but your timing.
</p>

<h3>A new lesson, and a better bassline</h3>
<p>
	<a href="{base}/lessons/paradiddle-groove">4.5 Paradiddle Groove</a> is written: the same
	sticking as 4.4, with a kick on beats one and three underneath, which is the step from
	rudiment to groove. And the very first lesson has a new bass part — the old one played
	the same four beats as your kick, so it was inaudible under your own playing and dull
	besides. It now answers in the gaps between your hits.
</p>

<h3>Fixes</h3>
<ul>
	<li>
		The backing bass was silent on the first play on a new device — its samples had not
		finished loading and the notes were dropped. Lessons now wait for their own backing,
		and fetch it quietly in the background when you open a lesson.
	</li>
	<li>
		The result screen no longer shows a greyed-out <em>Next lesson</em> button next to
		<em>Done</em>. You get whichever one applies.
	</li>
	<li>Shared links now show a proper preview card, and the site has its own icon.</li>
</ul>

<p>
	Follow <a href={mastodon} target="_blank" rel="noopener">@groove_academy</a> for the next
	update, or go <a href="{base}/lessons">play something</a>.
</p>
