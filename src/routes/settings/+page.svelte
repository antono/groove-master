<script lang="ts">
	const GRID = 4;
	const TOTAL = GRID * GRID;
	const STORAGE_PREFIX = 'padrill:';

	const defaultNotes = [48, 50, 51, 53, 55, 56, 58, 60, 62, 63, 65, 67, 68, 70, 72, 74];

	let midiAccess: MIDIAccess | null = $state(null);
	let inputs: { id: string; name: string; manufacturer: string }[] = $state([]);
	let selectedId: string | null = $state(null);
	let status: string = $state('');
	let denied = $state(false);
	let currentInput: MIDIInput | null = null;

	let capturing = $state(false);
	let captureIndex = $state(0);
	let assignedNotes: (number | null)[] = $state(Array(TOTAL).fill(null));
	let activeNotes: Set<number> = $state(new Set());
	let audioCtx: AudioContext | null = null;

	let savedHint = $state('');
	let hasSaved = $state(false);
	let started = $state(false);

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
		const dev = inputs.find(d => d.id === selectedId);
		return dev ? { id: dev.id, name: dev.name || dev.id } : null;
	}

	function loadSaved(deviceId: string): number[] | null {
		try {
			const raw = localStorage.getItem(STORAGE_PREFIX + deviceId);
			if (!raw) return null;
			const data = JSON.parse(raw);
			if (Array.isArray(data.notes) && data.notes.length === TOTAL) return data.notes;
		} catch { }
		return null;
	}

	function saveConfig() {
		const dev = getCurrentDevice();
		if (!dev) return;
		const all = assignedNotes.every(n => n !== null);
		if (!all) return;
		localStorage.setItem(STORAGE_PREFIX + dev.id, JSON.stringify({ notes: assignedNotes, deviceName: dev.name }));
		hasSaved = true;
		savedHint = '';
	}

	function hasSavedConfig(deviceId: string): boolean {
		return loadSaved(deviceId) !== null;
	}

	function applySaved(deviceId: string) {
		const notes = loadSaved(deviceId);
		if (!notes) return;
		assignedNotes = [...notes];
		hasSaved = true;
		status = 'Loaded saved config';
	}

	async function start() {
		started = true;
		audioCtx = new AudioContext();
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
		currentInput = midiAccess.inputs.get(selectedId);
		if (!currentInput) return;
		currentInput.onmidimessage = handleMIDIMessage;
	}

	function initDevice() {
		if (!selectedId) return;
		const saved = loadSaved(selectedId);
		if (saved) {
			assignedNotes = [...saved];
			hasSaved = true;
			status = 'Loaded saved config';
		}
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
					playNote(defaultNotes[idx]);
				}
			}
		} else if (cmd === 0x80 || (cmd === 0x90 && velocity === 0)) {
			activeNotes = new Set([...activeNotes].filter(n => n !== note));
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

	function playNote(midiNote: number) {
		const ctx = audioCtx!;
		const freq = 440 * Math.pow(2, (midiNote - 69) / 12);
		const osc = ctx.createOscillator();
		const gain = ctx.createGain();
		osc.type = 'triangle';
		osc.frequency.value = freq;
		gain.gain.setValueAtTime(0.25, ctx.currentTime);
		gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.8);
		osc.connect(gain);
		gain.connect(ctx.destination);
		osc.start();
		osc.stop(ctx.currentTime + 0.8);
	}

	const cells = Array.from({ length: TOTAL }, (_, i) => i);

function restoreDevice() {
	const savedId = localStorage.getItem(STORAGE_PREFIX + 'selectedDevice');
	if (!savedId || !inputs.some(d => d.id === savedId)) return;
	selectedId = savedId;
}
</script>

<h1>Padrill</h1>

{#if !started}
	<button class="start-btn" onclick={start}>Start Padrill</button>
{:else if denied}
	<p>{status}</p>
	<button class="start-btn" onclick={start}>Retry</button>
{:else if !midiAccess}
	<p>Connecting...</p>
{:else}
	<div class="toolbar">
		<select bind:value={selectedId} aria-label="Select MIDI input">
			<option value="">-- device --</option>
			{#each inputs as input (input.id)}
				<option value={input.id}>
					{input.name || 'Unnamed'}{input.manufacturer ? ' (' + input.manufacturer + ')' : ''}
				</option>
			{/each}
		</select>

		<button onclick={startCapture} disabled={capturing}>Capture</button>

		{#if selectedId && hasSavedConfig(selectedId) && !hasSaved}
			<button onclick={() => applySaved(selectedId!)}>Load saved</button>
		{/if}

		<span class="status">{status}</span>
	</div>

	{#if savedHint}
		<div class="savebar">
			<span>{savedHint}</span>
			<button onclick={saveConfig}>Save</button>
		</div>
	{/if}

	<div class="grid">
		{#each cells as i}
			{@const note = assignedNotes[i]}
			{@const active = note !== null && activeNotes.has(note)}
			{@const current = capturing && i === captureIndex}
			{@const done = note !== null}
			<div
				class="cell"
				class:active
				class:current
				class:done
			>
				{#if done}
					<span class="label">{i + 1}</span>
					<span class="midi">{noteName(note!)}</span>
				{:else if current}
					<span class="label">{i + 1}</span>
					<span class="hint">press</span>
				{:else}
					<span class="label dim">{i + 1}</span>
				{/if}
			</div>
		{/each}
	</div>
{/if}

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
		min-width: 220px;
	}

	.toolbar button {
		padding: 0.4em 1em;
		font-size: 1rem;
		cursor: pointer;
	}

	.status {
		font-size: 0.9rem;
		color: #666;
	}

	.grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 0.75rem;
		max-width: 520px;
	}

	.cell {
		aspect-ratio: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		border-radius: 0.5rem;
		background: #1a1a2e;
		border: 2px solid #333;
		color: #ccc;
		font-family: monospace;
		transition: all 0.08s ease;
		user-select: none;
	}

	.cell.current {
		border-color: #f0c040;
		box-shadow: 0 0 12px rgba(240, 192, 64, 0.5);
		animation: pulse 0.8s ease-in-out infinite alternate;
	}

	.cell.done {
		border-color: #4a8;
		background: #162b1e;
	}

	.cell.active {
		border-color: #6cf;
		background: #1a3a4e;
		box-shadow: 0 0 16px rgba(100, 200, 255, 0.4);
		transform: scale(0.95);
	}

	.label {
		font-size: 1.2rem;
		font-weight: bold;
	}

	.label.dim {
		opacity: 0.3;
	}

	.midi {
		font-size: 0.75rem;
		color: #8a8;
		margin-top: 0.2rem;
	}

	.hint {
		font-size: 0.65rem;
		color: #f0c040;
		text-transform: uppercase;
		margin-top: 0.2rem;
	}

	.savebar {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin-bottom: 1rem;
		padding: 0.5rem 1rem;
		background: #e0f5e0;
		border: 1px solid #8c8;
		border-radius: 0.4rem;
		font-size: 0.9rem;
		color: #222;
	}

	.savebar button {
		padding: 0.3em 0.8em;
		font-size: 0.85rem;
		cursor: pointer;
	}

	.start-btn {
		padding: 1em 2em;
		font-size: 1.3rem;
		cursor: pointer;
		margin-top: 2rem;
	}

	@keyframes pulse {
		from { box-shadow: 0 0 6px rgba(240, 192, 64, 0.4); }
		to { box-shadow: 0 0 18px rgba(240, 192, 64, 0.7); }
	}
</style>
