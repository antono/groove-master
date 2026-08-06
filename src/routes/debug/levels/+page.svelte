<script lang="ts">
	// Level workbench for the rendered drum one-shots.
	//
	// The SoundFont's own levels are uneven — a kit spans roughly -33 to -7.5 dBFS,
	// so some pads are hard to hear next to a kick or snare. This page measures
	// every sample's peak, lets you trim each one by ear, and exports the result as
	// JSON so the gains can be baked into the .oga files by scripts/render-drums.py.
	//
	// Nothing here changes what the app plays; it only writes to localStorage.

	import { onMount } from 'svelte';
	import { base } from '$app/paths';

	import { DRUM_NOTES, drumUrl } from '$lib/drums';

	const STORAGE_KEY = 'groove-master:levels';
	const MIN_DB = -24;
	const MAX_DB = 24;

	type Kit = { id: number; name: string };
	type Drum = { note: number; name: string };
	/** kit id -> note -> gain in dB */
	type Gains = Record<number, Record<number, number>>;

	let audioCtx: AudioContext | null = null;
	let ready = $state(false);
	/** stamped once per page load, so a reload always re-reads from disk */
	let loadedAt = 0;
	/** decoded buffers for the page, keyed kit:note */
	const buffers = new Map<string, AudioBuffer>();

	let kits: Kit[] = $state([]);
	let drums: Drum[] = $state([]);
	let selectedKit = $state(1);
	let status = $state('');

	/** measured peak in dBFS per note, for the selected kit */
	let peaks: Record<number, number> = $state({});
	let measuring = $state(false);

	let gains: Gains = $state({});
	let target = $state(-9);
	let referenceNote = $state(38); // Snare — the loudest thing in the bank
	let lastPlayed: number | null = $state(null);

	const drumName = $derived(new Map(drums.map((d) => [d.note, d.name])));
	const kitGains = $derived(gains[selectedKit] ?? {});
	const adjustedCount = $derived(Object.values(kitGains).filter((g) => g !== 0).length);

	// --- audio ------------------------------------------------------------

	function gainOf(note: number) {
		return gains[selectedKit]?.[note] ?? 0;
	}

	function setGain(note: number, db: number) {
		const clamped = Math.max(MIN_DB, Math.min(MAX_DB, Math.round(db * 10) / 10));
		gains[selectedKit] = { ...(gains[selectedKit] ?? {}), [note]: clamped };
		save();
	}

	/**
	 * Decode a sample straight from disk.
	 *
	 * The cache-busting query is what gets past the service worker: it caches
	 * one-shots cache-first, so without this the page would keep measuring the
	 * levels a sample had before it was re-levelled. See src/service-worker.ts.
	 */
	async function loadFresh(kit: number, note: number): Promise<AudioBuffer | null> {
		const key = kit + ':' + note;
		const cached = buffers.get(key);
		if (cached) return cached;
		if (!audioCtx) return null;
		try {
			const res = await fetch(`${drumUrl(kit, note)}?fresh=${loadedAt}`);
			const buf = await audioCtx.decodeAudioData(await res.arrayBuffer());
			buffers.set(key, buf);
			return buf;
		} catch {
			return null;
		}
	}

	async function play(note: number) {
		if (!audioCtx) return;
		audioCtx.resume();
		const buf = await loadFresh(selectedKit, note);
		if (!buf) return;
		const src = audioCtx.createBufferSource();
		src.buffer = buf;
		const gain = audioCtx.createGain();
		// dB -> linear amplitude
		gain.gain.value = 10 ** (gainOf(note) / 20);
		src.connect(gain).connect(audioCtx.destination);
		src.start();
		lastPlayed = note;
	}

	/** Peak of a decoded buffer, in dBFS (-Infinity for silence). */
	function peakDbfs(buf: AudioBuffer) {
		let peak = 0;
		for (let ch = 0; ch < buf.numberOfChannels; ch++) {
			const data = buf.getChannelData(ch);
			for (let i = 0; i < data.length; i++) {
				const v = Math.abs(data[i]);
				if (v > peak) peak = v;
			}
		}
		return peak === 0 ? -Infinity : 20 * Math.log10(peak);
	}

	/** Decode every drum in a kit and record its peak. */
	async function measure(kit: number) {
		measuring = true;
		status = 'measuring…';
		const next: Record<number, number> = {};
		for (const note of DRUM_NOTES) {
			const buf = await loadFresh(kit, note);
			if (buf) next[note] = Math.round(peakDbfs(buf) * 10) / 10;
		}
		// A kit switch mid-measure owns the result by then.
		if (kit === selectedKit) {
			peaks = next;
			status = '';
		}
		measuring = false;
	}

	$effect(() => {
		const kit = selectedKit;
		if (ready) measure(kit);
	});

	// --- suggestions ------------------------------------------------------

	/** Gains that would bring every sample in this kit to `target` dBFS. */
	function suggest() {
		const next: Record<number, number> = {};
		for (const note of DRUM_NOTES) {
			const peak = peaks[note];
			if (peak === undefined || !Number.isFinite(peak)) continue;
			next[note] = Math.max(MIN_DB, Math.min(MAX_DB, Math.round((target - peak) * 10) / 10));
		}
		gains[selectedKit] = next;
		save();
	}

	function resetKit() {
		gains[selectedKit] = {};
		save();
	}

	function copyToAllKits() {
		const src = gains[selectedKit] ?? {};
		for (const kit of kits) gains[kit.id] = { ...src };
		save();
		status = `copied kit ${selectedKit}'s levels to all ${kits.length} kits`;
	}

	// --- persistence + JSON ----------------------------------------------

	function save() {
		try {
			localStorage.setItem(STORAGE_KEY, JSON.stringify({ gainsDb: prune(gains), target }));
		} catch {
			/* storage blocked — the JSON box is still the way out */
		}
	}

	/** Drop zero and empty entries so the export only carries real decisions. */
	function prune(all: Gains) {
		const out: Gains = {};
		for (const [kit, notes] of Object.entries(all)) {
			const kept = Object.fromEntries(Object.entries(notes).filter(([, db]) => db !== 0));
			if (Object.keys(kept).length) out[Number(kit)] = kept as Record<number, number>;
		}
		return out;
	}

	// `kit` records which kit was being auditioned, and `labels` names the trimmed
	// drums, so an exported doc reads on its own without the manifest next to it.
	// Import ignores both — `gainsDb` is the payload.
	const json = $derived(
		JSON.stringify(
			{
				kit: selectedKit,
				kitName: kits.find((k) => k.id === selectedKit)?.name ?? `kit ${selectedKit}`,
				gainsDb: prune(gains),
				labels: Object.fromEntries(
					[...new Set(Object.values(prune(gains)).flatMap((n) => Object.keys(n)))]
						.map(Number)
						.sort((a, b) => a - b)
						.map((n) => [n, drumName.get(n) ?? String(n)])
				)
			},
			null,
			2
		)
	);

	let importText = $state('');
	let importError = $state('');

	function importJson() {
		importError = '';
		try {
			const parsed = JSON.parse(importText);
			const src = parsed.gainsDb ?? parsed;
			const next: Gains = {};
			for (const [kit, notes] of Object.entries(src as Gains)) {
				next[Number(kit)] = Object.fromEntries(
					Object.entries(notes).map(([n, db]) => [Number(n), Number(db)])
				) as Record<number, number>;
			}
			gains = next;
			if (typeof parsed.target === 'number') target = parsed.target;
			save();
			status = 'loaded levels from JSON';
			importText = '';
		} catch (err) {
			importError = err instanceof Error ? err.message : 'could not parse JSON';
		}
	}

	async function copyJson() {
		try {
			await navigator.clipboard.writeText(json);
			status = 'JSON copied to clipboard';
		} catch {
			status = 'clipboard blocked — select the JSON below and copy manually';
		}
	}

	// --- setup ------------------------------------------------------------

	async function loadManifest() {
		try {
			const res = await fetch(`${base}/drums/manifest.json`);
			const data = await res.json();
			kits = data.kits ?? [];
			drums = data.drums ?? [];
		} catch {
			status = 'could not load the drum manifest — run scripts/render-drums.py';
		}
	}

	function restore() {
		try {
			const raw = localStorage.getItem(STORAGE_KEY);
			if (!raw) return;
			const data = JSON.parse(raw);
			if (data.gainsDb) gains = data.gainsDb;
			if (typeof data.target === 'number') target = data.target;
		} catch {
			/* nothing saved, or unreadable */
		}
	}

	onMount(() => {
		audioCtx = new AudioContext();
		loadedAt = Date.now();
		restore();
		loadManifest();
		ready = true;
	});

	/** 0..1 position of a dBFS reading on a -40..0 scale, for the level bar. */
	function barWidth(db: number | undefined) {
		if (db === undefined || !Number.isFinite(db)) return 0;
		return Math.max(0, Math.min(1, (db + 40) / 40)) * 100;
	}

	function fmt(db: number | undefined) {
		if (db === undefined) return '—';
		if (!Number.isFinite(db)) return 'SILENT';
		return db.toFixed(1);
	}
