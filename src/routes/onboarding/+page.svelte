<script lang="ts">
	import { onMount } from 'svelte';
	import { base } from '$app/paths';

	import { MidiHub, type MidiInputInfo } from '$lib/midi-hub.svelte';
	import { matchPreset, MAX_COLS, MAX_ROWS, type Preset } from '$lib/presets';
	import { playScaleTone, unlockAudio } from '$lib/scale';
	import { onboardingFinished, onboardingStarted, onboardingStep } from '$lib/analytics';
	import PadGrid from '$lib/pad-grid.svelte';
	import PageMeta from '$lib/page-meta.svelte';
	import {
		controlLabel,
		parseControl,
		sameControl,
		type MidiControl
	} from '$lib/transport-control';

	// Keep saved config compatible with the Lessons and Settings pages:
	// localStorage["groove-master:<deviceId>"] = { notes, soundNotes, kit, deviceName,
	// transport }.
	const STORAGE_PREFIX = 'groove-master:';
	// Grid cell -> GM drum note, mirrored from the Settings page. Bottom row =
	// groove core; smaller grids take the *tail* so kick/snare/hats stay on the
	// bottom row.
	const DEFAULT_SOUND = [39, 56, 54, 55, 49, 51, 53, 52, 45, 47, 50, 44, 36, 38, 42, 46];

	type Step = 'connect' | 'device' | 'grid' | 'map' | 'transport' | 'done';
	const STEPS: { id: Step; label: string }[] = [
		{ id: 'connect', label: 'Connect' },
		{ id: 'device', label: 'Device' },
		{ id: 'grid', label: 'Grid' },
		{ id: 'map', label: 'Map pads' },
		{ id: 'transport', label: 'Transport' }
	];

	const midi = new MidiHub();

	let step = $state<Step>('connect');
	let deviceId = $state<string | null>(null);
	let deviceName = $state('');
	let detected = $state<Preset | null>(null);
	let cols = $state(4);
	let rows = $state(4);
	let captured = $state<(number | null)[]>([]);
	let captureIndex = $state(0);
	let hitIndex = $state<number | null>(null);
	let soundOn = $state(true);
	let saved = $state(false);

	// Transport step: Play / Stop buttons, if the controller has any. Both are
	// optional — plenty of pad units are just pads.
	type Slot = 'start' | 'stop';
	const SLOTS: { id: Slot; label: string; hint: string }[] = [
		{ id: 'start', label: 'Play / Start', hint: 'Starts a lesson and resumes after a pause' },
		{ id: 'stop', label: 'Stop / Pause', hint: 'Pauses the run; press again to stop it' }
	];
	let startCtrl = $state<MidiControl | null>(null);
	let stopCtrl = $state<MidiControl | null>(null);
	let arming = $state<Slot | null>(null);
	let ctrlHint = $state('');

	const total = $derived(cols * rows);
	const pct = $derived(total ? Math.round((Math.min(captureIndex, total) / total) * 100) : 0);
	const stepIndex = $derived(
		STEPS.findIndex((s) => s.id === (step === 'done' ? 'transport' : step))
	);

	// note-capture debounce (pads can bounce a note-on twice)
	let lastNote = -1;
	let lastAt = 0;
	let hitTimer: ReturnType<typeof setTimeout>;

	// Which step the student is on is the one thing worth measuring here — the wizard
	// is where a new drummer either gets their pads working or gives up, and the step
	// they were last on says which. Reported off `step` rather than from each
	// transition so every route into a screen counts, Back included; only the finish
	// is once-per-visit, so a student who steps back out of "done" and returns is not
	// counted as having set up twice.
	let reportedStep: Step | null = null;
	let reportedFinish = false;

	$effect(() => {
		const current = step;
		if (current === reportedStep) return;
		reportedStep = current;
		onboardingStep(current);
		if (current === 'done' && !reportedFinish) {
			reportedFinish = true;
			onboardingFinished();
		}
	});

	onMount(() => {
		onboardingStarted();
		const off = midi.onNote(handleNote);
		const offRaw = midi.onMessage(handleMessage);
		return () => {
			off();
			offRaw();
			midi.stop();
			clearTimeout(hitTimer);
		};
	});

	function handleNote(note: number) {
		if (step !== 'map' || captureIndex >= total) return;
		const now = performance.now();
		if (note === lastNote && now - lastAt < 160) return; // ignore bounce
		lastNote = note;
		lastAt = now;

		captured[captureIndex] = note;
		captured = [...captured];
		flashHit(captureIndex);
		if (soundOn) playScaleTone(captureIndex, total);

		captureIndex++;
		if (captureIndex >= total) finish();
	}

	// Transport capture listens to the raw stream, not just note-ons: a Play
	// button may send a CC or a single-byte MIDI Start instead of a note.
	function handleMessage(data: Uint8Array) {
		if (step !== 'transport' || !arming) return;
		const hit = parseControl(data);
		if (!hit || !hit.pressed) return; // releases and clock are not presses
		const { control } = hit;

		// A pad we just mapped is not a transport button — say so instead of
		// silently binding the kick to Play.
		if (control.kind === 'note' && captured.includes(control.data1)) {
			ctrlHint = `That's one of your pads (note ${control.data1}). Press a Play or Stop button.`;
			return;
		}
		const other = arming === 'start' ? stopCtrl : startCtrl;
		if (sameControl(control, other)) {
			ctrlHint = 'That button is already taken by the other slot.';
			return;
		}

		ctrlHint = '';
		if (arming === 'start') {
			startCtrl = control;
			arming = 'stop'; // roll straight on to the Stop button
		} else {
			stopCtrl = control;
			arming = null;
			save();
		}
	}

	const slotControl = (slot: Slot) => (slot === 'start' ? startCtrl : stopCtrl);

	function armSlot(slot: Slot) {
		ctrlHint = '';
		arming = slot;
	}

	function clearSlot(slot: Slot) {
		ctrlHint = '';
		if (slot === 'start') startCtrl = null;
		else stopCtrl = null;
		if (arming === slot) arming = null;
		save();
	}

	function flashHit(i: number) {
		hitIndex = i;
		clearTimeout(hitTimer);
		hitTimer = setTimeout(() => (hitIndex = null), 140);
	}

	// --- step transitions --------------------------------------------------

	async function connect() {
		await unlockAudio(); // this click is our audio-unlock gesture
		const ok = await midi.connect();
		if (ok) step = 'device';
	}

	async function pair() {
		await unlockAudio();
		await midi.pairBluetooth();
		if (midi.access) step = 'device';
	}

	function selectDevice(info: MidiInputInfo) {
		deviceId = info.id;
		deviceName = info.name;
		midi.listen(info.id);
		detected = matchPreset(info.name);
		cols = detected?.cols ?? 4;
		rows = detected?.rows ?? 4;
		step = 'grid';
	}

	function setCols(n: number) {
		cols = Math.max(1, Math.min(MAX_COLS, n));
	}
	function setRows(n: number) {
		rows = Math.max(1, Math.min(MAX_ROWS, n));
	}

	function startCapture() {
		captured = Array(total).fill(null);
		captureIndex = 0;
		lastNote = -1;
		saved = false;
		step = 'map';
	}

	function undo() {
		if (captureIndex === 0) return;
		captureIndex--;
		captured[captureIndex] = null;
		captured = [...captured];
	}

	// Pads done — on to the transport buttons, already armed for the Play button
	// so the student can just press it.
	function finish() {
		save();
		ctrlHint = '';
		step = 'transport';
		// Guide the first pass; a re-map keeps buttons already captured, so don't
		// arm over them.
		arming = startCtrl || stopCtrl ? null : 'start';
	}

	function finishTransport() {
		arming = null;
		save();
		step = 'done';
	}

	function save() {
		if (!deviceId) return;
		const notes = captured.map((n) => n ?? 0);
		const soundNotes = DEFAULT_SOUND.slice(DEFAULT_SOUND.length - total);
		try {
			localStorage.setItem(
				STORAGE_PREFIX + deviceId,
				JSON.stringify({
					notes,
					soundNotes,
					kit: 1,
					deviceName,
					cols,
					rows,
					transport: { start: startCtrl, stop: stopCtrl }
				})
			);
			localStorage.setItem(STORAGE_PREFIX + 'selectedDevice', deviceId);
			saved = true;
		} catch {
			/* storage blocked (private mode) — config just isn't persisted */
		}
	}

	function previewPad(i: number) {
		unlockAudio();
		playScaleTone(i, total);
	}
