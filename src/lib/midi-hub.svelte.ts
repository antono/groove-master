// MidiHub — thin reactive wrapper over the Web MIDI API.
//
// Web MIDI enumerates both USB-MIDI and BLE-MIDI class-compliant controllers,
// so it is the transport for both "USB" and "Bluetooth" pads. For BLE pads that
// aren't paired yet, `pairBluetooth()` opens the browser's Bluetooth chooser
// (filtered to the BLE-MIDI GATT service) so the device becomes visible to
// Web MIDI, then re-scans.
//
// Runes live in a `.svelte.ts` module so `$state` is reactive when consumed
// from components.

/** BLE-MIDI GATT service UUID (MIDI over Bluetooth LE spec). */
const BLE_MIDI_SERVICE = "03b80e5a-ede8-4b33-a751-6ce34ec4c700";

// Web Bluetooth is not in the default DOM lib; declare the sliver we use.
type Bluetooth = {
  requestDevice(options: {
    filters: { services: string[] }[];
  }): Promise<unknown>;
};

export type MidiInputInfo = { id: string; name: string; manufacturer: string };
type NoteListener = (note: number, velocity: number) => void;

export class MidiHub {
  access = $state<MIDIAccess | null>(null);
  inputs = $state<MidiInputInfo[]>([]);
  supported = $state(true);
  bluetoothSupported = $state(false);
  error = $state<string | null>(null);

  #current: MIDIInput | null = null;
  #listeners = new Set<NoteListener>();

  constructor() {
    if (typeof navigator !== "undefined") {
      this.supported = typeof navigator.requestMIDIAccess === "function";
      this.bluetoothSupported = "bluetooth" in navigator;
    }
  }

  async connect(): Promise<boolean> {
    this.error = null;
    if (!this.supported) {
      this.error =
        "Web MIDI is not supported in this browser. Try Chrome, Edge, or Opera.";
      return false;
    }
    try {
      this.access = await navigator.requestMIDIAccess({ sysex: false });
      this.access.onstatechange = () => this.refresh();
      this.refresh();
      return true;
    } catch {
      this.error =
        "MIDI access was blocked. Allow MIDI for this site and try again.";
      return false;
    }
  }

  /** Open the BLE chooser so a Bluetooth-MIDI pad becomes visible to Web MIDI. */
  async pairBluetooth(): Promise<void> {
    this.error = null;
    const bt = (navigator as Navigator & { bluetooth?: Bluetooth }).bluetooth;
    if (!bt) {
      this.error = "Web Bluetooth is not supported in this browser.";
      return;
    }
    try {
      await bt.requestDevice({ filters: [{ services: [BLE_MIDI_SERVICE] }] });
      // Ensure we hold MIDI access, then re-enumerate; the paired device
      // should now appear as an input.
      if (!this.access) await this.connect();
      this.refresh();
      if (this.inputs.length === 0) {
        this.error =
          "Paired — if the pad still isn't listed, reconnect it and rescan.";
      }
    } catch {
      /* user dismissed the chooser — not an error */
    }
  }

  refresh() {
    if (!this.access) return;
    this.inputs = [...this.access.inputs.values()].map((i) => ({
      id: i.id,
      name: i.name ?? "Unknown device",
      manufacturer: i.manufacturer ?? "",
    }));
  }

  /** Route note-on events from the given input id to registered listeners. */
  listen(id: string) {
    if (!this.access) return;
    if (this.#current) this.#current.onmidimessage = null;
    this.#current = this.access.inputs.get(id) ?? null;
    if (this.#current) this.#current.onmidimessage = (e) => this.#onMessage(e);
  }

  stop() {
    if (this.#current) this.#current.onmidimessage = null;
    this.#current = null;
  }

  /** Subscribe to note-on events. Returns an unsubscribe fn. */
  onNote(fn: NoteListener): () => void {
    this.#listeners.add(fn);
    return () => this.#listeners.delete(fn);
  }

  #onMessage(event: MIDIMessageEvent) {
    if (!event.data || event.data.length < 3) return;
    const [status, note, velocity] = event.data;
    // note-on only (0x90 with non-zero velocity)
    if ((status & 0xf0) !== 0x90 || velocity === 0) return;
    this.#listeners.forEach((fn) => fn(note, velocity));
  }
}
