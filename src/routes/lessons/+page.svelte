<script lang="ts">
	import { base } from '$app/paths';
	import { browser } from '$app/environment';
	import { onDestroy, onMount } from 'svelte';
	import { parseMidi, type ParsedMidi, type BackingTrack } from '$lib/midi';
	import { DrumPlayer } from '$lib/drums';
	import { Sampler } from '$lib/sampler';

	type Lesson = {
		id: string;
		name: string;
		file: string;
		bpm: number;
		bars: number;
		description?: string;
	};
	type Status = 'pending' | 'perfect' | 'good' | 'off' | 'miss';

	const PX_PER_BEAT = 280;
	const LANE_H = 56; // resting lane height; grows to fill the viewport while playing
	const BEATS_PER_BAR = 4;
	const COUNT_IN = BEATS_PER_BAR; // one empty bar before the pattern
	const MATCH_WINDOW_BEATS = 0.4; // how far a hit may be from a target to count at all
	// Beginner-friendly timing grades (|error| in ms):
	const PERFECT_MS = 25; // exact  -> green, pops
	const GOOD_MS = 60; // precise -> green
	// between GOOD_MS and the match window -> off (orange); past the window -> miss (red)
	const STORAGE_PREFIX = 'padrill:';

	// The audio/scoring clock runs on a coarse setInterval instead of per-frame rAF,
	// so the main thread never wakes every vsync and the compositor scroll stays
	// uncoupled from main-thread scheduling (see startScroll / schedule).
	const SCHED_INTERVAL_MS = 25; // how often the scheduler runs
	const SCHED_LOOKAHEAD_SEC = 0.1; // schedule backing audio this far ahead of the clock

	let audioCtx: AudioContext | null = $state(null);
	let player: DrumPlayer | null = null;
	let backingPlayer: Sampler | null = null;

	// Backing tracks (bass, etc.) — auto-played, never shown or scored.
	let backing: BackingTrack[] = $state([]);
	let backingCursors: number[] = []; // per-track note pointer, advanced by the scheduler
	let muteBacking = $state(false);
	let backingNames = $state(new Map<string, string>()); // "family:id" -> friendly name
	let basses: { id: string; name: string }[] = $state([]); // selectable bass instruments
	let selectedBass = $state('lately'); // overrides the bass id the MIDI ships with

	// Which sample set a backing track actually plays (bass is user-selectable).
	const effId = (t: BackingTrack) => (t.family === 'bass' ? selectedBass : t.id);

	// MIDI + the device's saved pad->drum mapping (from the Settings page).
	let midiAccess: MIDIAccess | null = $state(null);
	let inputs: { id: string; name: string | null }[] = $state([]);
	let selectedId: string | null = $state(null);
	let currentInput: MIDIInput | null = null;
	let ctrlMap: Map<number, number> = $state(new Map()); // controller note -> GM drum
	let kit = $state(1);

	let lessons: Lesson[] = $state([]);
	let selected: Lesson | null = $state(null);
	let parsed: ParsedMidi | null = $state(null);
	let lanes: number[] = $state([]);
	let drumNames = $state(new Map<number, string>());

	let bpm = $state(60);
	let playing = $state(false);
	let paused = $state(false); // transport frozen mid-lesson; highway stays up
	let status = $state('');
	let beatPos = -COUNT_IN;
	let startBeat = -COUNT_IN; // beat the current scroll segment started from

	// Per-target scoring state (parallel to parsed.notes).
	let matched: boolean[] = $state([]);
	let statuses: Status[] = $state([]);
	let deltas: (number | null)[] = $state([]); // signed ms, - = early
	let extras: { note: number; beat: number }[] = [];
	let report: Report | null = $state(null);

	// Note indices sorted by beat, plus a single advancing cursor, so the miss
	// scan touches only newly-passed notes instead of the whole array each frame.
	let missOrder: number[] = [];
	let missCursor = 0;

	let flashing: Set<number> = $state(new Set());
	let flashTimers = new Map<number, ReturnType<typeof setTimeout>>();

	let startAudioTime = 0; // audioCtx.currentTime at the start of the current scroll segment
	let schedTimer: ReturnType<typeof setInterval> | 0 = 0;
	let dpr = 1; // cached devicePixelRatio; refreshed on resize
	let stripEl: HTMLDivElement | null = $state(null);

	const laneName = (n: number) => drumNames.get(n) ?? String(n);
	const laneRow = (n: number) => lanes.indexOf(n);
	const hasMapping = $derived(ctrlMap.size > 0);

	// A "session" spans from play until the result screen is dismissed. The highway
	// stays fullscreen for the whole span — including while the report is shown — so
	// finishing a lesson never collapses the layout (that reflow scored a 0.52 CLS).
	const inSession = $derived(playing || !!report);

	// Highway fills the whole viewport during a session; rests compact otherwise.
	let winH = $state(0);
	const laneH = $derived(
		inSession && lanes.length ? Math.max(48, Math.floor(winH / lanes.length)) : LANE_H
	);
	const NOTE = 26; // note block size (px)

	// ---- boot / loading -------------------------------------------------

	async function boot() {
		audioCtx = new AudioContext();
		player = new DrumPlayer(audioCtx);
		backingPlayer = new Sampler(audioCtx);
		try {
			const [lRes, dRes] = await Promise.all([
				fetch(`${base}/lessons/manifest.json`),
				fetch(`${base}/drums/manifest.json`)
			]);
			lessons = (await lRes.json()).lessons ?? [];
			const drums = (await dRes.json()).drums ?? [];
			drumNames = new Map(drums.map((d: { note: number; name: string }) => [d.note, d.name]));
		} catch {
			status = 'Could not load manifests — run make-lessons.py & render-drums.py';
			return;
		}
		await loadBackingNames();
		await initMidi();
		if (lessons.length) selectLesson(lessons[0]);
	}

	// Friendly names for backing instruments, e.g. "bass:lately" -> "Lately Bass".
	async function loadBackingNames() {
		try {
			const res = await fetch(`${base}/bass/manifest.json`);
			basses = (await res.json()).basses ?? [];
			backingNames = new Map(basses.map((b) => [`bass:${b.id}`, b.name]));
		} catch {}
	}

	const backingLabel = (t: BackingTrack) =>
		backingNames.get(`${t.family}:${t.id}`) ?? `${t.family} ${t.id}`;

	async function initMidi() {
		if (!navigator.requestMIDIAccess) {
			status = 'Web MIDI not supported — hits cannot be captured';
			return;
		}
		try {
			midiAccess = await navigator.requestMIDIAccess({ sysex: false });
			refreshInputs();
			midiAccess.onstatechange = refreshInputs;
			const saved = localStorage.getItem(STORAGE_PREFIX + 'selectedDevice');
			if (saved && inputs.some((i) => i.id === saved)) selectedId = saved;
			else if (inputs.length) selectedId = inputs[0].id;
		} catch {
			status = 'MIDI access denied — hits cannot be captured';
		}
	}

	function refreshInputs() {
		if (!midiAccess) return;
		inputs = [...midiAccess.inputs.values()].map((i) => ({ id: i.id, name: i.name }));
	}

	function loadDeviceMapping(deviceId: string) {
		ctrlMap = new Map();
		try {
			const raw = localStorage.getItem(STORAGE_PREFIX + deviceId);
			if (!raw) return;
			const cfg = JSON.parse(raw);
			if (Array.isArray(cfg.notes) && Array.isArray(cfg.soundNotes)) {
				const m = new Map<number, number>();
				cfg.notes.forEach((cn: number, i: number) => m.set(cn, cfg.soundNotes[i]));
				ctrlMap = m;
			}
			if (typeof cfg.kit === 'number') kit = cfg.kit;
		} catch {}
	}

	$effect(() => {
		const id = selectedId;
		if (!id || !midiAccess) return;
		if (currentInput) currentInput.onmidimessage = null;
		currentInput = midiAccess.inputs.get(id) ?? null;
		if (currentInput) currentInput.onmidimessage = handleMidi;
		loadDeviceMapping(id);
		localStorage.setItem(STORAGE_PREFIX + 'selectedDevice', id);
	});

	async function selectLesson(lesson: Lesson) {
		stop();
		selected = lesson;
		bpm = lesson.bpm;
		report = null;
		status = 'Loading ' + lesson.name + '…';
		try {
			const res = await fetch(`${base}/lessons/${lesson.file}`);
			parsed = parseMidi(await res.arrayBuffer());
		} catch {
			status = 'Could not load lesson MIDI';
			return;
		}
		lanes = [...new Set(parsed.notes.map((n) => n.note))].sort((a, b) => b - a);
		backing = parsed.backing;
		backingCursors = backing.map(() => 0);
		const bassTrack = backing.find((t) => t.family === 'bass');
		if (bassTrack) selectedBass = bassTrack.id; // default to what the MIDI ships with
		resetScoring();
		beatPos = -COUNT_IN;
		status = '';
		player?.preload(kit, lanes);
		for (const t of backing) backingPlayer?.preload(t.family, effId(t), t.notes.map((n) => n.note));
	}

	// Preload the chosen bass whenever the selection changes.
	$effect(() => {
		const id = selectedBass;
		for (const t of backing) {
			if (t.family === 'bass') backingPlayer?.preload('bass', id, t.notes.map((n) => n.note));
		}
	});

	function bars() {
		if (!parsed) return [];
		const count = parsed.lengthBeats / BEATS_PER_BAR + 1;
		return Array.from({ length: count }, (_, i) => i * BEATS_PER_BAR);
	}

	// ---- scoring --------------------------------------------------------

	function resetScoring() {
		const n = parsed?.notes.length ?? 0;
		matched = Array(n).fill(false);
		statuses = Array(n).fill('pending');
		deltas = Array(n).fill(null);
		extras = [];
		const notes = parsed?.notes ?? [];
		missOrder = notes.map((_, i) => i).sort((a, b) => notes[a].beat - notes[b].beat);
		missCursor = 0;
	}

	function registerHit(gmNote: number, hitBeat: number) {
		if (!parsed) return;
		let best = -1;
		let bestDist = MATCH_WINDOW_BEATS;
		parsed.notes.forEach((t, i) => {
			if (matched[i] || t.note !== gmNote) return;
			const dist = Math.abs(t.beat - hitBeat);
			if (dist < bestDist) {
				bestDist = dist;
				best = i;
			}
		});
		if (best === -1) {
			extras.push({ note: gmNote, beat: hitBeat });
			return;
		}
		const deltaMs = (hitBeat - parsed.notes[best].beat) * (60000 / bpm);
		const abs = Math.abs(deltaMs);
		matched[best] = true;
		deltas[best] = deltaMs;
		statuses[best] = abs <= PERFECT_MS ? 'perfect' : abs <= GOOD_MS ? 'good' : 'off';
	}

	function handleMidi(event: MIDIMessageEvent) {
		if (!event.data || event.data.length < 3) return;
		const [statusByte, note, velocity] = event.data;
		if ((statusByte & 0xf0) !== 0x90 || velocity === 0) return;

		const gm = ctrlMap.get(note);
		if (gm == null) return; // not a mapped pad
		player?.play(kit, gm); // the ONLY sound source — the user's own playing
		flash(gm);
		// Sample the beat straight from the audio clock at the moment of the hit, so
		// timing accuracy doesn't depend on the coarse scheduler cadence.
		if (playing && !paused) {
			const hitBeat = currentBeat();
			if (hitBeat >= -0.001) registerHit(gm, hitBeat);
		}
	}

	function flash(note: number) {
		flashing = new Set([...flashing, note]);
		clearTimeout(flashTimers.get(note));
		flashTimers.set(
			note,
			setTimeout(() => {
				flashing = new Set([...flashing].filter((n) => n !== note));
			}, 90)
		);
	}

	// ---- transport ------------------------------------------------------

	const beatToX = (beat: number) => -beat * PX_PER_BEAT;

	// Positions the strip for a static (paused) frame, snapped to device pixels for
	// crisp notes. While playing the strip is NOT driven from here — a single CSS
	// transform transition animates it on the compositor (see startScroll), immune
	// to main-thread jank. This only runs at rest / on lesson load.
	function updateStrip() {
		if (!stripEl) return;
		const x = Math.round(beatToX(beatPos) * dpr) / dpr;
		stripEl.style.transform = `translate3d(${x}px, 0, 0)`;
	}

	// The transport beat sampled live from the audio clock. Advances continuously
	// between scheduler ticks, so callers (hit scoring) get an exact position.
	function currentBeat() {
		if (!audioCtx) return beatPos;
		return startBeat + (audioCtx.currentTime - startAudioTime) * (bpm / 60);
	}

	// Absolute AudioContext time at which a given beat falls, for lookahead scheduling.
	const beatToAudioTime = (beat: number) => startAudioTime + (beat - startBeat) * (60 / bpm);

	// Hand the whole scroll to the compositor: one linear transform transition from
	// `fromBeat` to the end of the pattern. The scheduler below stays only as the
	// scoring/audio clock and never touches the transform.
	function startScroll(fromBeat: number) {
		if (!stripEl || !parsed) return;
		const durationSec = ((parsed.lengthBeats - fromBeat) * 60) / bpm;
		stripEl.style.transition = 'none';
		stripEl.style.transform = `translate3d(${beatToX(fromBeat)}px, 0, 0)`;
		void stripEl.offsetWidth; // force reflow so the transition starts from here
		stripEl.style.transition = `transform ${durationSec}s linear`;
		stripEl.style.transform = `translate3d(${beatToX(parsed.lengthBeats)}px, 0, 0)`;
	}

	// Freeze the compositor animation at wherever it currently is, then hand
	// positioning back to updateStrip (used when stopping mid-play).
	function freezeScroll() {
		if (!stripEl) return;
		const current = getComputedStyle(stripEl).transform;
		stripEl.style.transition = 'none';
		if (current && current !== 'none') stripEl.style.transform = current;
	}

	// The scoring/audio clock. Runs every SCHED_INTERVAL_MS off the render path — it
	// never requests an animation frame, so the compositor scroll is uncoupled from
	// main-thread scheduling. It only (a) marks passed notes as missed and (b) queues
	// upcoming backing notes at sample-accurate times via the Web Audio clock.
	function schedule() {
		if (!playing || paused || !parsed || !audioCtx) return;
		const ctx = audioCtx; // narrow for use inside the closure below
		beatPos = currentBeat();

		// Any target that has scrolled past the window unhit is a miss. Walk a single
		// beat-sorted cursor so only newly-passed notes touch reactive state. A coarse
		// cadence here is imperceptible — a note reddens a few ms late at most.
		while (
			missCursor < missOrder.length &&
			parsed.notes[missOrder[missCursor]].beat < beatPos - MATCH_WINDOW_BEATS
		) {
			const idx = missOrder[missCursor++];
			if (!matched[idx]) {
				matched[idx] = true;
				statuses[idx] = 'miss';
			}
		}

		// Queue backing (bass) notes up to the lookahead horizon, each scheduled at its
		// exact audio time so bass timing is sample-accurate and frame-rate independent.
		const horizon = beatPos + (SCHED_LOOKAHEAD_SEC * bpm) / 60;
		backing.forEach((track, ti) => {
			let c = backingCursors[ti];
			while (c < track.notes.length && track.notes[c].beat <= horizon) {
				if (!muteBacking) {
					const when = Math.max(beatToAudioTime(track.notes[c].beat), ctx.currentTime);
					backingPlayer?.playAt(track.family, effId(track), track.notes[c].note, when);
				}
				c++;
			}
			backingCursors[ti] = c;
		});

		if (beatPos >= parsed.lengthBeats) finish();
	}

	function startScheduler() {
		stopScheduler();
		schedule(); // fire once immediately so nothing waits a full interval
		schedTimer = setInterval(schedule, SCHED_INTERVAL_MS);
	}

	function stopScheduler() {
		if (schedTimer) {
			clearInterval(schedTimer);
			schedTimer = 0;
		}
	}

	$effect(() => {
		if (parsed) updateStrip(); // position the strip whenever a lesson (re)renders
	});

	async function play() {
		if (!parsed || playing) return;
		await audioCtx?.resume();
		await player?.preload(kit, lanes);
		resetScoring();
		backingCursors = backing.map(() => 0);
		report = null;
		beatPos = -COUNT_IN;
		startBeat = -COUNT_IN;
		playing = true;
		paused = false;
		startAudioTime = audioCtx?.currentTime ?? 0;
		startScroll(startBeat);
		startScheduler();
	}

	// Freeze the transport mid-lesson; resume restarts the compositor scroll
	// from the current beat with the remaining duration.
	function togglePause() {
		if (!playing) return;
		if (!paused) {
			paused = true;
			beatPos = currentBeat(); // freeze the clock where it currently is
			stopScheduler();
			freezeScroll();
			updateStrip();
		} else {
			paused = false;
			startBeat = beatPos;
			startAudioTime = audioCtx?.currentTime ?? 0;
			startScroll(startBeat);
			startScheduler();
		}
	}

	function stop() {
		playing = false;
		paused = false;
		stopScheduler();
		startAudioTime = 0;
		freezeScroll();
		updateStrip();
	}

	function finish() {
		stop();
		if (parsed) {
			parsed.notes.forEach((_, i) => {
				if (!matched[i]) {
					matched[i] = true;
					statuses[i] = 'miss';
				}
			});
		}
		report = buildReport();
		beatPos = parsed ? parsed.lengthBeats : 0;
		updateStrip();
	}

	// Dismiss the result screen, ending the session and collapsing the highway back
	// to its inline size. This runs on a user click, so its layout shift is excluded.
	function exitReport() {
		report = null;
		beatPos = -COUNT_IN;
		updateStrip();
	}

	// ---- report ---------------------------------------------------------

	type LaneReport = { note: number; name: string; total: number; hits: number; avgMs: number };
	type Report = {
		total: number;
		hits: number;
		perfect: number;
		good: number;
		off: number;
		miss: number;
		extra: number;
		accuracy: number;
		avgAbsMs: number;
		early: number;
		late: number;
		grade: string;
		gradeLabel: string;
		lanes: LaneReport[];
	};

	// Encouraging letter grade for beginners, weighted toward tight timing.
	function gradeFor(score: number): { grade: string; gradeLabel: string } {
		if (score >= 0.9) return { grade: 'S', gradeLabel: 'Flawless!' };
		if (score >= 0.75) return { grade: 'A', gradeLabel: 'Great timing' };
		if (score >= 0.6) return { grade: 'B', gradeLabel: 'Solid — nice groove' };
		if (score >= 0.4) return { grade: 'C', gradeLabel: 'Getting there' };
		if (score >= 0.2) return { grade: 'D', gradeLabel: 'Keep practicing' };
		return { grade: 'E', gradeLabel: 'Warm up and try again' };
	}

	function buildReport(): Report {
		const notes = parsed?.notes ?? [];
		const total = notes.length;
		let perfect = 0,
			good = 0,
			off = 0,
			miss = 0,
			absSum = 0,
			hitDeltas = 0,
			early = 0,
			late = 0;
		for (let i = 0; i < total; i++) {
			if (statuses[i] === 'perfect') perfect++;
			else if (statuses[i] === 'good') good++;
			else if (statuses[i] === 'off') off++;
			else if (statuses[i] === 'miss') miss++;
			const d = deltas[i];
			if (d != null) {
				absSum += Math.abs(d);
				hitDeltas++;
				if (d < 0) early++;
				else late++;
			}
		}
		const hits = perfect + good + off;
		const score = total ? (perfect + good * 0.85 + off * 0.5) / total : 0;
		const { grade, gradeLabel } = gradeFor(score);
		const laneReports: LaneReport[] = lanes.map((note) => {
			let t = 0,
				h = 0,
				a = 0,
				c = 0;
			notes.forEach((n, i) => {
				if (n.note !== note) return;
				t++;
				if (deltas[i] != null) {
					h++;
					a += Math.abs(deltas[i] as number);
					c++;
				}
			});
			return { note, name: laneName(note), total: t, hits: h, avgMs: c ? a / c : 0 };
		});
		return {
			total,
			hits,
			perfect,
			good,
			off,
			miss,
			extra: extras.length,
			accuracy: total ? hits / total : 0,
			avgAbsMs: hitDeltas ? absSum / hitDeltas : 0,
			early,
			late,
			grade,
			gradeLabel,
			lanes: laneReports
		};
	}

	onMount(() => {
		const measure = () => {
			winH = window.innerHeight;
			dpr = window.devicePixelRatio || 1;
		};
		measure();
		window.addEventListener('resize', measure);
		return () => window.removeEventListener('resize', measure);
	});

	onDestroy(() => {
		if (!browser) return;
		stop();
		audioCtx?.close();
	});
