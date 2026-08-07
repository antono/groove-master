<script lang="ts">
	import { base } from '$app/paths';
	import { browser } from '$app/environment';
	import { page } from '$app/state';
	import { onDestroy, onMount, tick } from 'svelte';
	import { parseMidi, COUNT_IN_BEATS, type ParsedMidi, type BackingTrack, type MidiNote } from '$lib/midi';
	import { DrumPlayer } from '$lib/drums';
	import { Sampler } from '$lib/sampler';
	import { asBinding, parseControl, sameControl, type TransportBinding } from '$lib/transport-control';
	import { dayKey, recordSession } from '$lib/stats';
	import { lessonFinished, lessonStarted } from '$lib/analytics';
	import { BPM_STEP, isCleanRun } from '$lib/progress';
	import PageMeta from '$lib/page-meta.svelte';
	import LessonChart from '$lib/lesson-chart.svelte';
	import ControllerMap from '$lib/controller-map.svelte';
	import { laneColor } from '$lib/drum-colors';

	// `id` is the lesson's slug and never changes; `number` ("2.4") is rendered
	// from its position in the curriculum, so inserting a lesson renumbers the
	// catalogue without orphaning practice history or a remembered tempo.
	type Lesson = {
		id: string;
		number: string;
		name: string;
		file: string;
		bpm: number;
		bars: number;
		description?: string;
		hints?: string[];
	};
	type Status = 'pending' | 'perfect' | 'good' | 'off' | 'miss';

	const PX_PER_BEAT = 280;
	const LANE_H = 56; // resting lane height; grows to fill the viewport while playing
	const BEATS_PER_BAR = 4;
	// One bar of lead-in before the pattern. It is no longer empty: the lesson MIDI
	// carries a "count-in" track whose clicks live in exactly this bar, so the
	// constant is shared with the parser that shifts them onto the beat axis.
	const COUNT_IN = COUNT_IN_BEATS;
	const MATCH_WINDOW_BEATS = 0.4; // how far a hit may be from a target to count at all
	// Beginner-friendly timing grades (|error| in ms):
	const PERFECT_MS = 25; // exact  -> green, pops
	const GOOD_MS = 60; // precise -> green
	// between GOOD_MS and the match window -> off (orange); past the window -> miss (red)
	const STORAGE_PREFIX = 'groove-master:';

	// The audio/scoring clock runs on a coarse setInterval instead of per-frame rAF,
	// so the main thread never wakes every vsync and the compositor scroll stays
	// uncoupled from main-thread scheduling (see startScroll / schedule).
	const SCHED_INTERVAL_MS = 25; // how often the scheduler runs
	const SCHED_LOOKAHEAD_SEC = 0.1; // schedule backing audio this far ahead of the clock

	let audioCtx: AudioContext | null = $state(null);
	let player: DrumPlayer | null = null;
	let backingPlayer: Sampler | null = null;

	// Backing tracks (bass, etc.) — auto-played, never shown or scored. Which
	// instrument plays is whatever the lesson MIDI names in its track ("bass:lately").
	let backing: BackingTrack[] = $state([]);
	let backingCursors: number[] = []; // per-track note pointer, advanced by the scheduler

	// Count-in clicks, all at negative beats (beat 0 is the student's). Played on
	// their own kit through the drum player, never shown and never scored.
	let countIn: MidiNote[] = $state([]);
	let countInCursor = 0;

	// The hi-hat a hatless lesson borrows to keep time against. Rides the same
	// clock and the same lookahead as everything else, plays on the lesson's own
	// kit, and — like the count-in — is never shown and never scored. Its MIDI
	// velocity is what keeps it under the student's playing.
	let guide: MidiNote[] = $state([]);
	let guideCursor = 0;

	// MIDI + the device's saved pad->drum mapping (from the Settings page).
	let midiAccess: MIDIAccess | null = $state(null);
	let inputs: { id: string; name: string | null }[] = $state([]);
	let selectedId: string | null = $state(null);
	let currentInput: MIDIInput | null = null;
	let ctrlMap: Map<number, number> = $state(new Map()); // controller note -> GM drum
	// Name stored with the device mapping, kept so a finished run can be filed
	// against a controller even when the port has since gone away.
	let savedDeviceName: string | null = $state(null);
	let kit = $state(1);
	// Play / Stop buttons on the controller, captured by the setup wizard.
	let transport: TransportBinding = $state({ start: null, stop: null });

	// The physical shape of the pad grid, plus the drum each pad triggers in that
	// same order. Only the preview uses it — playing goes through ctrlMap — but it
	// is what lets the resting page show the pattern *on the student's own device*.
	let padCols = $state(0);
	let padRows = $state(0);
	let padDrums: (number | null)[] = $state([]);

	let lessons: Lesson[] = $state([]);
	let selected: Lesson | null = $state(null);
	// Ids the student has earned. The first lesson is always open; each next one
	// opens when its predecessor is cleared one rung above its base (see maybeUnlock).
	let unlockedLessons = $state(new Set<string>());
	let parsed: ParsedMidi | null = $state(null);
	let lanes: number[] = $state([]);
	let drumNames = $state(new Map<number, string>());

	// Tempo is a ladder, not a free dial: each lesson ships a base BPM (its own
	// `bpm`, 60 for the early lessons) and every rung above is +10. The base is
	// unlocked from the start; each higher rung unlocks only once the student clears
	// the rung below it without skipping a note — so speed is earned, never just set.
	const LOCKED_AHEAD = 3; // locked rungs shown past the frontier before the ellipsis
	const NEXT_LESSON_BPM = 80; // finishing at or above this opens the next lesson

	let baseBpm = $state(60); // the lesson's own tempo, the ladder's bottom rung
	// Highest rung unlocked so far, restored per lesson. Never below the base.
	let unlockedBpm = $state(60);
	// The rung currently chosen to play. Always a rung between base and unlockedBpm.
	let selectedBpm = $state(60);

	// The tempo everything (scroll, scheduler, scoring) runs at.
	const bpm = $derived(selectedBpm);

	// Rungs to show: every unlocked one, plus the next locked rung as the target to
	// aim for. Clearing the top rung reveals a new locked one, so the ladder climbs
	// as far as the student can push it.
	const tiers = $derived.by(() => {
		const rungs: number[] = [];
		const top = unlockedBpm + LOCKED_AHEAD * BPM_STEP;
		for (let v = baseBpm; v <= top; v += BPM_STEP) rungs.push(v);
		return rungs;
	});

	// Every rung the student may actually pick, which is what the jump menu offers.
	const unlockedRungs = $derived(tiers.filter((v) => v <= unlockedBpm));

	// The ladder gains a rung per unlock, so a student who has climbed a while ends
	// up with more rungs than the row can hold. The slow end folds away rather than
	// scrolling — the whole point of the control is to show where the climb has got
	// to, and a scrollbar hides exactly that. In its place sits a dropdown holding
	// every unlocked tempo, so nothing folded away is out of reach.
	const VISIBLE_RUNGS = 3; // unlocked rungs kept beside the frontier

	const ladderRungs = $derived.by(() => {
		const from = Math.max(baseBpm, unlockedBpm - (VISIBLE_RUNGS - 1) * BPM_STEP);
		const shown = tiers.filter((v) => v >= from);
		// A slower rung stays on screen while it is the one selected — the control
		// must never hide what it is set to.
		if (selectedBpm < from) shown.unshift(selectedBpm);
		return shown;
	});

	// One menu covers every rung, so it only has to appear when something is missing
	// from the ladder — and only once, in the same place each time: the slow end.
	const hasFoldedRungs = $derived(unlockedRungs.some((v) => !ladderRungs.includes(v)));

	// A rung the student has not earned yet.
	const isLocked = (v: number) => v > unlockedBpm;
	// There is a freshly unlocked, faster rung sitting above the current choice — the
	// cue to climb. Drives both the "Increase BPM" hint and the glow on that rung.
	const canIncrease = $derived(selectedBpm < unlockedBpm);

	// The lesson that follows this one in the curriculum order, and whether it has
	// been earned yet — the "Next lesson →" button appears only once it is unlocked.
	const nextLesson = $derived.by(() => {
		if (!selected) return null;
		const i = lessons.findIndex((l) => l.id === selected!.id);
		return i >= 0 && i + 1 < lessons.length ? lessons[i + 1] : null;
	});
	const nextUnlocked = $derived(!!nextLesson && unlockedLessons.has(nextLesson.id));

	// A locked Next lesson still shows — a curriculum you cannot see the shape of is
	// not a curriculum — so it has to say what would open it, and how close you are.
	const nextLessonHint = $derived(
		`Finish this lesson at ${NEXT_LESSON_BPM} BPM to unlock it. ` +
			`Your ceiling here is ${unlockedBpm} BPM.`
	);

	// The lesson before this one. Unlike the next one it carries no condition: going
	// back is revision, and a student who is here has already been there.
	const prevLesson = $derived.by(() => {
		if (!selected) return null;
		const i = lessons.findIndex((l) => l.id === selected!.id);
		return i > 0 ? lessons[i - 1] : null;
	});

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
	// Everything the drum player needs decoded before a run: the lesson's own pads
	// plus the count-in click and the guide hat, neither of which is a lane and so
	// neither of which ever appears in `lanes`.
	const kitNotes = $derived([
		...lanes,
		...countIn.map((n) => n.note),
		...guide.map((n) => n.note)
	]);
	const hasMapping = $derived(ctrlMap.size > 0);
	// Nothing to draw for a student who has never run the setup wizard.
	const hasPadLayout = $derived(padCols > 0 && padRows > 0 && padDrums.length > 0);

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

	// The brief and the pattern chart need no audio, so they load on mount and the
	// page is readable before the user opts into sound.
	async function loadCatalogue() {
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
		}
	}

	// Follow the route: this component is reused across /lessons/[id], so navigating
	// to the next lesson never remounts it. Selecting off `page.params.id` here — not
	// once in loadCatalogue — means the "Next lesson" link actually loads the lesson
	// rather than leaving the old one on screen until a full reload.
	$effect(() => {
		const id = page.params.id;
		if (!lessons.length || selected?.id === id) return;
		const wanted = lessons.find((l) => l.id === id);
		if (wanted) void selectLesson(wanted);
		else status = `No lesson "${id}" in the manifest`;
	});

	// Audio needs a user gesture, so the samplers and MIDI come up on the first
	// click of Play or Listen. MIDI is deliberately NOT awaited: requestMIDIAccess
	// stays pending until the user answers the browser's permission prompt, and
	// nothing about starting the transport should wait on that. Pads simply come
	// alive whenever access lands.
	async function enableAudio() {
		if (audioCtx) return;
		audioCtx = new AudioContext();
		player = new DrumPlayer(audioCtx);
		backingPlayer = new Sampler(audioCtx);
		void initMidi();
		await player.preload(kit, kitNotes);
		for (const t of backing) backingPlayer.preload(t.family, t.id, t.notes.map((n) => n.note));
	}

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
		transport = { start: null, stop: null };
		savedDeviceName = null;
		padCols = 0;
		padRows = 0;
		padDrums = [];
		try {
			const raw = localStorage.getItem(STORAGE_PREFIX + deviceId);
			if (!raw) return;
			const cfg = JSON.parse(raw);
			if (typeof cfg.deviceName === 'string') savedDeviceName = cfg.deviceName;
			transport = asBinding(cfg.transport);
			if (Array.isArray(cfg.notes) && Array.isArray(cfg.soundNotes)) {
				const m = new Map<number, number>();
				cfg.notes.forEach((cn: number, i: number) => m.set(cn, cfg.soundNotes[i]));
				ctrlMap = m;
				// Grids written before the wizard stored their shape still map fine;
				// they just have no layout to draw, so the schematic stays away.
				if (typeof cfg.cols === 'number' && typeof cfg.rows === 'number') {
					padCols = cfg.cols;
					padRows = cfg.rows;
					padDrums = Array.from(
						{ length: cfg.cols * cfg.rows },
						(_, i) => cfg.soundNotes[i] ?? null
					);
				}
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
		// The manifest's BPM is the ladder's base; a stored unlock can only sit above
		// it, and the chosen rung is clamped into the unlocked range.
		baseBpm = lesson.bpm;
		unlockedBpm = Math.max(baseBpm, readMaxBpm(lesson.id) ?? baseBpm);
		selectedBpm = Math.min(unlockedBpm, Math.max(baseBpm, readSelected(lesson.id) ?? unlockedBpm));
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
		countIn = parsed.countIn;
		countInCursor = 0;
		guide = parsed.guide;
		guideCursor = 0;
		resetScoring();
		beatPos = -COUNT_IN;
		status = '';
		player?.preload(kit, kitNotes);
		for (const t of backing) backingPlayer?.preload(t.family, t.id, t.notes.map((n) => n.note));
	}

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

	// The controller's own Play / Stop buttons, when the wizard captured them.
	// Start also doubles as resume, so a single mapped button can drive a whole
	// run without touching the screen. Stop pauses first and only ends the run on
	// a second press, matching how hardware transports behave.
	function handleTransport(which: 'start' | 'stop') {
		if (which === 'start') {
			if (!playing) void play();
			else if (paused) togglePause();
			return;
		}
		if (!playing) return;
		if (!paused) togglePause();
		else stop();
	}

	// Returns true when the message was a transport press and has been consumed.
	function routeTransport(data: Uint8Array): boolean {
		if (!transport.start && !transport.stop) return false;
		const hit = parseControl(data);
		if (!hit || !hit.pressed) return false;
		// A pad always plays its drum, even if a stale config also bound it here.
		if (hit.control.kind === 'note' && ctrlMap.has(hit.control.data1)) return false;
		if (sameControl(hit.control, transport.start)) {
			handleTransport('start');
			return true;
		}
		if (sameControl(hit.control, transport.stop)) {
			handleTransport('stop');
			return true;
		}
		return false;
	}

	function handleMidi(event: MIDIMessageEvent) {
		// A hidden tab is deaf: ignore every message so nothing sounds or scores
		// while the page is in the background (see handleVisibility).
		if (typeof document !== 'undefined' && document.hidden) return;
		if (!event.data || event.data.length === 0) return;
		if (routeTransport(event.data)) return;

		if (event.data.length < 3) return;
		const [statusByte, note, velocity] = event.data;
		if ((statusByte & 0xf0) !== 0x90 || velocity === 0) return;

		const gm = ctrlMap.get(note);
		if (gm == null) return; // not a mapped pad
		player?.play(kit, gm); // the ONLY sound source — the user's own playing
		flash(gm);
		// Sample the beat straight from the audio clock at the moment of the hit, so
		// timing accuracy doesn't depend on the coarse scheduler cadence.
		//
		// Hits are scored from one match window BEFORE beat 0, not from beat 0 itself:
		// the first target sits on the down-beat, so its early half-window reaches back
		// into the count-in. Cutting the scan off at 0 made an entry a hair early — the
		// normal way a player anticipates a count-in — vanish entirely, and the
		// down-beat then reddened as a miss it was never given the chance to match.
		// Anything earlier than that is still ignored, so warming up on the clicks
		// costs nothing.
		if (playing && !paused) {
			const hitBeat = currentBeat();
			if (hitBeat >= -MATCH_WINDOW_BEATS) registerHit(gm, hitBeat);
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

		// The count-in rides the same clock and the same lookahead, so the three
		// clicks sit exactly one beat apart ahead of the student's first hit.
		while (countInCursor < countIn.length && countIn[countInCursor].beat <= horizon) {
			const click = countIn[countInCursor++];
			player?.playAt(kit, click.note, Math.max(beatToAudioTime(click.beat), ctx.currentTime));
		}

		// The borrowed hat, on the same lookahead. It starts at beat 0, so the
		// count-in still leads in alone and the hat arrives with the pattern.
		while (guideCursor < guide.length && guide[guideCursor].beat <= horizon) {
			const g = guide[guideCursor++];
			player?.playAt(
				kit,
				g.note,
				Math.max(beatToAudioTime(g.beat), ctx.currentTime),
				(g.vel ?? 100) / 100
			);
		}

		backing.forEach((track, ti) => {
			let c = backingCursors[ti];
			while (c < track.notes.length && track.notes[c].beat <= horizon) {
				const when = Math.max(beatToAudioTime(track.notes[c].beat), ctx.currentTime);
				const bn = track.notes[c];
				backingPlayer?.playAt(track.family, track.id, bn.note, when, (bn.vel ?? 100) / 100);
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

	// Tempo is chosen before a run, never during one: the scroll, the scheduler and
	// the scoring window all derive from `bpm`, so moving it mid-flight would shift
	// the segment the compositor is already animating. The ladder lives on the
	// resting page only, and stopping Listen keeps a preview from being split
	// across two tempos. A locked rung cannot be chosen — it must be earned first.
	function selectTier(value: number) {
		if (isLocked(value)) return;
		stopDemo();
		selectedBpm = value;
		writeSelected(value);
	}

	// Climb one rung and run again — the natural next move after a clean run has
	// unlocked a faster tempo. Offered on the result screen beside Try again / Done.
	function increaseAndPlay() {
		selectTier(Math.min(unlockedBpm, selectedBpm + BPM_STEP));
		void play();
	}

	// Two things can be earned by finishing a run:
	//  - the next rung, when the run was clean (no skipped note) at the top unlocked
	//    rung — only the frontier advances, so replaying an easier rung does nothing;
	//  - the next lesson, once the run was finished at NEXT_LESSON_BPM or faster.
	function maybeUnlock(r: Report) {
		if (!selected) return;
		if (isCleanRun(r) && selectedBpm === unlockedBpm) {
			unlockedBpm = selectedBpm + BPM_STEP;
			writeMaxBpm(selected.id, unlockedBpm);
		}
		if (nextLesson && selectedBpm >= NEXT_LESSON_BPM) unlockLesson(nextLesson.id);
	}

	// ---- earned progress (localStorage) -----------------------------------
	//
	// localStorage, not the stats database: these are read synchronously while the
	// page builds itself, and IndexedDB would hand them back a frame or two later —
	// after the ladder had already painted with everything locked.

	// The ceiling: the fastest rung this student is allowed to select for a given
	// lesson. Stored per lesson, because a tempo earned on 1.1 says nothing about
	// what is playable on 2.9 — every lesson has its own ladder and its own top.
	const maxBpmKey = (lessonId: string) => STORAGE_PREFIX + 'maxbpm:' + lessonId;
	// What that key used to be called. Read as a fallback and rewritten under the
	// new name, so nobody's earned ceiling resets on the way past.
	const legacyMaxBpmKey = (lessonId: string) => STORAGE_PREFIX + 'unlocked:' + lessonId;
	const selectedKey = (lessonId: string) => STORAGE_PREFIX + 'tier:' + lessonId;
	const LESSONS_KEY = STORAGE_PREFIX + 'lessons-unlocked';

	function readRung(key: string): number | null {
		try {
			const raw = localStorage.getItem(key);
			if (raw == null) return null;
			const n = Number(raw);
			if (!Number.isFinite(n) || n <= 0) return null;
			// Snap to the ladder in case an old value drifted off a rung.
			return Math.round(n / BPM_STEP) * BPM_STEP;
		} catch {
			return null; // no storage (private mode) — the base tempo still works
		}
	}

	/** The highest BPM this lesson may be played at, or null if none is stored. */
	function readMaxBpm(lessonId: string): number | null {
		const current = readRung(maxBpmKey(lessonId));
		if (current != null) return current;
		const legacy = readRung(legacyMaxBpmKey(lessonId));
		if (legacy != null) writeMaxBpm(lessonId, legacy); // migrate on first read
		return legacy;
	}

	const readSelected = (lessonId: string) => readRung(selectedKey(lessonId));

	function writeMaxBpm(lessonId: string, value: number) {
		try {
			localStorage.setItem(maxBpmKey(lessonId), String(value));
			localStorage.removeItem(legacyMaxBpmKey(lessonId));
		} catch {
			// Storage full or blocked — progress just will not be remembered.
		}
	}

	function writeSelected(value: number) {
		if (!selected) return;
		try {
			localStorage.setItem(selectedKey(selected.id), String(value));
		} catch {
			// Storage full or blocked — the chosen rung just will not be remembered.
		}
	}

	function readUnlockedLessons(): Set<string> {
		try {
			const raw = localStorage.getItem(LESSONS_KEY);
			const ids = raw ? JSON.parse(raw) : [];
			return new Set(Array.isArray(ids) ? ids.filter((i) => typeof i === 'string') : []);
		} catch {
			return new Set();
		}
	}

	function unlockLesson(lessonId: string) {
		if (unlockedLessons.has(lessonId)) return;
		unlockedLessons = new Set([...unlockedLessons, lessonId]);
		try {
			localStorage.setItem(LESSONS_KEY, JSON.stringify([...unlockedLessons]));
		} catch {
			// Storage full or blocked — the unlock just will not persist.
		}
	}

	async function play() {
		if (!parsed || playing) return;
		await enableAudio(); // no-op once audio is already up
		stopDemo(); // the in-place preview and the real run never overlap
		await audioCtx?.resume();
		await player?.preload(kit, kitNotes);
		resetScoring();
		backingCursors = backing.map(() => 0);
		countInCursor = 0;
		guideCursor = 0;
		report = null;
		beatPos = -COUNT_IN;
		startBeat = -COUNT_IN;
		playing = true;
		paused = false;
		if (selected) lessonStarted(selected.id);
		// The highway only exists during a session, so let it mount before the
		// scroll and the clock start from it.
		await tick();
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

	// Page Visibility: a backgrounded tab must be silent and deaf. Hiding freezes a
	// running lesson — it only ever resumes on a manual Play/Resume, never on its
	// own — stops any Listen preview, and suspends the audio graph so nothing plays.
	// Coming back just re-arms the graph; the transport stays wherever the user left it.
	function handleVisibility() {
		if (document.hidden) {
			stopDemo();
			if (playing && !paused) togglePause();
			void audioCtx?.suspend();
		} else {
			void audioCtx?.resume();
		}
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
		// Build once and keep the plain object: `report` is $state, so reading it
		// back yields a proxy, and structuredClone (what IndexedDB writes through)
		// throws on those.
		const built = buildReport();
		report = built;
		if (selected) lessonFinished(selected.id);
		maybeUnlock(built);
		void logSession(built);
		beatPos = parsed ? parsed.lengthBeats : 0;
		updateStrip();
	}

	// File the finished run in the practice history behind /stats. Fire-and-forget
	// and non-throwing by contract (see $lib/stats): the result screen is already
	// on screen and must not wait on, or be broken by, a storage failure.
	async function logSession(r: Report) {
		if (!selected) return;
		const at = Date.now();
		await recordSession({
			at,
			day: dayKey(at),
			lesson: selected.id,
			lessonName: selected.name,
			bpm,
			device: inputs.find((i) => i.id === selectedId)?.name ?? savedDeviceName,
			deviceId: selectedId,
			total: r.total,
			hits: r.hits,
			perfect: r.perfect,
			good: r.good,
			off: r.off,
			miss: r.miss,
			extra: r.extra,
			accuracy: r.accuracy,
			avgAbsMs: r.avgAbsMs,
			early: r.early,
			late: r.late,
			durationMs: ((parsed?.lengthBeats ?? 0) + COUNT_IN) * (60000 / bpm),
			grade: r.grade,
			lanes: r.lanes.map((l) => ({
				note: l.note,
				name: l.name,
				total: l.total,
				hits: l.hits,
				avgMs: l.avgMs
			}))
		});
	}

	// ---- listen (in-place preview) --------------------------------------
	//
	// Deliberately separate from the transport above: Listen is a preview of the
	// chart the student is looking at, so it must not take over the page. It plays
	// the drum track and the backing straight off the audio clock, walks a playhead
	// across the chart, and never touches scoring or the highway.

	let demoing = $state(false);
	let demoBeat: number | null = $state(null); // playhead position, null when idle
	let demoStart = 0; // audio time of the preview's beat 0
	let demoTimer: ReturnType<typeof setInterval> | 0 = 0;
	let demoRaf = 0;
	let demoDrumCursor = 0;
	let demoGuideCursor = 0;
	let demoBackCursors: number[] = [];

	const demoBeatTime = (beat: number) => demoStart + beat * (60 / bpm);

	async function toggleListen() {
		if (demoing) {
			stopDemo();
			return;
		}
		await enableAudio();
		if (!parsed || !audioCtx) return;
		await audioCtx.resume();
		await player?.preload(kit, kitNotes);
		demoDrumCursor = 0;
		demoGuideCursor = 0;
		demoBackCursors = backing.map(() => 0);
		// Listen skips the count-in and starts on beat 0 straight away: nobody is
		// playing along, so a bar of clicks would just be a wait before the preview.
		// Counting in belongs to Play, where it lines the student up.
		demoStart = audioCtx.currentTime + 0.25; // brief lead-in so nothing clips
		demoing = true;
		demoSchedule();
		demoTimer = setInterval(demoSchedule, SCHED_INTERVAL_MS);
		trackPlayhead();
	}

	function demoSchedule() {
		if (!demoing || !parsed || !audioCtx) return;
		const ctx = audioCtx;
		const beat = (ctx.currentTime - demoStart) * (bpm / 60);
		const horizon = beat + (SCHED_LOOKAHEAD_SEC * bpm) / 60;

		while (demoDrumCursor < parsed.notes.length && parsed.notes[demoDrumCursor].beat <= horizon) {
			const n = parsed.notes[demoDrumCursor++];
			const when = Math.max(demoBeatTime(n.beat), ctx.currentTime);
			player?.playAt(kit, n.note, when);
			setTimeout(() => flash(n.note), Math.max(0, (when - ctx.currentTime) * 1000));
		}

		// The preview is what the lesson sounds like, so the borrowed hat belongs
		// in it — without it the groove previews differently from how it plays. It
		// flashes nothing: there is no lane of its own to light up.
		while (demoGuideCursor < guide.length && guide[demoGuideCursor].beat <= horizon) {
			const g = guide[demoGuideCursor++];
			player?.playAt(
				kit,
				g.note,
				Math.max(demoBeatTime(g.beat), ctx.currentTime),
				(g.vel ?? 100) / 100
			);
		}

		backing.forEach((track, ti) => {
			let c = demoBackCursors[ti];
			while (c < track.notes.length && track.notes[c].beat <= horizon) {
				const when = Math.max(demoBeatTime(track.notes[c].beat), ctx.currentTime);
				const bn = track.notes[c];
				backingPlayer?.playAt(track.family, track.id, bn.note, when, (bn.vel ?? 100) / 100);
				c++;
			}
			demoBackCursors[ti] = c;
		});

		if (beat >= parsed.lengthBeats) stopDemo();
	}

	// The playhead is a single SVG line, so a plain rAF is cheap here — unlike the
	// highway, nothing else is animating while the preview runs.
	function trackPlayhead() {
		cancelAnimationFrame(demoRaf);
		const step = () => {
			if (!demoing || !audioCtx || !parsed) return;
			demoBeat = Math.max(0, Math.min(parsed.lengthBeats, (audioCtx.currentTime - demoStart) * (bpm / 60)));
			demoRaf = requestAnimationFrame(step);
		};
		demoRaf = requestAnimationFrame(step);
	}

	function stopDemo() {
		if (!demoing && !demoTimer) return;
		demoing = false;
		demoBeat = null;
		if (demoTimer) {
			clearInterval(demoTimer);
			demoTimer = 0;
		}
		cancelAnimationFrame(demoRaf);
		demoRaf = 0;
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
		unlockedLessons = readUnlockedLessons();
		// Read the saved controller up front, before (and whether or not) MIDI is
		// granted: the schematic is part of the resting page, not of a live session.
		// Connecting a device re-runs this through the port effect below.
		const savedDevice = localStorage.getItem(STORAGE_PREFIX + 'selectedDevice');
		if (savedDevice) loadDeviceMapping(savedDevice);
		window.addEventListener('resize', measure);
		document.addEventListener('visibilitychange', handleVisibility);
		void loadCatalogue();
		return () => {
			window.removeEventListener('resize', measure);
			document.removeEventListener('visibilitychange', handleVisibility);
		};
	});

	onDestroy(() => {
		if (!browser) return;
		stopDemo();
		stop();
		audioCtx?.close();
	});
</script>

<!-- The manifest is fetched in onMount, so a crawler — which never runs the
     script — only ever sees the fallbacks. Naming the lesson in a shared link
     would mean loading the manifest in a +page.ts instead. -->
<PageMeta
	title="Groove Academy — {selected?.name ?? 'Lesson'}"
	description={selected?.description ??
		'A looping groove that scrolls toward the hit line. Play it on a MIDI kit or the on-screen pads.'}
/>

<a class="back" href="{base}/lessons">← All lessons</a>
<h1>
	{#if selected}<span class="number">{selected.number}</span>{/if}{selected?.name ?? 'Lesson'}
</h1>

{#if selected?.description && !inSession}
	<p class="description">{selected.description}</p>
{/if}

{#if parsed && !inSession}
	<div class="chart-frame" class:with-pads={hasPadLayout}>
		{#if hasPadLayout}
			<ControllerMap
				cols={padCols}
				rows={padRows}
				drums={padDrums}
				{lanes}
				lit={flashing}
				{laneName}
			/>
		{/if}
		<LessonChart
			notes={parsed.notes}
			{lanes}
			lengthBeats={parsed.lengthBeats}
			{laneName}
			playhead={demoBeat}
		/>
		<div class="chart-actions">
			<button class="listen" class:running={demoing} onclick={toggleListen}>
				{demoing ? '■ Stop' : '▶ Listen'}
			</button>
			<span class="listen-hint">
				{demoing
					? 'Playing the groove here — nothing scored.'
					: 'Hear the groove right here: drums and backing, nothing scored.'}
			</span>
		</div>
	</div>
{/if}

{#if selected?.hints?.length && !inSession}
	<ul class="hints">
		{#each selected.hints as hint (hint)}
			<li>{hint}</li>
		{/each}
	</ul>
{/if}

<!-- The resting page keeps one shape whether or not audio is up and whether or not
	 a lesson has already been run: brief, chart, hints, Play. -->
{#if !inSession}
	<div class="launch">
		<div class="launch-nav to-prev">
			{#if prevLesson}
				<a class="lesson-nav" href="{base}/lessons/{prevLesson.id}">
					<span aria-hidden="true">←</span>
					<span class="nav-label">Previous lesson</span>
				</a>
			{/if}
		</div>

		<div class="launch-controls">
			<button class="start-btn play" onclick={() => play()} disabled={!parsed}>▶ Play</button>

			<div class="ladder" role="group" aria-label="Tempo (beats per minute)">
				<span class="rung label">BPM</span>
				{#if hasFoldedRungs}
					<!-- The rungs folded away, as one menu at the slow end of the ladder.
					     The select carries the whole interaction — keyboard, touch, click —
					     and sits invisibly over the chip, so all that shows is the caret. -->
					<div class="rung jump">
						<span aria-hidden="true">▾</span>
						<select
							aria-label="Jump to a tempo"
							title="Jump to any unlocked tempo"
							onchange={(e) => {
								const value = Number(e.currentTarget.value);
								e.currentTarget.selectedIndex = 0; // back to the caret
								if (value) selectTier(value);
							}}
						>
							<option value="">Jump to…</option>
							{#each unlockedRungs as rung (rung)}
								<option value={rung} disabled={rung === selectedBpm}>{rung} BPM</option>
							{/each}
						</select>
					</div>
				{/if}
				{#each ladderRungs as tier (tier)}
					<button
						class="rung"
						class:selected={tier === selectedBpm}
						class:locked={isLocked(tier)}
						class:glow={tier === unlockedBpm && canIncrease}
						onclick={() => selectTier(tier)}
						disabled={isLocked(tier)}
						aria-pressed={tier === selectedBpm}
						title={isLocked(tier) ? `Play ${tier - BPM_STEP} cleanly to unlock` : `${tier} BPM`}
					>
						{#if tier === unlockedBpm && canIncrease}
							<span class="increase-hint">Increase BPM</span>
						{/if}
						{#if isLocked(tier)}
							<span class="lock" aria-hidden="true">🔒</span>
						{:else}
							{tier}
						{/if}
					</button>
				{/each}
				<span class="rung ellipsis" aria-hidden="true">…</span>
			</div>
		</div>

		<div class="launch-nav to-next">
			{#if nextLesson}
				{#if nextUnlocked}
					<a class="lesson-nav next" href="{base}/lessons/{nextLesson.id}">
						<span class="nav-label">Next lesson</span>
						<span aria-hidden="true">→</span>
					</a>
				{:else}
					<button class="lesson-nav next locked" disabled title={nextLessonHint}>
						<span class="nav-label">Next lesson</span>
						<span class="lock" aria-hidden="true">🔒</span>
					</button>
				{/if}
			{/if}
		</div>
	</div>

	{#if status}<p class="warn">{status}</p>{/if}

	{#if audioCtx && !hasMapping}
		<p class="warn">
			No pad mapping for this device. Set one up on the
			<a href="{base}/onboarding">Setup</a> page so your hits make sound and get scored.
		</p>
	{/if}
{/if}

{#if inSession}
	{#if playing}
		<div class="hud">
			<span class="hud-tempo">{bpm} BPM</span>
			<button class="pause-btn" onclick={togglePause}>{paused ? '▶ Resume' : '❚❚ Pause'}</button>
			<button class="exit" onclick={stop}>■ Stop</button>
		</div>
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
								NOTE / 2}px; {statuses[i] === 'pending'
								? `background: ${laneColor(n.note, laneRow(n.note))}`
								: ''}"
						></div>
					{/each}
				</div>
			</div>
		</div>
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
				<button class="play" onclick={() => play()}>Try again</button>
				{#if canIncrease}
					<button class="increase-btn" onclick={increaseAndPlay}>
						Increase BPM → {Math.min(unlockedBpm, selectedBpm + BPM_STEP)}
					</button>
				{/if}
				{#if nextLesson && nextUnlocked}
					<a class="lesson-nav next" href="{base}/lessons/{nextLesson.id}">
						<span class="nav-label">Next lesson</span>
						<span aria-hidden="true">→</span>
					</a>
				{:else if nextLesson}
					<button class="lesson-nav next locked" disabled title={nextLessonHint}>
						<span class="nav-label">Next lesson</span>
						<span class="lock" aria-hidden="true">🔒</span>
					</button>
				{/if}
				<button class="done" onclick={exitReport}>Done</button>
			</div>
		</div>
	{/if}
{/if}

<style>
	.back {
		display: inline-block;
		margin-top: 0.75rem;
		font-family: var(--font-mono);
		font-size: 0.8rem;
		color: var(--text-muted);
		text-decoration: none;
	}

	.back:hover {
		color: var(--text);
	}

	h1 {
		margin-top: 0.25rem;
	}

	/* The number is position, the name is identity — so it reads as a label
	   beside the title rather than part of it. */
	h1 .number {
		margin-right: 0.6rem;
		font-family: var(--font-mono);
		font-size: 0.75em;
		color: var(--text-muted);
	}

	/* Pattern reference while the transport is at rest — same chart the catalogue shows. */
	.chart-frame {
		margin: 0 0 1rem;
		padding: 0.55rem 0.7rem;
		background: var(--bg);
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
	}

	/* With a controller to show, the frame becomes two columns — device on the
	   left, chart on the right — and the actions row dissolves into that same grid
	   (display: contents) so Listen lands squarely under the pads and its hint
	   under the chart. Nothing is nested crookedly: one grid, two columns, and the
	   button's left and right edges are the controller's. */
	.chart-frame.with-pads {
		display: grid;
		grid-template-columns: auto minmax(0, 1fr);
		align-items: center;
		column-gap: 0.9rem;
		row-gap: 0.5rem;
	}

	.chart-actions {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		flex-wrap: wrap;
		margin: 0.5rem 0.2rem 0.15rem;
	}

	.with-pads .chart-actions {
		display: contents;
	}

	.with-pads .listen {
		width: 100%;
		min-width: 0;
	}

	.listen {
		font-size: 0.9rem;
		padding: 0.35em 0.9em;
		min-width: 6.5em;
	}

	.listen.running {
		border-color: var(--gold);
		color: var(--gold);
	}

	.listen-hint {
		font-size: 0.82rem;
		color: var(--text-faint);
	}

	.hints {
		margin: 0 0 1.25rem;
		padding-left: 1.1rem;
		color: var(--text-muted);
		font-size: 0.9rem;
		line-height: 1.55;
	}

	.hints li {
		margin-bottom: 0.3rem;
	}

	.hints li::marker {
		color: var(--gold);
	}

	/* Play, the tempo ladder and the two lesson links share one row and one height,
	   so the rungs read as squares sitting flush beside the buttons.

	   Three zones across the full width: step back, the controls, step forward. The
	   outer columns are equal fractions and are rendered even when empty, so the
	   controls stay centred on the first lesson (no Previous) and on an un-earned
	   one (no Next) rather than sliding as you move through the curriculum. */
	.launch {
		--ctl-h: 3.1rem;
		display: grid;
		/* The outer columns never shrink below their own label (min-content on a
		   nowrap link is its full width), and the middle one is allowed to go to
		   zero — so a ladder long enough to fill the row wraps inside itself
		   instead of crushing "Previous lesson" down to its arrow. An absent link
		   has a min-content of 0, which is what keeps the controls centred on the
		   first lesson. */
		grid-template-columns:
			minmax(min-content, 1fr)
			minmax(0, auto)
			minmax(min-content, 1fr);
		align-items: center;
		gap: 0.75rem;
		margin: 2rem 0 0.5rem;
	}

	.launch-nav {
		display: flex;
		min-width: 0;
	}

	.launch-nav.to-prev {
		justify-content: flex-start;
	}

	.launch-nav.to-next {
		justify-content: flex-end;
	}

	.launch-controls {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		min-width: 0;
	}

	/* Narrow: one column. Play and the ladder stack full width, and the two lesson
	   links share the row beneath — the pair reads as "where am I" once, instead of
	   pushing the ladder off the screen to sit beside it. */
	@media (max-width: 46rem) {
		/* The controller keeps its place beside the chart on a phone — the two only
		   make sense read together — so only the gap between them gives way here;
		   the pads shrink themselves (see controller-map.svelte). */
		.chart-frame.with-pads {
			column-gap: 0.55rem;
		}

		.launch {
			grid-template-columns: 1fr 1fr;
			grid-template-areas:
				"controls controls"
				"to-prev to-next";
		}

		.launch-controls {
			grid-area: controls;
			flex-direction: column;
			align-items: stretch;
			/* Stacked, the ladder sits under Play — leaving the "Increase BPM"
			   callout, which points down at a rung from above the control, room to
			   land on. Reserved whether or not it is showing, so the column does not
			   shift when it appears. */
			gap: 2.25rem;
		}

		.launch-nav.to-prev {
			grid-area: to-prev;
		}

		.launch-nav.to-next {
			grid-area: to-next;
		}

		.launch-controls .start-btn {
			width: 100%;
		}

		.launch-nav .lesson-nav {
			flex: 1;
			justify-content: center;
		}

		/* Full width under a full-width Play button, so the rungs share the row
		   instead of huddling at the left with dead space beside them. They only
		   grow — min-width still floors them, and past that the ladder wraps. */
		.launch-controls .rung {
			flex: 1 0 auto;
		}
	}

	/* Tempo picker — only on the resting page, so a run can never change tempo
	   underneath itself. The rungs form one connected segmented control: a leading
	   "BPM" label, a caret menu holding any slow rungs folded away, the rungs around
	   the frontier, three locked ones ahead, then an ellipsis standing in for the
	   climb beyond. Only the group's outer corners are rounded; the rungs share hairline
	   dividers. A locked rung must be earned by clearing the one below it without
	   skipping a note. */
	/* Deliberately not a scroll container. `overflow-x: auto` also makes an element
	   scroll vertically, and the "Increase BPM" callout is positioned above its rung
	   — so the ladder grew a scrollbar and resized its own rungs every time that
	   callout appeared. Folding keeps the width in hand; a ladder that still outruns
	   its row (unfolded, or a phone) wraps to a second line instead. */
	.ladder {
		display: flex;
		flex-wrap: wrap;
		align-items: stretch;
		align-content: flex-start;
		min-height: var(--ctl-h);
		border: 1px solid var(--border-strong);
		border-radius: var(--radius-sm);
		min-width: 0;
	}

	.rung {
		position: relative;
		min-width: var(--ctl-h);
		/* Sets the row height now that the ladder is free to wrap: without it the
		   rungs would shrink to their text on a wrapped line. */
		height: calc(var(--ctl-h) - 2px);
		flex: 0 0 auto;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 0 0.35rem;
		background: var(--surface-2);
		border: none;
		border-right: 1px solid var(--border-strong);
		border-radius: 0;
		color: var(--text-muted);
		font-family: var(--font-mono);
		font-size: 0.95rem;
		cursor: pointer;
		transition:
			color 120ms ease,
			background 120ms ease;
	}

	/* Only the group's outer corners are rounded — round the end segments to match
	   the container so a coloured rung never squares off a corner. */
	.rung:first-child {
		border-top-left-radius: var(--radius-sm);
		border-bottom-left-radius: var(--radius-sm);
	}

	.rung:last-child {
		border-right: none;
		border-top-right-radius: var(--radius-sm);
		border-bottom-right-radius: var(--radius-sm);
	}

	/* The "BPM" caption and the trailing ellipsis are read-outs, not controls. */
	.rung.label,
	.rung.ellipsis {
		cursor: default;
		background: var(--surface);
		color: var(--text-faint);
		font-size: 0.75rem;
		letter-spacing: 0.04em;
	}

	.rung.ellipsis {
		font-size: 1rem;
	}

	/* The jump menu: a caret drawn as a rung, with the real <select> laid over it at
	   zero opacity. The native control keeps its own popup, keyboard handling and
	   touch behaviour; only the caret is ours. */
	.rung.jump {
		cursor: pointer;
		background: var(--surface);
		color: var(--text-muted);
		font-size: 0.85rem;
	}

	.rung.jump:hover {
		color: var(--text);
		background: var(--surface-3, var(--border));
	}

	.rung.jump select {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		padding: 0;
		border: none;
		opacity: 0;
		cursor: pointer;
		font: inherit;
	}

	/* Keyboard focus lands on the select, which is invisible — so the chip around it
	   has to carry the ring. */
	.rung.jump:focus-within {
		outline: 2px solid var(--gold);
		outline-offset: -2px;
	}

	.rung:not(.locked):not(.label):not(.ellipsis):hover {
		color: var(--text);
		background: var(--surface-3, var(--border));
	}

	.rung.selected {
		color: #1a1505;
		background: var(--gold);
		font-weight: 700;
	}

	.rung.locked {
		cursor: not-allowed;
		color: var(--text-faint);
	}

	.rung .lock {
		font-size: 0.75rem;
		line-height: 1;
	}

	/* The freshly unlocked rung pulses gold until the student climbs to it. A
	   background pulse (not an outer glow) so the clipped segmented group shows it. */
	.rung.glow {
		color: var(--gold);
		animation: rung-glow 1.2s ease-in-out infinite;
	}

	@keyframes rung-glow {
		0%,
		100% {
			background: var(--surface-2);
		}
		50% {
			background: color-mix(in srgb, var(--gold) 32%, var(--surface-2));
		}
	}

	/* A callout that sits above the freshly unlocked rung and points down at it, so
	   "Increase BPM" is tied to the rung to climb to — not floating by the buttons. */
	.increase-hint {
		position: absolute;
		bottom: calc(100% + 8px);
		left: 50%;
		transform: translateX(-50%);
		padding: 0.3em 0.6em;
		border-radius: var(--radius-sm);
		background: var(--gold);
		color: #1a1505;
		font-family: var(--font-mono);
		font-size: 0.72rem;
		font-weight: 700;
		white-space: nowrap;
		pointer-events: none;
	}

	/* Little downward arrow joining the callout to the rung. */
	.increase-hint::after {
		content: '';
		position: absolute;
		top: 100%;
		left: 50%;
		transform: translateX(-50%);
		border: 5px solid transparent;
		border-top-color: var(--gold);
	}

	/* Both curriculum links — Previous beside the controls, Next there and in the
	   result report. One style, so stepping back and stepping on look like the same
	   kind of move. */
	.lesson-nav {
		display: inline-flex;
		align-items: center;
		gap: 0.45rem;
		height: var(--ctl-h, auto);
		padding: 0.5em 1.1rem;
		border-radius: var(--radius-sm);
		background: var(--surface-2);
		border: 1px solid var(--border-strong);
		color: var(--text);
		font-size: 0.95rem;
		text-decoration: none;
		white-space: nowrap;
		min-width: 0;
	}

	.lesson-nav:hover {
		border-color: var(--gold);
		color: var(--gold);
	}

	/* A button, not a link, because there is nowhere to go yet. Same footprint as
	   the earned version so the row does not reflow when it opens. */
	.lesson-nav.locked {
		font-family: inherit;
		color: var(--text-faint);
		background: var(--surface);
		border-style: dashed;
		cursor: not-allowed;
	}

	.lesson-nav.locked:hover {
		border-color: var(--border-strong);
		color: var(--text-faint);
	}

	.lesson-nav .lock {
		font-size: 0.85em;
		opacity: 0.75;
	}

	/* Below the smallest phones the label would wrap the arrow onto its own line;
	   the arrow alone still says which way it goes. */
	@media (max-width: 24rem) {
		.launch-nav .nav-label {
			overflow: hidden;
			text-overflow: ellipsis;
		}
	}

	.play {
		height: var(--ctl-h, auto);
		padding: 0.5em 1.5rem;
		background: #2a7;
		color: #fff;
		border: 1px solid #185;
		border-radius: 0.3rem;
		font-weight: bold;
	}

	.description {
		margin: 0 0 1rem;
		color: #aab;
		font-size: 0.92rem;
		line-height: 1.5;
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

	/* Transport controls over the fullscreen highway, tempo readout included so the
	   ?bpm= override is visible while playing. */
	.hud {
		position: fixed;
		top: 1rem;
		right: 1rem;
		z-index: 60;
		display: flex;
		align-items: center;
		gap: 0.6rem;
	}

	.hud-tempo {
		padding: 0.4em 0.7em;
		border-radius: 0.3rem;
		background: rgba(12, 13, 22, 0.75);
		border: 1px solid var(--border-strong);
		font-family: var(--font-mono);
		font-size: 0.85rem;
		color: var(--gold);
	}

	.exit {
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
		/* Pending notes get their drum-family colour inline (see markup); this is the
		   fallback if that is ever absent — an identity hue, never a result one.
		   Status classes below recolour a scored note into the result band. */
		background: var(--note-1);
		transition: background 0.1s ease;
		contain: layout paint;
	}

	.note.good {
		background: var(--res-good);
		box-shadow: 0 0 4px color-mix(in srgb, var(--res-good) 55%, transparent);
	}

	.note.perfect {
		background: var(--res-perfect);
		box-shadow: 0 0 8px color-mix(in srgb, var(--res-perfect) 90%, transparent);
		animation: pop 0.28s ease;
	}

	.note.off {
		background: var(--res-off);
		box-shadow: 0 0 4px color-mix(in srgb, var(--res-off) 40%, transparent);
	}

	.note.miss {
		background: var(--res-miss);
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

	/* Climb-a-rung shortcut on the result screen — gold, so it reads as the reward
	   for a clean run rather than just another neutral action. */
	.increase-btn {
		background: var(--gold);
		color: #1a1505;
		border: 1px solid var(--gold);
		border-radius: 0.3rem;
		font-weight: bold;
		padding: 0.4em 0.9em;
		cursor: pointer;
	}

	.increase-btn:hover {
		background: #f6cd5e;
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

	/* The grade is the coarsest result there is, so it walks the result band end
	   to end: green at S, through amber, to red at E. Hue now falls monotonically
	   with the grade (it used to rise from S to A, and A sat at hue 168 — a teal
	   that had drifted out of the band and within 37° of the hi-hat note colour).
	   White on every step clears 3:1 at this size. */
	.grade-S {
		background: #3ca059; /* oklch(.63 .14 150) */
	}
	.grade-A {
		background: #749331; /* oklch(.62 .13 125) */
	}
	.grade-B {
		background: #998700; /* oklch(.62 .13 100) */
	}
	.grade-C {
		background: #a87520; /* oklch(.60 .115 75) */
	}
	.grade-D {
		background: #ae5528; /* oklch(.55 .13  45) */
	}
	.grade-E {
		background: #a43b38; /* oklch(.50 .14  25) */
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

	/* Each chip is its own result hue, tinted into the page for the fill and
	   lifted toward the text colour for the label — so the scoreline reads with
	   the same vocabulary as the notes it is counting. "perfect" used to be teal
	   on cyan, which is now note-identity territory. All four clear 4.5:1. */
	.chip.perfect {
		background: color-mix(in srgb, var(--res-perfect) 18%, var(--bg));
		color: color-mix(in srgb, var(--res-perfect) 70%, var(--text));
	}
	.chip.good {
		background: color-mix(in srgb, var(--res-good) 18%, var(--bg));
		color: color-mix(in srgb, var(--res-good) 70%, var(--text));
	}
	.chip.off {
		background: color-mix(in srgb, var(--res-off) 18%, var(--bg));
		color: color-mix(in srgb, var(--res-off) 70%, var(--text));
	}
	.chip.miss {
		background: color-mix(in srgb, var(--res-miss) 18%, var(--bg));
		color: color-mix(in srgb, var(--res-miss) 70%, var(--text));
	}
	/* Extra hits are not a grade on a target note, so they stay out of both
	   bands and read as neutral. */
	.chip.extra {
		background: var(--surface-3);
		color: var(--text-muted);
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
		font-size: 1.15rem;
		cursor: pointer;
		/* Play keeps its size whatever the ladder beside it does — an unfolded
		   ladder wrapping to a second line must not squeeze it onto two lines too. */
		flex: 0 0 auto;
		white-space: nowrap;
	}
</style>
