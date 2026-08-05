<script lang="ts">
	import { onMount } from 'svelte';
	import { base } from '$app/paths';

	import { STORAGE_PREFIX } from '$lib/config';
	import { DrumPlayer } from '$lib/drums';

	const GRID = 4;
	const TOTAL = GRID * GRID;

	// Grid cell -> GM drum note (the *sound*). Bottom row = groove core,
	// escalating to toms / cymbals / aux toward the top. See scripts/render-drums.py.
	const DEFAULT_SOUND = [39, 56, 54, 55, 49, 51, 53, 52, 45, 47, 50, 44, 36, 38, 42, 46];

	type Kit = { id: number; name: string };
	type Drum = { note: number; name: string };

	let midiAccess: MIDIAccess | null = $state(null);
	let inputs: { id: string; name: string | null; manufacturer: string | null }[] = $state([]);
	let selectedId: string | null = $state('');
	let status: string = $state('');
	let denied = $state(false);
	let currentInput: MIDIInput | null = null;

	let capturing = $state(false);
	let captureIndex = $state(0);
	// Controller pad note bound to each cell (set via Capture).
	let assignedNotes: (number | null)[] = $state(Array(TOTAL).fill(null));
	// GM drum note that each cell plays (set via the per-cell dropdown).
	let soundNotes: number[] = $state([...DEFAULT_SOUND]);
	let activeNotes: Set<number> = $state(new Set());
	let audioCtx: AudioContext | null = null;
	// Reactive so the preload effect below re-runs the moment onMount supplies a
	// player, rather than silently doing nothing on its first pass.
	let player: DrumPlayer | null = $state(null);
	let warming = $state(false);

	// Drum kits + drum catalogue, loaded from the render manifest.
	let kits: Kit[] = $state([]);
	let drums: Drum[] = $state([]);
	let selectedKit = $state(1);
	const drumName = $derived(new Map(drums.map((d) => [d.note, d.name])));

	let savedHint = $state('');
	let hasSaved = $state(false);

	const cells = Array.from({ length: TOTAL }, (_, i) => i);

	// --- sample playback -------------------------------------------------

	async function playCell(idx: number) {
		const note = soundNotes[idx];
		const kit = selectedKit;
		if (note == null || !player) return;
		// Awaiting the shared load joins whatever the preload already has in
		// flight instead of starting a second fetch+decode of the same file —
		// that duplicate was what made a fresh kit's first hit arrive late.
		await player.load(kit, note);
		// Dropped rather than fired if the kit changed while this was loading,
		// so a switch can't be followed by the previous kit's sound.
		if (kit === selectedKit) player.play(kit, note);
	}

	// Warm the 16 assigned drums whenever the kit, the layout, or the player
	// changes, so pads are instant once this settles.
	$effect(() => {
		const kit = selectedKit;
		const notes = new Set(soundNotes);
		if (!player) return;
		warming = true;
		player.preload(kit, notes).then(() => {
			// A later switch owns the flag by then; don't clear someone else's.
			if (kit === selectedKit) warming = false;
		});
	});

	// --- MIDI ------------------------------------------------------------

	function updateInputs() {
		if (!midiAccess) return;
		inputs = [...midiAccess.inputs.values()].map(inputToObj);
	}

	function noteName(m: number) {
		const names = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'];
		return names[m % 12] + Math.floor(m / 12 - 1);
	}

	function inputToObj(input: MIDIInput) {
		return { id: input.id, name: input.name, manufacturer: input.manufacturer };
	}

	function getCurrentDevice(): { id: string; name: string } | null {
		if (!selectedId || !inputs.length) return null;
		const dev = inputs.find((d) => d.id === selectedId);
		return dev ? { id: dev.id, name: dev.name || dev.id } : null;
	}

	function loadSaved(
		deviceId: string
	): { notes: number[]; soundNotes?: number[]; kit?: number } | null {
		try {
			const raw = localStorage.getItem(STORAGE_PREFIX + deviceId);
			if (!raw) return null;
			const data = JSON.parse(raw);
			if (Array.isArray(data.notes) && data.notes.length === TOTAL) return data;
		} catch {}
		return null;
	}

	function saveConfig() {
		const dev = getCurrentDevice();
		if (!dev) return;
		if (!assignedNotes.every((n) => n !== null)) return;
		localStorage.setItem(
			STORAGE_PREFIX + dev.id,
			JSON.stringify({ notes: assignedNotes, soundNotes, kit: selectedKit, deviceName: dev.name })
		);
		hasSaved = true;
		savedHint = '';
	}

	function hasSavedConfig(deviceId: string): boolean {
		return loadSaved(deviceId) !== null;
	}

	function applyConfig(data: { notes: number[]; soundNotes?: number[]; kit?: number }) {
		assignedNotes = [...data.notes];
		if (Array.isArray(data.soundNotes) && data.soundNotes.length === TOTAL)
			soundNotes = [...data.soundNotes];
		if (typeof data.kit === 'number') selectedKit = data.kit;
		hasSaved = true;
		status = 'Loaded saved config';
	}

	function applySaved(deviceId: string) {
		const data = loadSaved(deviceId);
		if (data) applyConfig(data);
	}

	async function loadManifest() {
		try {
			const res = await fetch(`${base}/drums/manifest.json`);
			const data = await res.json();
			kits = data.kits ?? [];
			drums = data.drums ?? [];
		} catch {
			status = 'Could not load drum manifest — run scripts/render-drums.py';
		}
	}

	// The AudioContext starts suspended until a user gesture; resume it on the
	// first interaction so pads are audible without a dedicated "start" button.
	function unlockAudio() {
		audioCtx?.resume();
	}

	onMount(() => {
		audioCtx = new AudioContext();
		player = new DrumPlayer(audioCtx);
		window.addEventListener('pointerdown', unlockAudio, { once: true });
		window.addEventListener('keydown', unlockAudio, { once: true });
		loadManifest();
		connectMidi();
		return () => {
			window.removeEventListener('pointerdown', unlockAudio);
			window.removeEventListener('keydown', unlockAudio);
			if (currentInput) currentInput.onmidimessage = null;
		};
	});

	async function connectMidi() {
		denied = false;
		if (!navigator.requestMIDIAccess) {
			status = 'Web MIDI API not supported in this browser';
			denied = true;
			return;
		}
		try {
			status = 'Connecting...';
			midiAccess = await navigator.requestMIDIAccess({ sysex: false });
			updateInputs();
			midiAccess.onstatechange = () => updateInputs();
			if (inputs.length === 0) {
				status = 'No MIDI devices found';
			} else {
				status = inputs.length + ' device(s) found';
				restoreDevice();
			}
		} catch (err) {
			status = 'MIDI access denied: ' + (err instanceof Error ? err.message : 'Unknown error');
			denied = true;
		}
	}

	function connectInput() {
		if (currentInput) currentInput.onmidimessage = null;
		if (!selectedId || !midiAccess) return;
		currentInput = midiAccess.inputs.get(selectedId) ?? null;
		if (!currentInput) return;
		currentInput.onmidimessage = handleMIDIMessage;
	}

	function initDevice() {
		if (!selectedId) return;
		const data = loadSaved(selectedId);
		if (data) applyConfig(data);
	}

	$effect(() => {
		const id = selectedId;
		if (!id || !midiAccess) return;
		connectInput();
		initDevice();
		localStorage.setItem(STORAGE_PREFIX + 'selectedDevice', id);
	});

	function handleMIDIMessage(event: MIDIMessageEvent) {
		if (!event.data || event.data.length < 3) return;
		const [statusByte, note, velocity] = event.data;
		const cmd = statusByte & 0xf0;

		if (cmd === 0x90 && velocity > 0) {
			if (capturing && captureIndex < TOTAL) {
				assignedNotes[captureIndex] = note;
				assignedNotes = [...assignedNotes];
				captureIndex++;
				if (captureIndex >= TOTAL) {
					capturing = false;
					status = 'All pads assigned!';
					savedHint = 'Save this config for ' + (getCurrentDevice()?.name ?? 'device') + '?';
				} else {
					status = 'Press pad ' + (captureIndex + 1) + ' of ' + TOTAL;
				}
			} else {
				const idx = assignedNotes.indexOf(note);
				if (idx !== -1) {
					activeNotes = new Set([...activeNotes, note]);
					playCell(idx);
				}
			}
		} else if (cmd === 0x80 || (cmd === 0x90 && velocity === 0)) {
			activeNotes = new Set([...activeNotes].filter((n) => n !== note));
		}
	}

	function startCapture() {
		assignedNotes = Array(TOTAL).fill(null);
		captureIndex = 0;
		capturing = true;
		hasSaved = false;
		savedHint = '';
		status = 'Press pad 1 of ' + TOTAL;
	}

	function markDirty() {
		hasSaved = false;
		if (assignedNotes.every((n) => n !== null))
			savedHint = 'Save changes for ' + (getCurrentDevice()?.name ?? 'device') + '?';
	}

	function restoreDevice() {
		const savedId = localStorage.getItem(STORAGE_PREFIX + 'selectedDevice');
		if (!savedId || !inputs.some((d) => d.id === savedId)) return;
		selectedId = savedId;
	}
