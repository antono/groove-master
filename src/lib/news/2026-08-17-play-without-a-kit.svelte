<!--
  v0.1.0. The user-facing half of the changelog, written as prose — see
  CHANGELOG.md for the full split, internal work included.
-->
<script lang="ts">
	import { base } from '$app/paths';

	let { mastodon }: { mastodon: string } = $props();
</script>

<p>
	The last release was about taking your kit as it comes. This one is about not having
	one. Until now Groove Academy needed a MIDI controller plugged into a browser that
	speaks Web MIDI — which ruled out every phone and tablet ever made, and anyone whose
	pads are at a friend's house. Your computer keyboard and a grid of on-screen pads are
	now instruments the app knows how to listen to.
</p>

<h3>Your keyboard is six drums</h3>
<p>
	Setup's first screen asks you to connect a controller. Underneath it now reads
	<em>No controller?</em> — take the keyboard, take the on-screen pads, and you are
	playing a lesson about fifteen seconds later.
</p>

<figure>
	<img
		src="{base}/news/2026-08-17-play-without-a-kit/no-controller.png"
		alt="The first setup step, “Connect your pads”, with buttons for Connect USB / MIDI
		and Pair Bluetooth pad. Below a dividing line, smaller text reads “No controller?”
		with two buttons: Use your keyboard, and Use on-screen pads."
	/>
	<figcaption>
		The way in, under the line: two buttons and no hardware between you and a lesson.
	</figcaption>
</figure>

<p>
	Six pads: kick, snare, closed hat, open hat, crash, ride. That is not a stripped-down
	sample of a real kit so much as the honest contents of the curriculum, which is
	overwhelmingly those six. The groove core — <strong>kick, snare, closed hat</strong> —
	sits on <kbd>F</kbd> <kbd>G</kbd> <kbd>H</kbd>, straight along the home row where your
	fingers are already resting; the colour voices sit on <kbd>R</kbd> <kbd>T</kbd>
	<kbd>Y</kbd> above. They are bound to the <em>physical</em> keys rather than the
	printed letters, so the shape is the same shape on AZERTY or Dvorak.
	<kbd>Space</kbd> starts a run and resumes a paused one, <kbd>Esc</kbd> pauses and stops
	on a second press — so a practice session never needs the mouse.
</p>

<figure>
	<img
		src="{base}/news/2026-08-17-play-without-a-kit/keyboard-pads.png"
		alt="A setup step titled “Your keyboard pads”, reading “The keys are fixed — pick the
		drum each one plays.” Six pads in two rows of three, each with its key in a small box
		and a drop-down beneath: R Crash, T Ride, Y Open HH on the top row; F Kick, G Snare,
		H Closed HH on the bottom."
	/>
	<figcaption>
		The keys are fixed; the drums are not. Every one of those six drop-downs is yours to
		change.
	</figcaption>
</figure>

<h3>And a phone is a way in</h3>
<p>
	No mobile browser implements Web MIDI — not Safari, not Chrome on iOS — so a phone has
	never been able to play a lesson here, whatever you plugged into it. The on-screen pads
	do not care: they lay out two-by-three to fit a phone held in one hand, three-by-two on
	anything wider, and they sit beside the pattern chart in exactly the spot a drum kit's
	schematic occupies, because as far as the lesson page is concerned that is what they
	are.
</p>
<p>
	During a run they move into the empty half of the screen below the scrolling lanes, and
	the pad you are about to need <strong>lights a ring about a beat before its note lands
	</strong>. When you are playing with your thumbs you are looking at your thumbs, not at
	the highway, so the cue had to go where your eyes already were.
</p>

<figure>
	<img
		src="{base}/news/2026-08-17-play-without-a-kit/touch-run.png"
		alt="A lesson mid-run. Three lanes — Closed HH, Snare, Kick — banded across the middle
		of the screen with coloured note blocks scrolling toward a vertical yellow hit line;
		two blocks just past the line have turned green. Across the bottom sit six large
		on-screen pads, and the Kick and Hat pads are outlined with a bright ring."
	/>
	<figcaption>
		Kick and Hat are ringed because their notes are the next to land. The two green blocks
		behind the line are hits that scored.
	</figcaption>
</figure>

<h3>None of this is a lesser mode</h3>
<p>
	A keyboard is picked from the same device list as a drum module, and once picked it
	behaves like one. Every pad's drum is changed from the same dropdown, so if you want
	the ride on <kbd>F</kbd> that is one click. And a run played on it lands in your
	<a href="{base}/stats">practice history</a> named for what it was, alongside your runs
	on a kit — which matters more than it sounds, because "my timing got worse this week"
	reads very differently once you can see that this week was played on a laptop in a
	hotel.
</p>

<figure>
	<img
		src="{base}/news/2026-08-17-play-without-a-kit/keyboard-beside-chart.png"
		alt="The lesson “2.5 Rock Beat, Quarter Hats”. Left of the pattern chart sit six
		keyboard pads; Kick (F), Snare (G) and Hat (H) are lit in pink, blue and cyan while
		Crash, Ride and Open hat are dimmed. The chart to the right shows Closed HH, Snare and
		Kick lanes in those same three colours. Below, an Input drop-down reads “Keyboard”."
	/>
	<figcaption>
		The three keys this lesson wants, lit in the colours its lanes use — exactly where a
		drum kit's own diagram would sit.
	</figcaption>
</figure>

<h3>A calmer highway</h3>
<p>
	Notes now cover 110 pixels a beat where they used to cover 280. At the same tempo — the
	music has not changed at all — they approach from further away and a great deal more of
	the pattern is legible before it arrives, which turns the highway from something you
	react to into something you can read ahead on. Nothing about scoring moved: it has
	always been measured against the audio clock and has never once looked at a pixel.
</p>

<h3>Also in this release</h3>
<ul>
	<li>
		<strong>Kit pads that sound like the drums they are.</strong> A drum module that
		names its pads in General MIDI knows more about them than a profile written from a
		photograph does. So on a kit, a pad whose note we hold a sample for now plays that
		sound instead of the profile's guess, and the MD-90's toms are corrected against
		the real hardware. Pad grids are left alone — on an MPD218 the notes are addresses,
		not drums.
	</li>
	<li>
		<strong>Revealing a quote's testimonial no longer shoves the buttons away.</strong>
		It appeared in the flow and pushed Like and Dislike down the page as it did.
		It floats now, and nothing moves.
	</li>
</ul>

<p>
	Follow <a href={mastodon} target="_blank" rel="noopener">@groove_academy</a> for the
	next update, or go <a href="{base}/lessons">play something</a> — with, as of today,
	whatever you happen to have.
</p>
