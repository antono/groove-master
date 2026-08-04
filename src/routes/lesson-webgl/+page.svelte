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
	const PERFECT_MS = 25; // exact  -> green
	const GOOD_MS = 60; // precise -> green
	// between GOOD_MS and the match window -> off (orange); past the window -> miss (red)
	const STORAGE_PREFIX = 'padrill:';

	let audioCtx: AudioContext | null = $state(null);
	let player: DrumPlayer | null = null;
	let backingPlayer: Sampler | null = null;

	// Backing tracks (bass, etc.) — auto-played, never shown or scored.
	// `backing` ($state) drives the pre-play UI only; the tick loop reads the
	// PLAIN `backingP` snapshot so no proxy traps run per frame.
	let backing: BackingTrack[] = $state([]);
	let backingP: BackingTrack[] = [];
	let backingCursors: number[] = []; // per-track note pointer, advanced in tick()
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
	// The parsed lesson stays a PLAIN object — never $state. Wrapping it in a
	// deep proxy puts a trap on every notes[i].beat read in the hot loop.
	let parsed: ParsedMidi | null = null;
	let ready = $state(false); // template gate for the highway
	let lanes: number[] = $state([]);
	let drumNames = $state(new Map<number, string>());

	let bpm = $state(60);
	let playing = $state(false);
	let paused = $state(false); // transport frozen mid-lesson; highway stays up
	let status = $state('');
	let beatPos = -COUNT_IN;

	// Per-target scoring state (parallel to parsed.notes). Plain arrays: the
	// notes are drawn by WebGL, not Svelte, so nothing here needs reactivity.
	let matched: boolean[] = [];
	let statuses: Status[] = [];
	let deltas: (number | null)[] = []; // signed ms, - = early
	let extras: { note: number; beat: number }[] = [];
	let report: Report | null = $state(null);

	// Note indices sorted by beat, plus a single advancing cursor, so the miss
	// scan touches only newly-passed notes instead of the whole array each frame.
	let missOrder: number[] = [];
	let missCursor = 0;

	let raf = 0;
	let lastTs = 0;
	let dpr = 1; // cached devicePixelRatio; refreshed on resize

	const laneName = (n: number) => drumNames.get(n) ?? String(n);
	const laneRow = (n: number) => lanesP.indexOf(n);
	const hasMapping = $derived(ctrlMap.size > 0);

	// Highway fills the whole viewport while playing; rests compact otherwise.
	let winH = $state(0);
	let lanesP: number[] = []; // plain copy of lanes for the hot path
	const laneH = $derived(
		playing && lanes.length ? Math.max(48, Math.floor(winH / lanes.length)) : LANE_H
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

	// Plain (non-reactive) mirror of the mapping for the MIDI hot path.
	let ctrlMapP: Map<number, number> = new Map();
	let kitP = 1;
	$effect(() => {
		ctrlMapP = new Map(ctrlMap);
		kitP = kit;
	});

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
		ready = false;
		status = 'Loading ' + lesson.name + '…';
		try {
			const res = await fetch(`${base}/lessons/${lesson.file}`);
			parsed = parseMidi(await res.arrayBuffer());
		} catch {
			status = 'Could not load lesson MIDI';
			return;
		}
		lanesP = [...new Set(parsed.notes.map((n) => n.note))].sort((a, b) => b - a);
		lanes = lanesP;
		backingP = parsed.backing; // plain, for the tick loop
		backing = parsed.backing; // reactive copy, for the pre-play UI
		backingCursors = backingP.map(() => 0);
		const bassTrack = backingP.find((t) => t.family === 'bass');
		if (bassTrack) selectedBass = bassTrack.id; // default to what the MIDI ships with
		resetScoring();
		beatPos = -COUNT_IN;
		status = '';
		ready = true;
		// Preload in the background; lesson geometry must not wait for audio.
		void player?.preload(kit, lanesP);
		void Promise.all(
			backingP.map((t) => backingPlayer?.preload(t.family, effId(t), t.notes.map((n) => n.note)))
		);
	}

	// Preload the chosen bass whenever the selection changes.
	$effect(() => {
		const id = selectedBass;
		for (const t of backingP) {
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
		resetNoteColors();
	}

	function registerHit(gmNote: number, hitBeat: number) {
		if (!parsed) return;
		const notes = parsed.notes;
		let best = -1;
		let bestDist = MATCH_WINDOW_BEATS;
		for (let i = 0; i < notes.length; i++) {
			if (matched[i] || notes[i].note !== gmNote) continue;
			const dist = Math.abs(notes[i].beat - hitBeat);
			if (dist < bestDist) {
				bestDist = dist;
				best = i;
			}
		}
		if (best === -1) {
			extras.push({ note: gmNote, beat: hitBeat });
			return;
		}
		const deltaMs = (hitBeat - notes[best].beat) * (60000 / bpmP);
		const abs = Math.abs(deltaMs);
		matched[best] = true;
		deltas[best] = deltaMs;
		statuses[best] = abs <= PERFECT_MS ? 'perfect' : abs <= GOOD_MS ? 'good' : 'off';
		writeNoteColor(best, statuses[best]);
		dynDirty = true;
	}

	function handleMidi(event: MIDIMessageEvent) {
		if (!event.data || event.data.length < 3) return;
		const [statusByte, note, velocity] = event.data;
		if ((statusByte & 0xf0) !== 0x90 || velocity === 0) return;

		const gm = ctrlMapP.get(note);
		if (gm == null) return; // not a mapped pad
		player?.play(kitP, gm); // the ONLY sound source — the user's own playing
		if (running && beatPos >= -0.001) registerHit(gm, beatPos);
	}

	// ---- WebGL highway ----------------------------------------------------
	//
	// Deliberately barebones. Per frame: one clear, two uniform writes, four
	// draw calls. No per-frame buffer uploads (note colors upload only when a
	// status changed), no allocations, no reactive reads.
	//
	// Edges are anti-aliased in the fragment shader (1px box-SDF ramp). This is
	// NOT decoration: without sub-pixel edges a ~5px-per-frame scroll rounds to
	// a different pixel phase every frame and hard edges visibly strobe —
	// temporal aliasing reads as jitter. (The MSAA context hint is ignored on
	// too many Linux stacks to rely on.)

	const VS = `
		attribute vec2 aCenter;   // quad center (strip- or screen-space CSS px)
		attribute vec2 aOffset;   // corner offset from the center (half-size)
		attribute vec4 aColor;
		uniform vec2 uRes;
		uniform float uScroll;
		varying vec4 vColor;
		varying vec2 vLocal;
		varying vec2 vHalf;
		void main() {
			vColor = aColor;
			vLocal = aOffset;
			vHalf = abs(aOffset);
			vec2 pos = vec2(aCenter.x + uScroll, aCenter.y) + aOffset;
			gl_Position = vec4(
				pos.x / uRes.x * 2.0 - 1.0,
				1.0 - pos.y / uRes.y * 2.0,
				0.0, 1.0
			);
		}`;

	const FS = `
		precision mediump float;
		varying vec4 vColor;
		varying vec2 vLocal;
		varying vec2 vHalf;
		void main() {
			// box SDF, ~1px linear edge ramp
			vec2 q = abs(vLocal) - vHalf;
			float a = clamp(0.5 - max(q.x, q.y), 0.0, 1.0);
			gl_FragColor = vec4(vColor.rgb, vColor.a * a);
		}`;

	const NOTE_COLORS: Record<Status, [number, number, number, number]> = {
		pending: [0.4, 0.8, 1.0, 1], // #6cf
		good: [0.2, 0.8, 0.53, 1], // #3c8
		perfect: [0.27, 1.0, 0.47, 1], // #4f7
		off: [1.0, 0.6, 0.0, 1], // #f90
		miss: [0.93, 0.2, 0.2, 1] // #e33
	};
	const COLOR_LANE: [number, number, number, number] = [0.125, 0.125, 0.227, 1]; // #20203a
	const COLOR_BAR: [number, number, number, number] = [0.2, 0.2, 0.302, 1]; // #33334d
	const COLOR_HIT: [number, number, number, number] = [0.941, 0.753, 0.251, 1]; // #f0c040
	const BG: [number, number, number] = [0.0706, 0.0706, 0.118]; // #12121e

	let canvasEl: HTMLCanvasElement | null = $state(null);
	let gl: WebGLRenderingContext | null = null;
	let prog: WebGLProgram | null = null;
	let aCenter = 0;
	let aOffset = 0;
	let aColor = 0;
	let uRes: WebGLUniformLocation | null = null;
	let uScroll: WebGLUniformLocation | null = null;

	let laneBuf: WebGLBuffer | null = null,
		laneCount = 0;
	let hitBuf: WebGLBuffer | null = null,
		hitCount = 0;
	let barBuf: WebGLBuffer | null = null,
		barCount = 0;
	// notes: static positions + a color buffer patched only on status change
	let notePosBuf: WebGLBuffer | null = null;
	let noteColBuf: WebGLBuffer | null = null;
	let noteCol: Float32Array | null = null; // 6 verts * rgba per note
	let noteCount = 0;
	let dynDirty = false;

	let cssW = 0,
		cssH = 0;
	let ro: ResizeObserver | null = null;
	let renderQueued = false;

	function compile(g: WebGLRenderingContext, type: number, src: string) {
		const s = g.createShader(type)!;
		g.shaderSource(s, src);
		g.compileShader(s);
		if (!g.getShaderParameter(s, g.COMPILE_STATUS))
			throw new Error(g.getShaderInfoLog(s) ?? 'shader error');
		return s;
	}

	function initGL(canvas: HTMLCanvasElement) {
		const g = canvas.getContext('webgl', {
			alpha: false,
			antialias: true, // MSAA smooths quad edges; no fragment tricks needed
			depth: false,
			powerPreference: 'high-performance'
		});
		if (!g) {
			status = 'WebGL unavailable — use the DOM lessons page';
			return;
		}
		gl = g;
		prog = g.createProgram()!;
		g.attachShader(prog, compile(g, g.VERTEX_SHADER, VS));
		g.attachShader(prog, compile(g, g.FRAGMENT_SHADER, FS));
		g.linkProgram(prog);
		if (!g.getProgramParameter(prog, g.LINK_STATUS))
			throw new Error(g.getProgramInfoLog(prog) ?? 'link error');
		g.useProgram(prog);
		aCenter = g.getAttribLocation(prog, 'aCenter');
		aOffset = g.getAttribLocation(prog, 'aOffset');
		aColor = g.getAttribLocation(prog, 'aColor');
		uRes = g.getUniformLocation(prog, 'uRes');
		uScroll = g.getUniformLocation(prog, 'uScroll');
		g.enableVertexAttribArray(aCenter);
		g.enableVertexAttribArray(aOffset);
		g.enableVertexAttribArray(aColor);
		// The fragment shader gives moving quad edges fractional alpha. Blend it
		// into the opaque canvas so sub-pixel scrolling does not strobe.
		g.enable(g.BLEND);
		g.blendFunc(g.SRC_ALPHA, g.ONE_MINUS_SRC_ALPHA);
		g.clearColor(BG[0], BG[1], BG[2], 1);
	}

	// One quad = two triangles = 6 vertices, with center/offset positions so
	// the shader can keep edge smoothing stable while scrolling.
	function pushQuad(
		arr: number[],
		x0: number,
		y0: number,
		x1: number,
		y1: number,
		c: [number, number, number, number]
	) {
		const cx = (x0 + x1) / 2;
		const cy = (y0 + y1) / 2;
		arr.push(
			cx, cy, x0 - cx, y0 - cy, ...c,
			cx, cy, x1 - cx, y0 - cy, ...c,
			cx, cy, x1 - cx, y1 - cy, ...c,
			cx, cy, x0 - cx, y0 - cy, ...c,
			cx, cy, x1 - cx, y1 - cy, ...c,
			cx, cy, x0 - cx, y1 - cy, ...c
		);
	}

	function makeBuffer(g: WebGLRenderingContext, data: number[] | Float32Array, usage: number) {
		const b = g.createBuffer()!;
		g.bindBuffer(g.ARRAY_BUFFER, b);
		g.bufferData(g.ARRAY_BUFFER, data instanceof Float32Array ? data : new Float32Array(data), usage);
		return b;
	}

	// (Re)build all geometry. Runs on lesson load and layout changes only.
	function rebuildScene() {
		if (!gl || !parsed || !cssW || !cssH) return;
		const g = gl;
		const trackH = lanesP.length * laneH;
		const hitX = cssW * 0.15;

		const laneArr: number[] = [];
		for (let row = 1; row <= lanesP.length; row++)
			pushQuad(laneArr, 0, row * laneH - 1, cssW, row * laneH, COLOR_LANE);
		g.deleteBuffer(laneBuf);
		laneBuf = makeBuffer(g, laneArr, g.STATIC_DRAW);
		laneCount = laneArr.length / 8;

		const hitArr: number[] = [];
		pushQuad(hitArr, hitX, 0, hitX + 3, trackH, COLOR_HIT);
		g.deleteBuffer(hitBuf);
		hitBuf = makeBuffer(g, hitArr, g.STATIC_DRAW);
		hitCount = hitArr.length / 8;

		const barArr: number[] = [];
		for (const barBeat of bars())
			pushQuad(barArr, barBeat * PX_PER_BEAT, 0, barBeat * PX_PER_BEAT + 1, trackH, COLOR_BAR);
		g.deleteBuffer(barBuf);
		barBuf = makeBuffer(g, barArr, g.STATIC_DRAW);
		barCount = barArr.length / 8;

		// Notes: positions are static; colors live in their own buffer so a
		// status change patches 96 bytes.
		const notes = parsed.notes;
		noteCount = notes.length;
		const pos: number[] = [];
		for (const n of notes) {
			const cx = n.beat * PX_PER_BEAT;
			const cy = laneRow(n.note) * laneH + laneH / 2;
			const x0 = cx - NOTE / 2,
				y0 = cy - NOTE / 2,
				x1 = cx + NOTE / 2,
				y1 = cy + NOTE / 2;
			const centerX = (x0 + x1) / 2;
			const centerY = (y0 + y1) / 2;
			pos.push(
				centerX, centerY, x0 - centerX, y0 - centerY,
				centerX, centerY, x1 - centerX, y0 - centerY,
				centerX, centerY, x1 - centerX, y1 - centerY,
				centerX, centerY, x0 - centerX, y0 - centerY,
				centerX, centerY, x1 - centerX, y1 - centerY,
				centerX, centerY, x0 - centerX, y1 - centerY
			);
		}
		g.deleteBuffer(notePosBuf);
		notePosBuf = makeBuffer(g, pos, g.STATIC_DRAW);

		noteCol = new Float32Array(noteCount * 6 * 4);
		for (let i = 0; i < noteCount; i++) writeNoteColor(i, statuses[i] ?? 'pending');
		g.deleteBuffer(noteColBuf);
		noteColBuf = makeBuffer(g, noteCol, g.DYNAMIC_DRAW);
		dynDirty = false;
	}

	function writeNoteColor(i: number, s: Status) {
		if (!noteCol) return;
		const c = NOTE_COLORS[s];
		for (let v = 0; v < 6; v++) {
			const o = (i * 6 + v) * 4;
			noteCol[o] = c[0];
			noteCol[o + 1] = c[1];
			noteCol[o + 2] = c[2];
			noteCol[o + 3] = c[3];
		}
	}

	function resetNoteColors() {
		if (!noteCol || noteCol.length !== noteCount * 24) return;
		for (let i = 0; i < noteCount; i++) writeNoteColor(i, 'pending');
		dynDirty = true;
		requestRender();
	}

	const F = Float32Array.BYTES_PER_ELEMENT;

	// Interleaved center(2)+offset(2)+color(4) buffer.
	function draw6(buf: WebGLBuffer | null, count: number) {
		if (!gl || !buf || !count) return;
		const g = gl;
		g.bindBuffer(g.ARRAY_BUFFER, buf);
		g.vertexAttribPointer(aCenter, 2, g.FLOAT, false, 8 * F, 0);
		g.vertexAttribPointer(aOffset, 2, g.FLOAT, false, 8 * F, 2 * F);
		g.vertexAttribPointer(aColor, 4, g.FLOAT, false, 8 * F, 4 * F);
		g.drawArrays(g.TRIANGLES, 0, count);
	}

	function drawNotes() {
		if (!gl || !notePosBuf || !noteColBuf || !noteCount) return;
		const g = gl;
		g.bindBuffer(g.ARRAY_BUFFER, notePosBuf);
		g.vertexAttribPointer(aCenter, 2, g.FLOAT, false, 4 * F, 0);
		g.vertexAttribPointer(aOffset, 2, g.FLOAT, false, 4 * F, 2 * F);
		g.bindBuffer(g.ARRAY_BUFFER, noteColBuf);
		g.vertexAttribPointer(aColor, 4, g.FLOAT, false, 4 * F, 0);
		g.drawArrays(g.TRIANGLES, 0, noteCount * 6);
	}

	function render() {
		if (!gl || !parsed) return;
		const g = gl;
		if (dynDirty && noteColBuf && noteCol) {
			g.bindBuffer(g.ARRAY_BUFFER, noteColBuf);
			g.bufferSubData(g.ARRAY_BUFFER, 0, noteCol);
			dynDirty = false;
		}
		g.clear(g.COLOR_BUFFER_BIT);
		g.uniform2f(uRes, cssW, cssH);
		const scroll = cssW * 0.15 - beatPos * PX_PER_BEAT;
		g.uniform1f(uScroll, 0);
		draw6(laneBuf, laneCount);
		g.uniform1f(uScroll, scroll);
		draw6(barBuf, barCount);
		drawNotes();
		g.uniform1f(uScroll, 0);
		draw6(hitBuf, hitCount);
	}

	// One-shot frame while the transport isn't running (tick() renders otherwise).
	function requestRender() {
		if (running || renderQueued || !browser) return;
		renderQueued = true;
		requestAnimationFrame(() => {
			renderQueued = false;
			render();
		});
	}

	function resizeCanvas() {
		const c = canvasEl;
		const host = c?.parentElement;
		if (!c || !host || !gl) return;
		dpr = window.devicePixelRatio || 1;
		// Snap the drawing buffer to whole device pixels AND force the CSS size
		// to match it exactly, so the compositor blits 1:1 instead of resampling.
		const rect = host.getBoundingClientRect();
		const pw = Math.max(1, Math.round(rect.width * dpr));
		const ph = Math.max(1, Math.round(rect.height * dpr));
		c.width = pw;
		c.height = ph;
		c.style.width = `${pw / dpr}px`;
		c.style.height = `${ph / dpr}px`;
		cssW = pw / dpr;
		cssH = ph / dpr;
		gl.viewport(0, 0, pw, ph);
		rebuildScene();
		requestRender();
	}

	$effect(() => {
		const c = canvasEl;
		if (!c) return;
		initGL(c);
		// Observe the host, not the canvas: the canvas gets an explicit size, so
		// it would never report the parent growing.
		ro = new ResizeObserver(resizeCanvas);
		if (c.parentElement) ro.observe(c.parentElement);
		resizeCanvas();
		return () => {
			ro?.disconnect();
			ro = null;
			gl = null;
		};
	});

	// Rebuild geometry when the lesson or the lane height changes (the resize
	// observer catches the resulting size change too; rebuilds are cheap).
	$effect(() => {
		ready;
		laneH;
		if (gl) {
			rebuildScene();
			requestRender();
		}
	});

	// ---- frame clock ------------------------------------------------------
	//
  // rAF timestamps are monotonic and represent the presentation timeline.
  // Use them directly: quantizing deltas to an estimated refresh period makes
  // the highway alternate between short and long movement steps.

	let rawPrev = 0;
	let framePeriod = 1000 / 60; // refined continuously from measured deltas

	function frameClock(ts: number): number {
		if (!rawPrev) {
			rawPrev = ts;
      return ts;
		}
		const dt = ts - rawPrev;
		rawPrev = ts;
    if (dt > 1 && dt < 100) framePeriod += (dt - framePeriod) * 0.05;
		// stats for the ?debug overlay
		statFrames++;
		if (dt > framePeriod * 1.5) statDropped++;
		if (dt > statWorst) statWorst = dt;
    return ts;
	}

	function resetClock() {
		rawPrev = 0;
    lastTs = 0;
	}

	// ?debug — live frame stats to tell dropped frames from timestamp noise.
	// Written imperatively (textContent, 1 Hz): updating reactive state would
	// itself mutate the DOM mid-lesson and cause the very drops it measures.
	let debug = $state(false);
	let hudEl: HTMLDivElement | null = $state(null);
	let statFrames = 0,
		statDropped = 0,
		statWorst = 0,
		statT0 = 0;

	// ---- transport ------------------------------------------------------
	//
	// `running` is the plain (non-reactive) transport flag the hot path checks;
	// `playing`/`paused` ($state) only drive the surrounding UI and change on
	// user action, never per frame.
	let running = false;
	let bpmP = 60; // plain bpm snapshot taken at play()
	let lengthBeatsP = 0;
	let transportStartTime = 0;
	let transportStartPerf = 0;
	let pausedAtAudio = 0;
	let pausedAtPerf = 0;
	const AUDIO_LOOKAHEAD_SECONDS = 0.08;

	function tick(ts: number) {
		if (!running) return;
		const t = frameClock(ts);
		if (!lastTs) lastTs = t;
		lastTs = t;
		// AudioContext.currentTime advances in render quanta, which can be larger
		// than a display frame. Keep audio scheduling on that clock, but interpolate
		// the visual transport from the matching performance-clock origin.
		beatPos = -COUNT_IN + Math.max(0, (ts - transportStartPerf) / 1000) * (bpmP / 60);

		if (debug && hudEl) {
			if (!statT0) statT0 = ts;
			if (ts - statT0 > 1000) {
				const fps = (statFrames * 1000) / (ts - statT0);
				hudEl.textContent = `${fps.toFixed(0)} fps · period ${framePeriod.toFixed(2)} ms · worst ${statWorst.toFixed(1)} ms · dropped ${statDropped}`;
				statFrames = 0;
				statWorst = 0;
				statT0 = ts;
			}
		}

		// Any target that has scrolled past the window unhit is a miss. Walk a
		// single beat-sorted cursor so only newly-passed notes are touched.
		const notes = parsed!.notes;
		while (
			missCursor < missOrder.length &&
			notes[missOrder[missCursor]].beat < beatPos - MATCH_WINDOW_BEATS
		) {
			const idx = missOrder[missCursor++];
			if (!matched[idx]) {
				matched[idx] = true;
				statuses[idx] = 'miss';
				writeNoteColor(idx, 'miss');
				dynDirty = true;
			}
		}

		// Queue backing samples against the audio clock just ahead of playback.
		// Starting AudioBufferSourceNodes in the rAF callback at the exact crossing
		// makes their main-thread work contend with the visual frame.
		const scheduledBeat = beatPos + AUDIO_LOOKAHEAD_SECONDS * (bpmP / 60);
		for (let ti = 0; ti < backingP.length; ti++) {
			const track = backingP[ti];
			let c = backingCursors[ti];
			while (c < track.notes.length && track.notes[c].beat <= scheduledBeat) {
				if (!muteBackingP) {
					const when = transportStartTime + ((track.notes[c].beat + COUNT_IN) * 60) / bpmP;
					backingPlayer?.playAt(track.family, bassIdP(track), track.notes[c].note, when);
				}
				c++;
			}
			backingCursors[ti] = c;
		}

		if (beatPos >= lengthBeatsP) {
			finish();
			return;
		}
		render();
		raf = requestAnimationFrame(tick);
	}

	// Plain snapshots of the reactive knobs the tick loop needs.
	let muteBackingP = false;
	let selectedBassP = 'lately';
	const bassIdP = (t: BackingTrack) => (t.family === 'bass' ? selectedBassP : t.id);
	$effect(() => {
		muteBackingP = muteBacking;
		selectedBassP = selectedBass;
	});

	async function play() {
		if (!parsed || playing) return;
		await audioCtx?.resume();
    await player?.preload(kit, lanesP);
    await Promise.all(
      backingP.map((t) => backingPlayer?.preload(t.family, effId(t), t.notes.map((n) => n.note)))
    );
		resetScoring();
		backingCursors = backingP.map(() => 0);
		report = null;
		beatPos = -COUNT_IN;
		bpmP = bpm;
		lengthBeatsP = parsed.lengthBeats;
		transportStartTime = (audioCtx?.currentTime ?? 0) + AUDIO_LOOKAHEAD_SECONDS;
		transportStartPerf = performance.now() + AUDIO_LOOKAHEAD_SECONDS * 1000;
		playing = true;
		paused = false;
		running = true;
		resetClock();
		statFrames = statDropped = statWorst = statT0 = 0;
		raf = requestAnimationFrame(tick);
	}

	// Freeze the transport mid-lesson; the clock restarts cleanly on resume
	// (the paused stretch never counts as elapsed time).
	function togglePause() {
		if (!playing) return;
		paused = !paused;
		running = !paused;
		resetClock();
		if (paused) {
			pausedAtAudio = audioCtx?.currentTime ?? 0;
			pausedAtPerf = performance.now();
			cancelAnimationFrame(raf);
			requestRender();
		} else {
			transportStartTime += (audioCtx?.currentTime ?? 0) - pausedAtAudio;
			transportStartPerf += performance.now() - pausedAtPerf;
			raf = requestAnimationFrame(tick);
		}
	}

	function stop() {
		running = false;
		playing = false;
		paused = false;
		if (typeof cancelAnimationFrame !== 'undefined') cancelAnimationFrame(raf);
		resetClock();
		requestRender();
	}

	function finish() {
		stop();
		if (parsed) {
			parsed.notes.forEach((_, i) => {
				if (!matched[i]) {
					matched[i] = true;
					statuses[i] = 'miss';
					writeNoteColor(i, 'miss');
					dynDirty = true;
				}
			});
		}
		report = buildReport();
		beatPos = parsed ? parsed.lengthBeats : 0;
		requestRender();
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
		const laneReports: LaneReport[] = lanesP.map((note) => {
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
		debug = new URLSearchParams(location.search).has('debug');
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
	<title>Padrill — Lessons (WebGL)</title>
</svelte:head>

<h1>Lessons <span class="tag">WebGL</span></h1>

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
			<button class="play" onclick={play} disabled={!ready}>Start</button>
		{/if}

		<span class="status">{status}</span>
	</div>

	{#if selected?.description && !playing}
		<p class="description">{selected.description}</p>
	{/if}

	{#if backing.length && !playing}
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

	{#if debug}
		<div class="debug-hud" bind:this={hudEl}></div>
	{/if}

	{#if ready}
		<div class="highway" class:full={playing} style="height: {lanes.length * laneH}px">
			<div class="labels">
				{#each lanes as note (note)}
					<div class="lane-label" style="height: {laneH}px">
						{laneName(note)}
					</div>
				{/each}
			</div>

			<div class="track">
				<canvas bind:this={canvasEl}></canvas>
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
			<button class="play" onclick={play}>Try again</button>
		</div>
	{/if}
{/if}

<style>
	.tag {
		font-size: 0.55em;
		vertical-align: middle;
		padding: 0.25em 0.6em;
		border-radius: 0.3rem;
		background: #2a2a4a;
		color: #9ac;
		font-family: monospace;
	}

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
		/* deliberately static while playing — the DOM must not change mid-lesson */
	}

	.track {
		position: relative;
		flex: 1;
		overflow: hidden;
	}

	.track canvas {
		/* size is set from JS so the buffer maps 1:1 onto device pixels */
		position: absolute;
		top: 0;
		left: 0;
		display: block;
	}

	.debug-hud {
		position: fixed;
		bottom: 1rem;
		left: 1rem;
		z-index: 60;
		padding: 0.35em 0.7em;
		font-family: monospace;
		font-size: 0.8rem;
		color: #9fb;
		background: rgba(10, 10, 20, 0.8);
		border: 1px solid #2a2a3a;
		border-radius: 0.3rem;
		pointer-events: none;
	}

	.hint {
		color: #778;
		font-size: 0.85rem;
	}

	.report {
		margin-top: 1.5rem;
		max-width: 500px;
		padding: 1rem 1.25rem;
		border: 1px solid #2a2a3a;
		border-radius: 0.5rem;
		background: #16162a;
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