</script>

<svelte:head>
	<title>Padrill — Lessons</title>
</svelte:head>

<h1>Lessons</h1>

{#if !audioCtx}
	<button class="start-btn" onclick={boot}>Load lessons</button>
{:else}
	<div class="toolbar">
		<select
			value={selected?.id ?? ''}
			onchange={(e) => {
				const l = lessons.find((x) => x.id === e.currentTarget.value);
				if (l) selectLesson(l);
			}}
			aria-label="Select lesson"
		>
			{#each lessons as l (l.id)}
				<option value={l.id}>{l.name}</option>
			{/each}
		</select>

		<select bind:value={selectedId} aria-label="Select MIDI input">
			<option value="">-- device --</option>
			{#each inputs as input (input.id)}
				<option value={input.id}>{input.name || 'Unnamed'}</option>
			{/each}
		</select>

		<label class="bpm">
			BPM
			<input type="number" min="40" max="240" bind:value={bpm} />
		</label>

		{#if playing}
			<button onclick={stop}>Stop</button>
		{:else}
			<button class="play" onclick={play} disabled={!parsed}>Start</button>
		{/if}

		<span class="status">{status}</span>
	</div>

	{#if selected?.description && !inSession}
		<p class="description">{selected.description}</p>
	{/if}

	{#if backing.length && !inSession}
		<div class="backing">
			<span class="backing-tag">backing</span>
			{#each backing as t (t.family + ':' + t.id)}
				{#if t.family === 'bass' && basses.length}
					<select bind:value={selectedBass} aria-label="Select bass">
						{#each basses as b (b.id)}
							<option value={b.id}>{b.name}</option>
						{/each}
					</select>
				{:else}
					<span class="backing-name">{backingLabel(t)}</span>
				{/if}
			{/each}
			<label class="mute">
				<input type="checkbox" bind:checked={muteBacking} /> mute
			</label>
		</div>
	{/if}

	{#if !hasMapping}
		<p class="warn">
			No pad mapping for this device. Set one up on the
			<a href="{base}/settings">Settings</a> page so your hits make sound and get scored.
		</p>
	{/if}

	{#if playing}
		<button class="pause-btn" onclick={togglePause}>{paused ? '▶ Resume' : '❚❚ Pause'}</button>
		<button class="exit" onclick={stop}>■ Stop</button>
	{/if}

	{#if parsed}
		<div class="highway" class:full={inSession} style="height: {lanes.length * laneH}px">
			<div class="labels">
				{#each lanes as note (note)}
					<div class="lane-label" class:flash={flashing.has(note)} style="height: {laneH}px">
						{laneName(note)}
					</div>
				{/each}
			</div>

			<div class="track">
				<div class="hitline"></div>
				{#each lanes as note (note)}
					<div class="lane" style="height: {laneH}px; top: {laneRow(note) * laneH}px"></div>
				{/each}

				<div class="strip" bind:this={stripEl}>
					{#each bars() as barBeat}
						<div class="barline" style="left: {barBeat * PX_PER_BEAT}px"></div>
					{/each}
					{#each parsed.notes as n, i (i)}
						<div
							class="note {statuses[i]}"
							style="left: {n.beat * PX_PER_BEAT}px; top: {laneRow(n.note) * laneH +
								laneH / 2 -
								NOTE / 2}px"
						></div>
					{/each}
				</div>
			</div>
		</div>
		<p class="hint">
			Play the pads as each note crosses the line. Only your hits make sound — timing is scored.
		</p>
	{/if}

	{#if report}
		<div class="report">
			<div class="grade-head">
				<span class="grade grade-{report.grade}">{report.grade}</span>
				<div>
					<h2>{report.gradeLabel}</h2>
					<p class="sub">{Math.round(report.accuracy * 100)}% of notes hit</p>
				</div>
			</div>
			<div class="scoreline">
				<span class="chip perfect">{report.perfect} perfect</span>
				<span class="chip good">{report.good} good</span>
				<span class="chip off">{report.off} off</span>
				<span class="chip miss">{report.miss} missed</span>
				{#if report.extra}<span class="chip extra">{report.extra} extra</span>{/if}
			</div>
			<p class="timing">
				Avg timing error <strong>{Math.round(report.avgAbsMs)} ms</strong>
				({report.early} early / {report.late} late) over {report.hits}/{report.total} notes.
			</p>
			<table>
				<thead>
					<tr><th>Pad</th><th>Hit</th><th>Avg error</th></tr>
				</thead>
				<tbody>
					{#each report.lanes as l (l.note)}
						<tr>
							<td>{l.name}</td>
							<td>{l.hits}/{l.total}</td>
							<td>{l.hits ? Math.round(l.avgMs) + ' ms' : '—'}</td>
						</tr>
					{/each}
				</tbody>
			</table>
			<div class="report-actions">
				<button class="play" onclick={play}>Try again</button>
				<button class="done" onclick={exitReport}>Done</button>
			</div>
		</div>
	{/if}
{/if}

<style>
	.toolbar {
		display: flex;
		gap: 0.75rem;
		align-items: center;
		margin-bottom: 1rem;
		flex-wrap: wrap;
	}

	.toolbar select,
	.toolbar button {
		padding: 0.4em 0.9em;
		font-size: 1rem;
		cursor: pointer;
	}

	.bpm {
		display: flex;
		align-items: center;
		gap: 0.4rem;
		font-size: 0.9rem;
	}

	.bpm input {
		width: 4.5em;
		padding: 0.3em;
		font-size: 1rem;
	}

	.play {
		background: #2a7;
		color: #fff;
		border: 1px solid #185;
		border-radius: 0.3rem;
		font-weight: bold;
	}

	.status {
		font-size: 0.9rem;
		color: #666;
	}

	.description {
		max-width: 640px;
		margin: 0 0 1rem;
		color: #aab;
		font-size: 0.92rem;
		line-height: 1.5;
	}

	.backing {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		margin: 0 0 1rem;
		font-size: 0.85rem;
		color: #bcd;
	}

	.backing-tag {
		padding: 0.15em 0.5em;
		border-radius: 0.25rem;
		background: #2a2a4a;
		color: #9ac;
		font-family: monospace;
		font-size: 0.75rem;
		text-transform: uppercase;
	}

	.backing-name {
		font-weight: bold;
	}

	.backing select {
		padding: 0.2em 0.4em;
		font-size: 0.85rem;
	}

	.mute {
		display: flex;
		align-items: center;
		gap: 0.3rem;
		color: #99a;
		cursor: pointer;
	}

	.warn {
		color: #d80;
		font-size: 0.9rem;
	}

	.highway {
		display: flex;
		border: 1px solid #333;
		border-radius: 0.5rem;
		overflow: hidden;
		background: #12121e;
		max-width: 900px;
	}

	.highway.full {
		position: fixed;
		inset: 0;
		z-index: 50;
		max-width: none;
		height: 100vh !important;
		border: none;
		border-radius: 0;
	}

	.exit {
		position: fixed;
		top: 1rem;
		right: 1rem;
		z-index: 60;
		padding: 0.5em 1em;
		font-size: 1rem;
		font-weight: bold;
		color: #fff;
		background: #a33;
		border: 1px solid #c55;
		border-radius: 0.3rem;
		cursor: pointer;
	}

	.pause-btn {
		position: fixed;
		top: 1rem;
		right: 7.5rem;
		z-index: 60;
		padding: 0.5em 1em;
		font-size: 1rem;
		font-weight: bold;
		color: #fff;
		background: #357;
		border: 1px solid #579;
		border-radius: 0.3rem;
		cursor: pointer;
	}

	.labels {
		flex: 0 0 130px;
		border-right: 1px solid #333;
		background: #16162a;
		z-index: 2;
	}

	.lane-label {
		display: flex;
		align-items: center;
		padding: 0 0.75rem;
		font-family: monospace;
		font-size: 0.85rem;
		color: #bcd;
		border-bottom: 1px solid #23233a;
		transition: background 0.08s ease;
	}

	.lane-label.flash {
		background: #1a3a4e;
		color: #fff;
	}

	.track {
		position: relative;
		flex: 1;
		overflow: hidden;
	}

	.lane {
		position: absolute;
		left: 0;
		right: 0;
		border-bottom: 1px solid #20203a;
	}

	.hitline {
		position: absolute;
		left: 15%;
		top: 0;
		bottom: 0;
		width: 3px;
		background: #f0c040;
		box-shadow: 0 0 10px rgba(240, 192, 64, 0.6);
		z-index: 3;
	}

	.strip {
		position: absolute;
		top: 0;
		bottom: 0;
		left: 15%;
		will-change: transform;
	}

	.barline {
		position: absolute;
		top: 0;
		bottom: 0;
		width: 1px;
		background: #33334d;
	}

	.note {
		position: absolute;
		width: 26px;
		height: 26px;
		margin-left: -13px;
		border-radius: 0.3rem;
		background: #6cf;
		box-shadow: 0 0 4px rgba(100, 200, 255, 0.4);
		transition: background 0.1s ease;
		contain: layout paint;
	}

	.note.good {
		background: #3c8;
		box-shadow: 0 0 4px rgba(60, 220, 140, 0.5);
	}

	.note.perfect {
		background: #4f7;
		box-shadow: 0 0 8px rgba(80, 255, 150, 0.9);
		animation: pop 0.28s ease;
	}

	.note.off {
		background: #f90;
		box-shadow: 0 0 4px rgba(255, 150, 0, 0.4);
	}

	.note.miss {
		background: #e33;
		box-shadow: none;
	}

	@keyframes pop {
		0% {
			transform: scale(1);
		}
		45% {
			transform: scale(1.7);
		}
		100% {
			transform: scale(1);
		}
	}

	.hint {
		color: #778;
		font-size: 0.85rem;
	}

	/* The report floats over the frozen fullscreen highway rather than pushing it
	   out of flow, so a finished lesson never reflows the page (kills the CLS jump). */
	.report {
		position: fixed;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		z-index: 60;
		width: min(500px, calc(100vw - 2rem));
		max-height: 90vh;
		overflow: auto;
		padding: 1rem 1.25rem;
		border: 1px solid #2a2a3a;
		border-radius: 0.5rem;
		background: #16162a;
		box-shadow: 0 12px 48px rgba(0, 0, 0, 0.6);
	}

	.report-actions {
		display: flex;
		gap: 0.6rem;
	}

	.done {
		background: #333;
		color: #ddd;
		border: 1px solid #555;
		border-radius: 0.3rem;
		font-weight: bold;
		padding: 0.4em 0.9em;
		cursor: pointer;
	}

	.report h2 {
		margin: 0;
		font-size: 1.2rem;
	}

	.grade-head {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin-bottom: 0.75rem;
	}

	.grade {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 3rem;
		height: 3rem;
		border-radius: 0.5rem;
		font-size: 1.8rem;
		font-weight: bold;
		font-family: monospace;
		color: #fff;
		background: #444;
	}

	.grade-S {
		background: #2a7;
	}
	.grade-A {
		background: #4a8;
	}
	.grade-B {
		background: #7a6;
	}
	.grade-C {
		background: #b93;
	}
	.grade-D {
		background: #a55;
	}
	.grade-E {
		background: #944;
	}

	.sub {
		margin: 0.15rem 0 0;
		font-size: 0.85rem;
		color: #99a;
	}

	.scoreline {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
		margin-bottom: 0.5rem;
	}

	.chip {
		padding: 0.2em 0.6em;
		border-radius: 1em;
		font-size: 0.8rem;
		font-weight: bold;
	}

	.chip.perfect {
		background: #175;
		color: #cff;
	}
	.chip.good {
		background: #163;
		color: #cfe;
	}
	.chip.off {
		background: #650;
		color: #fe9;
	}
	.chip.miss {
		background: #522;
		color: #fbb;
	}
	.chip.extra {
		background: #334;
		color: #bcd;
	}

	.timing {
		font-size: 0.9rem;
		color: #ccd;
	}

	.report table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.85rem;
		margin: 0.5rem 0 1rem;
	}

	.report th,
	.report td {
		text-align: left;
		padding: 0.3em 0.5em;
		border-bottom: 1px solid #2a2a3a;
	}

	.start-btn {
		padding: 1em 2em;
		font-size: 1.3rem;
		cursor: pointer;
		margin-top: 2rem;
	}
</style>
