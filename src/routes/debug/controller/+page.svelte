<!--
  What is actually mapped, and a way to move it.

  Every other view of a controller is interpretive — the wizard shows it as a
  picture, the lesson page shows the drums one lesson wants. This one shows the
  record: every pad, the note it listens for, the drum it fires, the hi-hat
  wiring and the transport bindings, exactly as stored.

  Export/import exists because a controller is device-local *and* keyed by the
  MIDI port id, which browsers scope per origin — the same kit is a different id
  on localhost and in production, so a mapping cannot simply be copied between
  them. Import therefore always re-targets: you pick which device the incoming
  layout lands on.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { base } from '$app/paths';

	import { Controller, type ControllerSummary } from '$lib/controller.svelte';
	import { MidiHub, type MidiInputInfo } from '$lib/midi-hub.svelte';
	import { ROLE_LABELS } from '$lib/presets';
	import { noteName } from '$lib/note';
	import { controlLabel } from '$lib/transport-control';

	const midi = new MidiHub();

	let known = $state<ControllerSummary[]>([]);
	let selected = $state<string | null>(null);
	let controller = $state<Controller | null>(null);
	let drumNames = $state(new Map<number, string>());
	let status = $state('');

	// Live monitor: what the selected controller makes of what is arriving.
	let live = $state<{ at: number; raw: string; verdict: string }[]>([]);
	let listening = $state(false);

	const geometryLabel = $derived.by(() => {
		const g = controller?.geometry;
		if (!g) return '—';
		if (g.kind === 'grid') return `grid ${g.cols}×${g.rows}`;
		if (g.kind === 'schematic') return `schematic ${g.src}`;
		return 'neutral';
	});

	function load(deviceId: string | null) {
		selected = deviceId;
		controller = deviceId ? Controller.load(deviceId) : null;
		live = [];
	}

	function refresh() {
		known = Controller.list();
		if (!selected && known.length) load(known[0].deviceId);
	}

	onMount(() => {
		refresh();
		try {
			const sel = localStorage.getItem('groove-master:selectedDevice');
			if (sel) load(sel);
		} catch {
			/* storage blocked — the page still works, it just lists nothing */
		}
		fetch(`${base}/drums/manifest.json`)
			.then((r) => (r.ok ? r.json() : null))
			.then((m) => {
				if (m?.drums) {
					drumNames = new Map(
						m.drums.map((d: { note: number; name: string }) => [d.note, d.name])
					);
				}
			})
			.catch(() => {});
		const off = midi.onMessage(onMessage);
		return () => {
			off();
			midi.stop();
		};
	});

	const drumName = (n: number) => drumNames.get(n) ?? `note ${n}`;

	// --- live monitor ---------------------------------------------------------

	async function listen(info: MidiInputInfo) {
		if (!midi.access) await midi.connect();
		midi.listen(info.id);
		listening = true;
		status = `Listening to ${info.name}`;
	}

	function onMessage(data: Uint8Array) {
		if (!controller) return;
		const ev = controller.handle(data);
		let verdict: string;
		if (ev.kind === 'hit') verdict = `hit — ${ev.pad.label} → ${drumName(ev.note)} (vel ${ev.velocity})`;
		else if (ev.kind === 'pedal') verdict = `pedal — ${ev.which} ${ev.down ? 'down' : 'up'}`;
		else if (ev.kind === 'transport') verdict = `transport — ${ev.which}`;
		else if (ev.kind === 'unmapped') verdict = `unmapped — note ${ev.note}`;
		else return; // clock and other noise: not worth a row
		live = [
			{ at: Date.now(), raw: [...data].map((b) => b.toString(16).padStart(2, '0')).join(' '), verdict },
			...live
		].slice(0, 12);
	}

	// --- export / import ------------------------------------------------------

	const exported = $derived(
		controller ? JSON.stringify({ ...controller.toJSON(), deviceId: undefined }, null, 2) : ''
	);

	let importText = $state('');
	let importTarget = $state<string>('');

	async function copyExport() {
		try {
			await navigator.clipboard.writeText(exported);
			status = 'Copied to clipboard';
		} catch {
			status = 'Clipboard blocked — select the text and copy it by hand';
		}
	}

	function download() {
		const name = (controller?.name || 'controller').replace(/[^a-z0-9]+/gi, '-').toLowerCase();
		const url = URL.createObjectURL(new Blob([exported], { type: 'application/json' }));
		const a = document.createElement('a');
		a.href = url;
		a.download = `${name}.json`;
		a.click();
		URL.revokeObjectURL(url);
	}

	/**
	 * Import onto a chosen device id. The id in the file is deliberately ignored:
	 * it came from another origin or another machine, where the same hardware has
	 * a different id, so honouring it would write a config nothing can find.
	 */
	function doImport() {
		const target = importTarget.trim();
		if (!target) {
			status = 'Pick a device to import onto first';
			return;
		}
		let parsed: unknown;
		try {
			parsed = JSON.parse(importText);
		} catch {
			status = 'That is not valid JSON';
			return;
		}
		const incoming = Controller.fromStored(target, parsed);
		if (!incoming) {
			status = 'Parsed, but it does not look like a controller config';
			return;
		}
		incoming.save();
		refresh();
		load(target);
		status = `Imported onto ${target} — ${incoming.pads.filter((p) => p.note != null).length} pads mapped`;
	}