</script>

<h1>Settings</h1>

{#if denied}
	<div class="warnbar">
		<span>{status}</span>
		<button onclick={connectMidi}>Retry</button>
	</div>
{/if}

<div class="toolbar">
	<select bind:value={selectedId} aria-label="Select MIDI input">
		<option value="">-- device --</option>
		{#each inputs as input (input.id)}
			<option value={input.id}>
				{input.name || 'Unnamed'}{input.manufacturer ? ' (' + input.manufacturer + ')' : ''}
			</option>
		{/each}
	</select>

	<select bind:value={selectedKit} onchange={markDirty} aria-label="Select drum kit">
		{#each kits as kit (kit.id)}
			<option value={kit.id}>{kit.name}</option>
		{/each}
	</select>

	{#if warming}
		<span class="warming">loading samples…</span>
	{/if}

	<button onclick={startCapture} disabled={capturing}>Capture pads</button>

	{#if selectedId && hasSavedConfig(selectedId) && !hasSaved}
		<button onclick={() => applySaved(selectedId!)}>Load saved</button>
	{/if}

	{#if !denied}
		<span class="status">{status}</span>
	{/if}
</div>

{#if savedHint}
	<div class="savebar">
		<span>{savedHint}</span>
		<button onclick={saveConfig}>Save</button>
	</div>
{/if}

<div class="grid">
	{#each cells as i}
		{@const bound = assignedNotes[i]}
		{@const active = bound !== null && activeNotes.has(bound)}
		{@const current = capturing && i === captureIndex}
		<div class="cell" class:active class:current class:done={bound !== null}>
			<div class="cell-head">
				<span class="label">{i + 1}</span>
				{#if bound !== null}
					<span class="midi">{noteName(bound)}</span>
				{:else if current}
					<span class="hint">press</span>
				{:else}
					<span class="midi dim">unbound</span>
				{/if}
			</div>

			<button class="preview" onclick={() => playCell(i)} title="Preview">
				{drumName.get(soundNotes[i]) ?? soundNotes[i]}
			</button>

			<select
				class="drum-select"
				bind:value={soundNotes[i]}
				onchange={markDirty}
				aria-label={'Drum for pad ' + (i + 1)}
			>
				{#each drums as d (d.note)}
					<option value={d.note}>{d.name}</option>
				{/each}
			</select>
		</div>
	{/each}
</div>

<style>
	.toolbar {
		display: flex;
		gap: 0.75rem;
		align-items: center;
		margin-bottom: 1.5rem;
		flex-wrap: wrap;
	}

	.toolbar select {
		padding: 0.4em;
		font-size: 1rem;
		min-width: 180px;
	}

	.toolbar button {
		padding: 0.4em 1em;
		font-size: 1rem;
		cursor: pointer;
	}

	.status {
		font-size: 0.9rem;
		color: var(--text-muted);
	}

	.warming {
		font-size: 0.85rem;
		color: var(--text-muted);
		font-style: italic;
	}

	.grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 0.75rem;
		max-width: 640px;
	}

	.cell {
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
		padding: 0.6rem;
		border-radius: 0.5rem;
		background: #1a1a2e;
		border: 2px solid #333;
		color: #ccc;
		font-family: monospace;
		transition:
			border-color 0.08s ease,
			background 0.08s ease;
		user-select: none;
	}

	.cell-head {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
	}

	.cell.current {
		border-color: #f0c040;
		box-shadow: 0 0 12px rgba(240, 192, 64, 0.5);
	}

	.cell.done {
		border-color: #4a8;
	}

	.cell.active {
		border-color: #6cf;
		background: #1a3a4e;
		box-shadow: 0 0 16px rgba(100, 200, 255, 0.4);
	}

	.label {
		font-size: 1.1rem;
		font-weight: bold;
	}

	.midi {
		font-size: 0.75rem;
		color: #8a8;
	}

	.midi.dim {
		opacity: 0.4;
	}

	.hint {
		font-size: 0.65rem;
		color: #f0c040;
		text-transform: uppercase;
	}

	.preview {
		padding: 0.5rem 0.3rem;
		font-family: inherit;
		font-size: 0.85rem;
		font-weight: bold;
		color: #cde;
		background: #24243e;
		border: 1px solid #3a3a5a;
		border-radius: 0.35rem;
		cursor: pointer;
	}

	.preview:active {
		background: #1a3a4e;
		border-color: #6cf;
	}

	.drum-select {
		width: 100%;
		padding: 0.25em;
		font-size: 0.8rem;
		font-family: inherit;
	}

	.warnbar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.75rem;
		margin-bottom: 1rem;
		padding: 0.5rem 1rem;
		background: rgba(224, 112, 112, 0.08);
		border: 1px solid rgba(224, 112, 112, 0.4);
		border-radius: var(--radius-sm);
		font-size: 0.9rem;
		color: var(--red);
	}

	.savebar {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin-bottom: 1rem;
		padding: 0.5rem 1rem;
		background: rgba(85, 187, 136, 0.1);
		border: 1px solid var(--green-dim);
		border-radius: var(--radius-sm);
		font-size: 0.9rem;
		color: var(--green);
	}

	.savebar button {
		padding: 0.3em 0.8em;
		font-size: 0.85rem;
		cursor: pointer;
	}

</style>
