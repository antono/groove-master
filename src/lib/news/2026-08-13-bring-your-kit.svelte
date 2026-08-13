<!--
  v0.0.4. The user-facing half of the changelog, written as prose — see
  CHANGELOG.md for the full split, internal work included.
-->
<script lang="ts">
	import { base } from '$app/paths';

	let { mastodon }: { mastodon: string } = $props();
</script>

<p>
	Groove Academy has always assumed you were playing it on a grid of pads. If what you
	own is an electronic drum kit, the only way in was to pretend it was a rectangle and
	map its drums in an order you had to invent for yourself. That assumption is gone. The
	app now takes a kit as a kit — and while we were in there, the lesson catalogue stopped
	being one long list.
</p>

<h3>Set up a kit as a kit</h3>
<p>
	Plug in an electronic kit and setup shows you your kit: the drums where they actually
	sit on the unit, lit one at a time so you know which one to hit. A profile for the
	<strong>Millenium MD-90</strong> ships with this release.
</p>
<p>
	It is recognised by its maker rather than its name, which is worth explaining: the MD-90
	does not call itself an MD-90. It announces itself as <em>e-drum</em> by
	<em>Medeli</em> — the company that actually builds it, for Thomann and others. So the
	setup offers you the layout and asks whether it is yours, rather than telling you what
	you own. If it is not, pick another or describe your own.
</p>

<figure>
	<img
		src="{base}/news/2026-08-13-bring-your-kit/kit-check.png"
		alt="The setup wizard on a step titled “Check your kit”: a Millenium MD-90 seen from
		above, seven round pads on a tabletop unit with a kick pedal below it, each labelled
		with the note it sends. Underneath, “Snare — plays Snare”. Buttons read Re-map drums,
		Pedals, Buttons and Looks right."
	/>
	<figcaption>
		A kit you have already set up is not asked to prove itself again — it goes straight
		here, where you hit a pad and hear the drum it plays.
	</figcaption>
</figure>

<h3>Your feet, worked out rather than guessed</h3>
<p>
	Kits disagree about how a hi-hat works. Some send one note and let the pedal say whether
	it was open or closed; some send two different notes and need no pedal at all; plenty of
	people own the module and never bought the footswitches. Rather than ask you — most
	drummers have no idea what their module sends, and why should they — setup finds out
	from three quick gestures, and captures the bass pedal alongside.
</p>
<p>
	<strong>Skip anything you have not got.</strong> Each pedal on its own, or the lot. What
	you skipped is then said out loud, so a kick that will never make a sound is something
	you find out now instead of halfway through a lesson.
</p>

<h3>Your instrument, next to the lesson</h3>
<p>
	The pattern chart tells you <em>when</em>. Your own kit, drawn beside it, tells you
	<em>where</em> — the drums this lesson asks for, named in the same colours the chart
	gives them, lighting up as you play them. During a run it sits under the scrolling
	highway whenever there is room for it.
</p>

<figure>
	<img
		src="{base}/news/2026-08-13-bring-your-kit/kit-beside-chart.png"
		alt="The lesson “2.4 Kick &amp; Hi-Hat”. Left of the pattern chart, the drum kit seen
		from above with two drums highlighted and labelled Closed HH and Kick; the chart to
		its right shows those same two lanes in matching cyan and pink."
	/>
	<figcaption>
		Two drums marked on the kit, the same two lanes on the chart, the same two colours.
	</figcaption>
</figure>

<p>
	And if a lesson needs a drum your setup cannot produce — an open hi-hat, say, on a kit
	with no pedal — the page tells you before you start, rather than letting those notes
	pile up as misses you cannot account for.
</p>

<h3>Finding a lesson</h3>
<p>
	<a href="{base}/lessons">Lessons</a> was one long list. It now opens on four tiers, each
	with the question it answers: can you keep time, do you have things to say, can you play
	something someone wants to hear, can you make it your own. Open a tier for its stages,
	a stage for its lessons — or press <em>Continue</em> and go straight back to where you
	left off.
</p>

<figure>
	<img
		src="{base}/news/2026-08-13-bring-your-kit/catalogue-tiers.png"
		alt="The Lessons page: a Continue button naming the next lesson, then four tier cards —
		Foundations, Vocabulary, Music and Mastery — each with a question and a cleared count,
		the last two marked “not yet available”. Below them a spine lists every stage with its
		tier-local number."
	/>
	<figcaption>
		Stages count from one inside their own tier, so you read “Vocabulary · Stage 1”
		instead of a running total that means nothing.
	</figcaption>
</figure>

<h3>Also in this release</h3>
<ul>
	<li>
		<strong>A closed hi-hat that would not score.</strong> On a kit with a hi-hat pedal,
		every hat you hit was being counted as an <em>open</em> hat unless you held the pedal
		down — correct for a drummer, useless here, where nearly every lesson wants closed
		hats. It failed quietly, too: the picture of your kit lit up either way, so the hits
		looked like they had landed. A lesson that uses one hi-hat sound now takes that sound
		however you strike it, and only the two lessons that genuinely use both leave the
		pedal in charge.
	</li>
	<li>
		Your <strong>quote ratings now follow you</strong> between devices along with your
		progress and your runs — and if one of those fails to sync it can no longer take the
		others down with it.
	</li>
	<li>
		A <strong>How it works</strong> section on the landing page, for anyone arriving
		without knowing what this is.
	</li>
</ul>

<p>
	Follow <a href={mastodon} target="_blank" rel="noopener">@groove_academy</a> for the next
	update, or go <a href="{base}/lessons">play something</a>.
</p>