</script>

<svelte:head>
	<title>Groove Academy — Controller</title>
</svelte:head>

<h1>Controller</h1>
<p class="lede">
	What is actually stored for each controller set up on this machine, and a way to move it
	between them. Mappings are keyed by MIDI port id, which browsers scope per origin — the
	same kit has a different id on localhost and in production, so importing always re-targets.
</p>

<section class="bar">
	<label>
		<span class="lbl">Stored controller</span>
		<select value={selected} onchange={(e) => load(e.currentTarget.value || null)}>
			<option value="">— none —</option>
			{#each known as k (k.deviceId)}
				<option value={k.deviceId}>
					{k.name || k.deviceId} · {k.kind} · {k.padCount} mapped
				</option>
			{/each}
		</select>
	</label>
	<button onclick={refresh}>Rescan storage</button>
	{#if status}<span class="status">{status}</span>{/if}
</section>

{#if controller}
	<section class="card">
		<h2>Identity</h2>
		<dl class="meta">
			<dt>Device id</dt>
			<dd><code>{controller.deviceId}</code></dd>
			<dt>Name</dt>
			<dd>{controller.name || '—'}</dd>
			<dt>Kind</dt>
			<dd>{controller.kind}</dd>
			<dt>Profile</dt>
			<dd>{controller.profile ?? '—'}</dd>
			<dt>Geometry</dt>
			<dd>{geometryLabel}</dd>
			<dt>Sample kit</dt>
			<dd>{controller.kitId}</dd>
			<dt>Last used</dt>
			<dd>{controller.lastUsed ?? '—'}</dd>
			<dt>Transport</dt>
			<dd>
				start {controlLabel(controller.transport.start)} · stop
				{controlLabel(controller.transport.stop)}
			</dd>
			<dt>Hi-hat</dt>
			<dd>
				{controller.hihat.mode}
				{#if controller.hihat.pedal}· pedal {controlLabel(controller.hihat.pedal)}{/if}
				· closed {controller.hihat.closed} · open {controller.hihat.open}
			</dd>
		</dl>
	</section>

	<section class="card">
		<h2>Pads <span class="count">{controller.pads.filter((p) => p.note != null).length} of {controller.pads.length} mapped</span></h2>
		<table>
			<thead>
				<tr><th>id</th><th>label</th><th>role</th><th>listens for</th><th>plays</th></tr>
			</thead>
			<tbody>
				{#each controller.pads as pad (pad.id)}
					<tr class:unmapped={pad.note == null}>
						<td><code>{pad.id}</code>{#if pad.pedal}<span class="tag">{pad.pedal} pedal</span>{/if}</td>
						<td>{pad.label}</td>
						<td>{ROLE_LABELS[pad.role] ?? pad.role}</td>
						<td>
							{#if pad.note == null}
								<span class="none">not mapped</span>
							{:else}
								{pad.note} <span class="dim">{noteName(pad.note)}</span>
							{/if}
							{#if pad.altNote != null}
								<span class="alt">+ {pad.altNote} <span class="dim">{noteName(pad.altNote)}</span></span>
							{/if}
						</td>
						<td>
							{drumName(pad.sound)} <span class="dim">({pad.sound})</span>
							{#if pad.altNote != null}
								<span class="alt">/ {drumName(pad.altSound ?? 46)}</span>
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</section>

	<section class="card">
		<h2>Live</h2>
		<p class="hint">
			Hit something and see what this controller makes of it — the fastest way to tell a
			wrong mapping from a wrong picture.
		</p>
		<div class="devices">
			{#if !midi.supported}
				<span class="none">This browser has no Web MIDI.</span>
			{:else if !midi.access}
				<button onclick={() => midi.connect()}>Enable MIDI</button>
			{:else if midi.inputs.length === 0}
				<span class="none">No inputs. <button onclick={() => midi.refresh()}>Rescan</button></span>
			{:else}
				{#each midi.inputs as input (input.id)}
					<button onclick={() => listen(input)} class:active={listening}>{input.name}</button>
				{/each}
			{/if}
		</div>
		{#if live.length}
			<ul class="live">
				{#each live as row (row.at + row.raw)}
					<li><code>{row.raw}</code> <span class="arrow">→</span> {row.verdict}</li>
				{/each}
			</ul>
		{/if}
	</section>

	<section class="card">
		<h2>Export</h2>
		<p class="hint">The stored record, minus the device id — that is re-chosen on import.</p>
		<textarea readonly rows="12" value={exported}></textarea>
		<div class="row">
			<button onclick={copyExport}>Copy</button>
			<button onclick={download}>Download .json</button>
		</div>
	</section>
{:else}
	<p class="empty">
		Nothing stored for this device yet. Set one up on the
		<a href="{base}/onboarding">Setup</a> page.
	</p>
{/if}

<section class="card">
	<h2>Import</h2>
	<p class="hint">
		Paste a layout and choose which device it belongs to. The id inside the file is ignored:
		it came from somewhere the same hardware has a different id.
	</p>
	<div class="targets">
		<label>
			<span class="lbl">Onto device</span>
			<select bind:value={importTarget}>
				<option value="">— choose —</option>
				{#each midi.inputs as input (input.id)}
					<option value={input.id}>{input.name} (connected)</option>
				{/each}
				{#each known as k (k.deviceId)}
					<option value={k.deviceId}>{k.name || k.deviceId} (stored)</option>
				{/each}
			</select>
		</label>
		<label>
			<!-- Neither connected nor stored is a real case: restoring a backup before
			     plugging the kit in. A debug page can take an id on trust. -->
			<span class="lbl">…or type an id</span>
			<input type="text" bind:value={importTarget} placeholder="MIDI port id" />
		</label>
	</div>
	{#if !midi.access && midi.supported}
		<p class="hint">
			<button onclick={() => midi.connect()}>Enable MIDI</button> to import onto a connected
			device rather than one already stored.
		</p>
	{/if}
	<textarea bind:value={importText} rows="8" placeholder="Paste controller JSON here"></textarea>
	<div class="row">
		<button class="primary" onclick={doImport} disabled={!importText.trim()}>Import</button>
	</div>
</section>

<style>
	.lede {
		max-width: 46rem;
		margin: -0.5rem 0 1.5rem;
		color: var(--text-muted);
	}

	.bar {
		display: flex;
		align-items: end;
		gap: 0.9rem;
		flex-wrap: wrap;
		margin-bottom: 1.25rem;
	}

	label {
		display: flex;
		flex-direction: column;
		gap: 0.35rem;
	}

	.lbl {
		font-size: 0.75rem;
		font-weight: 600;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--text-muted);
	}

	.targets {
		display: flex;
		gap: 0.9rem;
		flex-wrap: wrap;
		align-items: end;
		margin-bottom: 0.75rem;
	}

	select,
	input[type='text'],
	textarea {
		padding: 0.45em 0.6em;
		border-radius: var(--radius-sm);
		border: 1px solid var(--border-strong);
		background: var(--surface-2);
		color: var(--text);
		font-family: inherit;
	}

	textarea {
		width: 100%;
		font-family: var(--font-mono);
		font-size: 0.78rem;
		line-height: 1.5;
		resize: vertical;
	}

	.card {
		max-width: 60rem;
		margin: 0 0 1.25rem;
		padding: 1rem 1.15rem;
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		background: var(--surface);
	}

	.card h2 {
		margin: 0 0 0.75rem;
		font-size: 1rem;
	}

	.count {
		margin-left: 0.5rem;
		font-family: var(--font-mono);
		font-size: 0.78rem;
		font-weight: 400;
		color: var(--text-faint);
	}

	.hint {
		margin: 0 0 0.75rem;
		color: var(--text-muted);
		font-size: 0.88rem;
	}

	.meta {
		display: grid;
		grid-template-columns: max-content 1fr;
		gap: 0.35rem 1rem;
		margin: 0;
		font-size: 0.88rem;
	}

	.meta dt {
		color: var(--text-faint);
	}

	.meta dd {
		margin: 0;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.85rem;
	}

	th {
		text-align: left;
		font-weight: 600;
		color: var(--text-faint);
		font-size: 0.72rem;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		padding-bottom: 0.4rem;
	}

	td {
		padding: 0.35rem 0.6rem 0.35rem 0;
		border-top: 1px solid var(--border);
	}

	tr.unmapped td {
		opacity: 0.55;
	}

	code {
		font-family: var(--font-mono);
		font-size: 0.8em;
	}

	.dim {
		color: var(--text-faint);
	}

	.none {
		color: var(--text-faint);
		font-style: italic;
	}

	.alt {
		margin-left: 0.4rem;
		color: var(--cyan);
	}

	.tag {
		margin-left: 0.4rem;
		padding: 0.1em 0.4em;
		border-radius: 999px;
		border: 1px solid var(--gold-dim);
		color: var(--gold);
		font-size: 0.68rem;
	}

	.devices {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
		margin-bottom: 0.75rem;
	}

	.live {
		margin: 0;
		padding: 0;
		list-style: none;
		font-size: 0.82rem;
	}

	.live li {
		padding: 0.25rem 0;
		border-top: 1px solid var(--border);
	}

	.arrow {
		color: var(--text-faint);
	}

	.row {
		display: flex;
		gap: 0.6rem;
		margin-top: 0.75rem;
	}

	.status {
		color: var(--green);
		font-size: 0.85rem;
	}

	.empty {
		max-width: 46rem;
		color: var(--text-muted);
	}
</style>