</script>

<svelte:head>
	<title>Groove Academy — sample levels</title>
	<meta name="robots" content="noindex" />
</svelte:head>

<h1>Sample levels</h1>

<p class="lede">
	Peaks are measured from the rendered <code>.oga</code> files. Drag a slider to trim a drum by ear,
	then hand the JSON back so the gains can be baked into the samples. Nothing here changes what the
	app plays.
</p>

<div class="toolbar">
	<select bind:value={selectedKit} aria-label="Select drum kit">
		{#each kits as kit (kit.id)}
			<option value={kit.id}>{kit.name}</option>
		{/each}
	</select>

	<button onclick={() => play(referenceNote)} disabled={measuring}>
		Reference: {drumName.get(referenceNote) ?? referenceNote}
	</button>

	<select bind:value={referenceNote} aria-label="Reference drum">
		{#each drums as d (d.note)}
			<option value={d.note}>{d.name}</option>
		{/each}
	</select>

	<span class="sep"></span>

	<label class="target">
		target
		<input type="number" bind:value={target} min="-30" max="0" step="0.5" />
		dBFS
	</label>
	<button onclick={suggest} disabled={measuring}>Suggest</button>
	<button onclick={copyToAllKits} disabled={measuring}>Copy to all kits</button>
	<button onclick={resetKit} disabled={measuring}>Reset kit</button>

	<span class="status">
		{#if measuring}measuring…{:else}{adjustedCount} of {DRUM_NOTES.length} adjusted{/if}
		{#if status}— {status}{/if}
	</span>
</div>

<table>
	<thead>
		<tr>
			<th class="c-note">note</th>
			<th class="c-name">drum</th>
			<th class="c-peak">peak dBFS</th>
			<th class="c-bar"></th>
			<th class="c-gain">gain dB</th>
			<th class="c-slider">trim</th>
			<th class="c-result">result</th>
			<th class="c-play"></th>
		</tr>
	</thead>
	<tbody>
		{#each drums as d (d.note)}
			{@const peak = peaks[d.note]}
			{@const g = gainOf(d.note)}
			{@const quiet = Number.isFinite(peak) && peak < -20}
			<tr class:adjusted={g !== 0} class:quiet class:playing={lastPlayed === d.note}>
				<td class="c-note">{d.note}</td>
				<td class="c-name">{d.name}</td>
				<td class="c-peak" class:silent={peak !== undefined && !Number.isFinite(peak)}>
					{fmt(peak)}
				</td>
				<td class="c-bar">
					<span class="bar" style="width: {barWidth(peak)}%"></span>
				</td>
				<td class="c-gain">{g > 0 ? '+' : ''}{g.toFixed(1)}</td>
				<td class="c-slider">
					<input
						type="range"
						min={MIN_DB}
						max={MAX_DB}
						step="0.5"
						value={g}
						oninput={(e) => setGain(d.note, Number(e.currentTarget.value))}
						aria-label={'Trim for ' + d.name}
					/>
				</td>
				<td class="c-result">{fmt(peak === undefined ? undefined : peak + g)}</td>
				<td class="c-play">
					<button onclick={() => play(d.note)} title="Play with this trim">▶</button>
				</td>
			</tr>
		{/each}
	</tbody>
</table>

<section class="io">
	<div class="io-col">
		<div class="io-head">
			<h2>Export</h2>
			<button onclick={copyJson}>Copy</button>
		</div>
		<textarea readonly rows="12" value={json}></textarea>
		<p class="hint">
			Only non-zero gains are included, keyed by kit then GM note. Hand this back and the gains get
			baked into <code>static/drums/</code>.
		</p>
	</div>

	<div class="io-col">
		<div class="io-head">
			<h2>Import</h2>
			<button onclick={importJson} disabled={!importText.trim()}>Load</button>
		</div>
		<textarea
			rows="12"
			bind:value={importText}
			placeholder={'{\n  "gainsDb": {\n    "1": { "47": 3.5 }\n  }\n}'}
		></textarea>
		{#if importError}<p class="err">{importError}</p>{/if}
	</div>
</section>

<style>
	.lede {
		max-width: 62ch;
		color: var(--text-muted);
		font-size: 0.95rem;
	}

	.toolbar {
		display: flex;
		gap: 0.6rem;
		align-items: center;
		flex-wrap: wrap;
		margin: 1.25rem 0;
	}

	.toolbar select,
	.toolbar button,
	.target input {
		padding: 0.35em 0.6em;
		font-size: 0.9rem;
	}

	.toolbar button {
		cursor: pointer;
	}

	.target {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		font-size: 0.85rem;
		color: var(--text-muted);
	}

	.target input {
		width: 5.5em;
	}

	.sep {
		width: 1px;
		height: 1.6em;
		background: #3a3a5a;
	}

	.status {
		font-size: 0.85rem;
		color: var(--text-muted);
	}

	table {
		width: 100%;
		border-collapse: collapse;
		font-family: monospace;
		font-size: 0.85rem;
	}

	th {
		text-align: left;
		font-weight: normal;
		color: var(--text-muted);
		border-bottom: 1px solid #3a3a5a;
		padding: 0.4rem 0.5rem;
	}

	td {
		padding: 0.25rem 0.5rem;
		border-bottom: 1px solid #24243e;
	}

	tr.quiet .c-peak {
		color: #f0c040;
	}

	tr.adjusted {
		background: rgba(100, 200, 255, 0.06);
	}

	tr.playing {
		background: #1a3a4e;
	}

	.c-note,
	.c-peak,
	.c-gain,
	.c-result {
		text-align: right;
		white-space: nowrap;
	}

	.c-name {
		min-width: 9em;
	}

	.c-peak.silent {
		color: var(--red);
		font-weight: bold;
	}

	.c-bar {
		width: 18%;
		min-width: 60px;
	}

	.bar {
		display: block;
		height: 0.55em;
		border-radius: 2px;
		background: linear-gradient(90deg, #4a8, #6cf);
	}

	.c-slider {
		width: 32%;
	}

	.c-slider input {
		width: 100%;
	}

	.c-play button {
		cursor: pointer;
		padding: 0.1em 0.5em;
	}

	.io {
		display: flex;
		gap: 1.5rem;
		flex-wrap: wrap;
		margin: 2rem 0 3rem;
	}

	.io-col {
		flex: 1 1 22rem;
		min-width: 0;
	}

	.io-head {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 0.75rem;
	}

	.io-head h2 {
		font-size: 1rem;
		margin: 0 0 0.4rem;
	}

	.io-head button {
		cursor: pointer;
		padding: 0.25em 0.7em;
		font-size: 0.85rem;
	}

	textarea {
		width: 100%;
		font-family: monospace;
		font-size: 0.8rem;
		padding: 0.5rem;
		background: #1a1a2e;
		color: #cde;
		border: 1px solid #3a3a5a;
		border-radius: 0.35rem;
		resize: vertical;
	}

	.hint {
		font-size: 0.8rem;
		color: var(--text-muted);
	}

	.err {
		font-size: 0.8rem;
		color: var(--red);
	}
</style>