</script>

<PageMeta
	title="Groove Academy — Set up your pads"
	description="Point the browser at your MIDI kit, tap each pad once, and Groove Academy learns the layout. No kit? The on-screen pads work too."
/>

<div class="wizard">
	<!-- step rail -->
	<ol class="rail" aria-label="Setup progress">
		{#each STEPS as s, i (s.id)}
			<li class="rail-step" class:active={i === stepIndex} class:done={i < stepIndex}>
				<span class="rail-dot">{i < stepIndex ? '✓' : i + 1}</span>
				<span class="rail-label">{s.label}</span>
				{#if i < STEPS.length - 1}<span class="rail-line"></span>{/if}
			</li>
		{/each}
	</ol>

	<section class="card">
		{#if step === 'connect'}
			<header class="card-head">
				<h2>Connect your pads</h2>
				<p class="sub">Plug in a USB-MIDI controller, or pair a Bluetooth-MIDI pad. No account needed.</p>
			</header>
			{#if midi.error}
				<p class="alert">{midi.error}</p>
			{/if}
			<div class="connect-actions">
				<button class="primary big" onclick={connect} disabled={!midi.supported}>
					Connect USB / MIDI
				</button>
				{#if midi.bluetoothSupported}
					<button class="big" onclick={pair}>Pair Bluetooth pad</button>
				{/if}
			</div>
			<p class="fine">
				{#if !midi.supported}
					This browser has no Web MIDI support. Use Chrome, Edge, or Opera on desktop or Android.
				{:else}
					Your browser will ask permission to use MIDI devices.
				{/if}
			</p>
		{:else if step === 'device'}
			<header class="card-head">
				<h2>Choose your device</h2>
				<p class="sub">
					{midi.inputs.length
						? 'Pick the controller you want to set up.'
						: 'No MIDI inputs found yet — connect a pad and rescan.'}
				</p>
			</header>
			{#if midi.error}
				<p class="alert">{midi.error}</p>
			{/if}
			{#if midi.inputs.length}
				<div class="devices">
					{#each midi.inputs as input (input.id)}
						{@const preset = matchPreset(input.name)}
						<button type="button" class="device" onclick={() => selectDevice(input)}>
							<span class="device-text">
								<span class="device-name">{input.name}</span>
								{#if input.manufacturer}
									<span class="device-mfr">{input.manufacturer}</span>
								{/if}
							</span>
							{#if preset}
								<span class="tag">{preset.cols}×{preset.rows}</span>
							{/if}
							<span class="device-go" aria-hidden="true">→</span>
						</button>
					{/each}
				</div>
			{:else}
				<div class="empty">
					<span class="empty-icon" aria-hidden="true">🎛</span>
					<span>Waiting for a controller…</span>
				</div>
			{/if}
			<footer class="card-foot">
				<button class="ghost" onclick={() => (step = 'connect')}>← Back</button>
				<span class="btn-group">
					<button onclick={() => midi.refresh()}>Rescan</button>
					{#if midi.bluetoothSupported}
						<button onclick={pair}>Pair Bluetooth</button>
					{/if}
				</span>
			</footer>
		{:else if step === 'grid'}
			<header class="card-head">
				<h2>Pad layout</h2>
				<p class="sub">
					{#if detected}
						Detected <strong>{detected.label}</strong> — adjust if it looks wrong.
					{:else}
						No preset matched for <strong>{deviceName}</strong>. Set your grid size.
					{/if}
				</p>
			</header>
			<div class="steppers">
				<div class="stepper">
					<span class="stepper-label">Columns</span>
					<span class="stepper-controls">
						<button class="square" onclick={() => setCols(cols - 1)} disabled={cols <= 1}>−</button>
						<span class="stepper-value">{cols}</span>
						<button class="square" onclick={() => setCols(cols + 1)} disabled={cols >= MAX_COLS}>+</button>
					</span>
				</div>
				<span class="steppers-x" aria-hidden="true">×</span>
				<div class="stepper">
					<span class="stepper-label">Rows</span>
					<span class="stepper-controls">
						<button class="square" onclick={() => setRows(rows - 1)} disabled={rows <= 1}>−</button>
						<span class="stepper-value">{rows}</span>
						<button class="square" onclick={() => setRows(rows + 1)} disabled={rows >= MAX_ROWS}>+</button>
					</span>
				</div>
			</div>
			<div class="well compact">
				<PadGrid {cols} {rows} captured={Array(total).fill(null)} />
				<p class="fine center">{cols} × {rows} = {total} pad{total === 1 ? '' : 's'}</p>
			</div>
			<footer class="card-foot">
				<button class="ghost" onclick={() => (step = 'device')}>← Back</button>
				<button class="primary" onclick={startCapture}>Map pads →</button>
			</footer>
		{:else if step === 'map'}
			<header class="card-head">
				<h2>Press each pad</h2>
				<p class="sub">
					Left to right, top to bottom — hit the glowing pad.
					<strong class="count">{captureIndex < total ? `${captureIndex + 1} / ${total}` : 'all set!'}</strong>
				</p>
			</header>
			<div class="progress" role="progressbar" aria-valuenow={pct} aria-label="Pads mapped">
				<div class="progress-bar" style="width: {pct}%"></div>
			</div>
			<div class="well">
				<PadGrid {cols} {rows} {captured} {captureIndex} {hitIndex} onpreview={previewPad} />
			</div>
			<label class="sound-toggle">
				<input type="checkbox" bind:checked={soundOn} />
				Play an A-minor tone on each press
			</label>
			<footer class="card-foot">
				<button class="ghost" onclick={() => (step = 'grid')}>← Back</button>
				<span class="btn-group">
					<button onclick={undo} disabled={captureIndex === 0}>Undo</button>
					<button onclick={startCapture}>Restart</button>
				</span>
			</footer>
		{:else if step === 'transport'}
			<header class="card-head">
				<h2>Transport buttons</h2>
				<p class="sub">
					Has your controller got Play and Stop buttons? Press them now and they'll start and
					pause lessons. If it hasn't, skip — the on-screen buttons work either way.
				</p>
			</header>
			<div class="slots">
				{#each SLOTS as slot (slot.id)}
					{@const ctrl = slotControl(slot.id)}
					<button
						type="button"
						class="slot"
						class:armed={arming === slot.id}
						class:set={!!ctrl}
						onclick={() => armSlot(slot.id)}
					>
						<span class="slot-text">
							<span class="slot-label">{slot.label}</span>
							<span class="slot-hint">{slot.hint}</span>
						</span>
						<span class="slot-value">
							{#if arming === slot.id}
								<span class="listening">Press it…</span>
							{:else if ctrl}
								<span class="tag">{controlLabel(ctrl)}</span>
							{:else}
								<span class="slot-empty">Not set</span>
							{/if}
						</span>
					</button>
				{/each}
			</div>
			{#if ctrlHint}
				<p class="fine center">{ctrlHint}</p>
			{:else}
				<p class="fine center">
					{arming === 'start'
						? 'Waiting for your Play button…'
						: arming === 'stop'
							? 'Now press Stop — or skip to finish with just Play.'
							: 'Tap a row to re-record that button.'}
				</p>
			{/if}
			<footer class="card-foot">
				<button class="ghost" onclick={() => (step = 'map')}>← Back</button>
				<span class="btn-group">
					{#if startCtrl || stopCtrl}
						<button
							onclick={() => {
								clearSlot('start');
								clearSlot('stop');
								armSlot('start');
							}}>Clear</button
						>
					{/if}
					<button class="primary" onclick={finishTransport}>
						{startCtrl || stopCtrl ? 'Done →' : 'Skip →'}
					</button>
				</span>
			</footer>
		{:else if step === 'done'}
			<header class="card-head done-head">
				<span class="check" aria-hidden="true">✓</span>
				<h2>You're set up</h2>
				<p class="sub">
					{deviceName} · {cols}×{rows} · {total} pads mapped{saved ? ' and saved' : ''}.
				</p>
			</header>
			<div class="well">
				<PadGrid {cols} {rows} {captured} onpreview={previewPad} />
				<p class="fine center">Tap a pad to hear its tone.</p>
			</div>
			{#if startCtrl || stopCtrl}
				<p class="fine center">
					Transport:
					{#if startCtrl}<span class="tag">{controlLabel(startCtrl)}</span> starts{/if}{#if startCtrl && stopCtrl},
					{/if}{#if stopCtrl}<span class="tag">{controlLabel(stopCtrl)}</span> pauses{/if}.
				</p>
			{/if}
			<footer class="card-foot">
				<span class="btn-group">
					<button class="ghost" onclick={() => (step = 'device')}>Switch device</button>
					<button onclick={startCapture}>Re-map</button>
					<button
						onclick={() => {
							step = 'transport';
							armSlot('start');
						}}>Buttons</button
					>
				</span>
				<a class="cta" href="{base}/lessons">Start practicing →</a>
			</footer>
		{/if}
	</section>
</div>

<style>
	.wizard {
		max-width: 560px;
		margin: 1.5rem auto 0;
	}

	/* --- step rail --- */

	.rail {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		list-style: none;
		margin: 0 0 1.5rem;
		padding: 0 0.25rem;
	}

	.rail-step {
		display: flex;
		flex: 1;
		align-items: center;
		gap: 0.5rem;
		min-width: 0;
	}

	.rail-step:last-child {
		flex: 0 0 auto;
	}

	.rail-dot {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 1.6rem;
		height: 1.6rem;
		flex-shrink: 0;
		border-radius: 50%;
		border: 2px solid var(--border-strong);
		color: var(--text-faint);
		font-family: var(--font-mono);
		font-size: 0.75rem;
		font-weight: 700;
		transition:
			border-color 200ms ease,
			background 200ms ease,
			color 200ms ease;
	}

	.rail-step.active .rail-dot {
		border-color: var(--gold);
		color: var(--gold);
		box-shadow: 0 0 10px var(--gold-dim);
	}

	.rail-step.done .rail-dot {
		border-color: var(--green);
		background: var(--green);
		color: #0e2018;
	}

	.rail-label {
		font-size: 0.85rem;
		color: var(--text-faint);
		white-space: nowrap;
	}

	.rail-step.active .rail-label {
		color: var(--text);
		font-weight: 600;
	}

	.rail-step.done .rail-label {
		color: var(--text-muted);
	}

	.rail-line {
		flex: 1;
		height: 1px;
		min-width: 0.75rem;
		background: var(--border);
	}

	@media (max-width: 480px) {
		.rail-label {
			display: none;
		}
	}

	/* --- card --- */

	.card {
		padding: 1.75rem;
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: calc(var(--radius) + 4px);
		box-shadow: 0 16px 40px rgba(0, 0, 0, 0.35);
	}

	@media (max-width: 480px) {
		.card {
			padding: 1.25rem;
		}
	}

	.card-head {
		margin-bottom: 1.5rem;
	}

	.sub {
		margin: 0.25rem 0 0;
		color: var(--text-muted);
		font-size: 0.95rem;
	}

	.count {
		color: var(--gold);
		font-family: var(--font-mono);
	}

	.card-foot {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.75rem;
		flex-wrap: wrap;
		margin-top: 1.5rem;
		padding-top: 1.25rem;
		border-top: 1px solid var(--border);
	}

	.btn-group {
		display: flex;
		gap: 0.6rem;
	}

	.ghost {
		background: transparent;
		border-color: transparent;
		color: var(--text-muted);
	}

	.big {
		padding: 0.7em 1.4em;
		font-size: 1.05rem;
		flex: 1;
	}

	.square {
		width: 2.2rem;
		height: 2.2rem;
		padding: 0;
		font-size: 1.1rem;
		line-height: 1;
	}

	.cta {
		display: inline-block;
		padding: 0.45em 1.1em;
		border-radius: var(--radius-sm);
		background: var(--gold);
		border: 1px solid var(--gold);
		color: #1a1505;
		font-weight: 650;
		text-decoration: none;
		transition: background 120ms ease;
	}

	.cta:hover {
		background: #f6cd5e;
	}

	.alert {
		margin: 0 0 1.25rem;
		padding: 0.6rem 0.9rem;
		border: 1px solid rgba(224, 112, 112, 0.4);
		border-radius: var(--radius-sm);
		background: rgba(224, 112, 112, 0.08);
		color: var(--red);
		font-size: 0.9rem;
	}

	.fine {
		margin: 1rem 0 0;
		color: var(--text-faint);
		font-size: 0.85rem;
	}

	.fine.center {
		text-align: center;
	}

	.well {
		padding: 1.5rem 1.25rem 1.25rem;
		border-radius: var(--radius);
		background: rgba(0, 0, 0, 0.22);
	}

	/* smaller preview on the layout step — it's a size picker, not the mapper */
	.well.compact {
		--pad-grid-max: 300px;
	}

	/* --- connect --- */

	.connect-actions {
		display: flex;
		gap: 0.75rem;
		flex-wrap: wrap;
	}

	/* --- device list --- */

	.devices {
		display: flex;
		flex-direction: column;
		gap: 0.6rem;
	}

	.device {
		display: flex;
		align-items: center;
		gap: 0.85rem;
		width: 100%;
		padding: 0.85rem 1.1rem;
		text-align: left;
		background: var(--surface-2);
		border: 1px solid var(--border-strong);
		border-radius: var(--radius);
	}

	.device:hover:not(:disabled) {
		border-color: var(--gold);
		background: var(--surface-3);
	}

	.device:hover .device-go {
		color: var(--gold);
		transform: translateX(2px);
	}

	.device-text {
		display: flex;
		flex-direction: column;
		min-width: 0;
		flex: 1;
	}

	.device-name {
		font-weight: 600;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.device-mfr {
		font-size: 0.78rem;
		color: var(--text-muted);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.tag {
		flex-shrink: 0;
		padding: 0.2em 0.55em;
		border-radius: 999px;
		background: rgba(240, 192, 64, 0.12);
		border: 1px solid var(--gold-dim);
		color: var(--gold);
		font-family: var(--font-mono);
		font-size: 0.78rem;
	}

	.device-go {
		flex-shrink: 0;
		color: var(--text-faint);
		transition:
			color 120ms ease,
			transform 120ms ease;
	}

	.empty {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
		padding: 2rem 1rem;
		border: 1px dashed var(--border-strong);
		border-radius: var(--radius);
		color: var(--text-faint);
		font-size: 0.9rem;
	}

	.empty-icon {
		font-size: 1.6rem;
		opacity: 0.7;
	}

	/* --- grid steppers --- */

	.steppers {
		display: flex;
		align-items: end;
		justify-content: center;
		gap: 1.25rem;
		margin-bottom: 1.5rem;
	}

	.steppers-x {
		padding-bottom: 0.45rem;
		color: var(--text-faint);
		font-family: var(--font-mono);
	}

	.stepper {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.45rem;
	}

	.stepper-label {
		font-size: 0.78rem;
		font-weight: 600;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--text-muted);
	}

	.stepper-controls {
		display: flex;
		align-items: center;
		gap: 0.6rem;
	}

	.stepper-value {
		min-width: 1.6rem;
		text-align: center;
		font-family: var(--font-mono);
		font-size: 1.35rem;
		font-weight: 700;
	}

	/* --- map step --- */

	.progress {
		height: 0.45rem;
		margin-bottom: 1.25rem;
		border-radius: 999px;
		background: var(--surface-3);
		overflow: hidden;
	}

	.progress-bar {
		height: 100%;
		border-radius: 999px;
		background: linear-gradient(90deg, var(--gold), #f6cd5e);
		transition: width 200ms ease;
	}

	.sound-toggle {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		margin-top: 1.1rem;
		font-size: 0.88rem;
		color: var(--text-muted);
		user-select: none;
		cursor: pointer;
	}

	/* --- transport step --- */

	.slots {
		display: flex;
		flex-direction: column;
		gap: 0.6rem;
	}

	.slot {
		display: flex;
		align-items: center;
		gap: 0.85rem;
		width: 100%;
		padding: 0.85rem 1.1rem;
		text-align: left;
		background: var(--surface-2);
		border: 1px solid var(--border-strong);
		border-radius: var(--radius);
	}

	.slot:hover:not(:disabled) {
		border-color: var(--gold);
		background: var(--surface-3);
	}

	.slot.armed {
		border-color: var(--gold);
		box-shadow: 0 0 0 1px var(--gold-dim);
	}

	.slot.set {
		border-color: var(--green-dim);
	}

	.slot-text {
		display: flex;
		flex-direction: column;
		min-width: 0;
		flex: 1;
	}

	.slot-label {
		font-weight: 600;
	}

	.slot-hint {
		font-size: 0.78rem;
		color: var(--text-muted);
	}

	.slot-value {
		flex-shrink: 0;
	}

	.slot-empty {
		color: var(--text-faint);
		font-size: 0.85rem;
	}

	.listening {
		color: var(--gold);
		font-size: 0.85rem;
		animation: pulse 1.1s ease-in-out infinite;
	}

	@keyframes pulse {
		50% {
			opacity: 0.35;
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.listening {
			animation: none;
		}
	}

	/* --- done --- */

	.done-head {
		text-align: center;
	}

	.check {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 3rem;
		height: 3rem;
		margin: 0 auto 0.75rem;
		border-radius: 50%;
		background: rgba(85, 187, 136, 0.15);
		border: 1px solid var(--green-dim);
		color: var(--green);
		font-size: 1.4rem;
		font-weight: 700;
	}
</style>
