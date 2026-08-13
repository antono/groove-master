## Context

What the rest of the app actually consumes from setup is small. `/lessons/[id]`
reads one thing — `cfg.notes[i] → cfg.soundNotes[i]`, folded into a
`Map<number, number>` — and uses `cfg.cols` / `cfg.rows` only to decide whether
to draw a schematic beside the chart. `warmKit()` reads `cfg.kit`. Everything
else in the saved blob is the wizard talking to itself.

That is the lever. A drum kit does not need a new pipeline; it needs a different
way of arriving at the same map, plus one place where a note is allowed to be
ambiguous.

But that map is assembled by hand in each consumer. `/lessons/[id]` holds
`ctrlMap`, `transport`, `padCols`, `padRows`, `padDrums`, `savedDeviceName` and
`kit` as seven separate pieces of `$state` rebuilt by `loadDeviceMapping()`;
`handleMidi` then checks transport, looks up the map, and would need pedal state
threaded through as an eighth. `/onboarding` writes the same blob from a
different set of variables, and `/debug/settings` from a third. Nobody owns the
instrument, so a second kind of instrument means a second special case in three
places at once — which is the argument for the Controller.

Three constraints shape the rest:

- **Pad notes cannot be hard-coded.** `presets.ts` already says so for grid
  controllers, and it is more true here: the MD-90's panel assigns any MIDI note
  to any pad, and its factory defaults are not published in a form we can trust.
  Reviews agree only on the shape — seven velocity pads reading as a snare,
  three toms, a hi-hat and two cymbals, with the hi-hat sat oddly to the right
  of the snare — plus jacks for a kick and a hi-hat footswitch.
  ([e-drums.nl review](https://e-drums.nl/en/millenium-md-90-review/),
  [product page](https://e-drums.nl/en/product/millennium-md-90-mobile-drum/),
  [reference photo](https://e-drums.nl/wp-content/uploads/2022/07/Millenium-MD-90-Mobile-Drum.jpg))
- **Scoring matches on an exact GM note.** `registerHit(gmNote, beat)` finds the
  nearest unmatched target with `t.note === gmNote`. So a hi-hat that means two
  different GM notes must be resolved to one _before_ it reaches scoring, not
  inside it.
- **Anything unmapped is silent, and anything mapped but unexpected is an
  extra.** `handleMidi` drops notes absent from `ctrlMap`, and `registerHit`
  banks a mapped-but-unwanted note as an `extra`. A hi-hat pedal that emits its
  own note-on would therefore be scored as a wrong hit on every close.

## Goals / Non-Goals

**Goals:**

- One object standing for the instrument, so that "what kind of controller is
  this" is asked once, at load, and never again per message or per component.
- A setup path that shows an e-drum kit as a kit and comes out the other end
  with the same note map the grid path produces.
- Correct hi-hat behaviour across the three wirings real kits use, discovered
  rather than assumed.
- A generic path that is as complete as a profiled one, and a way for a generic
  layout to become a profile.
- Zero change to the grid flow, and no migration for existing saved configs.

**Non-Goals:**

- E-drum-specific lessons or curriculum. Lessons stay written for finger
  drumming; a kit simply plays them.
- Positional sensing, rim/bell zones, choke, or velocity-layered articulation.
  One pad, one drum (plus the hi-hat's two voices).
- Reading shared layouts back into the app. Submissions are a mailbox we empty
  by hand into shipped profiles, not a live catalogue.
- Rebuilding `/debug/settings` for e-drums. It must decline to damage an e-drum
  config; making it edit one is later work.
- Per-controller latency calibration. The metadata shape is deliberately open so
  an offset can be added later, but measuring and applying one is its own change.
- Syncing controllers between devices. A controller is a property of the machine
  the hardware is plugged into, and stays device-local.

## Decisions

### 1. The branch is a route, not a mode

`Step` becomes two ordered lists sharing the first two entries:

```
grid  : connect · device · grid   · map        · transport · done
edrum : connect · device · kit    · map drums  · pedals · test · transport · done
```

The rail renders whichever list is active, so the student sees a truthful
step count rather than a five-dot rail that secretly has seven states. Choosing
a profile on the `kit` step (or "this is a grid controller") is what selects the
list, and going back to `device` resets it.

_Alternative rejected:_ one flow that adapts each step. The steps have almost
nothing in common past "listen for a note" — the grid step is a size picker, the
kit step is a picture — and merging them buries two simple screens inside one
conditional.

### 2. A profile supplies geometry and roles; capture supplies notes

```ts
type KitProfile = {
  id: string; // 'millenium-md-90'
  label: string; // 'Millenium MD-90'
  match: RegExp; // against the MIDI input name
  schematic: string; // '/kits/millenium-md-90.svg'
  pads: KitPad[]; // ordered as the wizard walks them
};
type KitPad = {
  id: string; // matches an element id in the SVG
  label: string; // 'Snare', 'Tom 1', 'Crash'
  role: DrumRole; // 'snare' | 'tom' | 'hihat' | 'crash' | 'ride' | 'kick'
  sound: number; // suggested GM note, editable
  pedal?: "kick" | "hihat"; // arrives via a footswitch jack, not a pad
};
```

`sound` is a suggestion the student can change; `role` is what the pedal step
and the "your kit can't play this" check reason about. No `note` field exists at
all, so there is nowhere for a wrong factory default to hide.

### 3. The schematic is an SVG asset with addressable drums

The preview fetches the profile's SVG, inlines it, and toggles classes on the
`<g>` whose `id` matches a `KitPad.id` — `pending`, `captured`, `lit`. One
component serves every profile and every consumer (see decision 6); a new kit is
a new SVG plus a table row, no new code.

Inlining means the SVG is executed as document markup, so **only first-party
files under `static/kits/` are ever loaded this way**. A shared layout never
carries or names an SVG.

_Alternative rejected:_ describing pads as `{cx, cy, r}` in the profile and
drawing them generically. It is safer and needs no asset, but every kit then
looks like circles on a rectangle, which is the problem this change exists to
fix. The geometry form stays available as a fallback for a profile drawn before
its picture is.

### 4. The pedal step discovers the hi-hat rather than declaring it

Three prompts, in order: _press the pedal_, _hit the hi-hat with the pedal up_,
_hit it with the pedal down_. What arrives decides the mode:

| Observed                                 | Mode       | Resolution at play time                           |
| ---------------------------------------- | ---------- | ------------------------------------------------- |
| Up and down hits give different notes    | `two-note` | static map; open note → 46, closed note → 42      |
| Same note, pedal sends CC or note-on/off | `stateful` | hold pedal state; that note → 42 or 46            |
| Pedal sends nothing                      | `none`     | the pad is one voice, whichever the student picks |

`stateful` also records what the pedal itself emitted, and that message is
registered as **control, not performance** — it plays no sample and never
becomes an `extra`. `two-note` needs no state, which is why it is checked first:
a kit that can be handled statelessly should be.

_Alternative rejected:_ asking the student which kind of hi-hat they have. Most
people do not know, and the three gestures take about as long as reading the
question.

**A pedal at rest is open, and that is the trap.** Physically correct, and
useless here: this curriculum is overwhelmingly closed hats, so a student who
sits down and plays scores nothing until they hold a footswitch down for the
whole lesson. Worse, it fails silently — the preview lights the hi-hat for
_either_ voice, so the hits look like they landed.

So `hihatPreference` pins the hat to one voice, and `/lessons/[id]` sets it to
whichever voice the lesson uses when the lesson uses exactly one. Such a lesson
is teaching the pattern, not pedal technique. Only the two lessons that use both
voices (`disco-open-hats`, `checkpoint-2`) leave the pedal in charge, which is
exactly where it belongs.

The pin is a bare GM note, not a lesson: the Controller still knows only what the
device means. Who pins, and from what, stays the page's business. It also falls
out that a single-voice kit can play a lesson written for the other voice, so
`drums` counts a pinned voice as producible and the "can't play this" notice
stops firing on a case that now works.

### 5. The Controller facade

`src/lib/controller.svelte.ts` — a rune-bearing class, like `MidiHub`, because
the preview reads its state reactively.

```ts
class Controller {
  // identity & metadata
  readonly deviceId: string;
  readonly name: string;
  readonly kind: 'grid' | 'edrum';
  readonly profile: string | null;   // 'millenium-md-90' | 'mpd218' | null
  kitId = $state(1);                 // sample kit, editable
  lastUsed: string;

  // layout
  readonly pads: Pad[];              // id, label, role, note, sound
  readonly geometry: Geometry;       // { kind:'grid', cols, rows } | { kind:'schematic', src } | { kind:'neutral' }

  // input — the facade
  handle(data: Uint8Array): ControllerEvent;
  hihat = $state<HihatConfig>(…);                       // how the hat is wired
  hihatPosition = $state<'open' | 'closed' | null>(null); // preview reads this

  // capability
  get drums(): Set<number>;
  canPlay(gmNote: number): boolean;

  // persistence
  static load(deviceId: string): Controller | null;
  static list(): ControllerSummary[];
  save(): void;
}

type ControllerEvent =
  | { kind: 'hit'; note: number; velocity: number; pad: Pad }  // note already resolved
  | { kind: 'pedal'; which: 'hihat' | 'kick'; down: boolean }
  | { kind: 'transport'; which: 'start' | 'stop' }
  | { kind: 'unmapped'; note: number }
  | { kind: 'none' };
```

The whole of `handleMidi` collapses to a switch:

```ts
const ev = controller.handle(event.data);
if (ev.kind === "transport") return handleTransport(ev.which);
if (ev.kind !== "hit") return; // pedals fall out here, unscored
player?.play(controller.kitId, ev.note);
flash(ev.note);
if (playing && !paused) registerHit(ev.note, currentBeat());
```

`{ kind: 'none' }` rather than `null` is deliberate: an unrecognised message is a
fact the controller states. `unmapped` is the sharper version of the same idea —
it is how the wizard's test step says "that pad isn't mapped" instead of showing
nothing, which is indistinguishable from a dead pad.

Two orderings inside `handle()` matter. Pads are matched **before** transport, so
a note bound to both still plays its drum — behaviour inherited from the
`routeTransport` this replaced. And the pedal is matched **after** pads, so a
student who taps the hat instead of pressing the pedal cannot bind their hi-hat
as its own pedal.

The facade is where the three constraints above are honoured — the ambiguity of
a hi-hat is spent inside `handle()`, and a pedal signal leaves as `pedal`, so it
can never reach `registerHit` and become an `extra`.

_Alternative rejected:_ keeping `ctrlMap` and adding a resolver function beside
it. It fixes the hi-hat and nothing else — transport matching, the geometry
triple and the storage parsing all stay scattered, and each new controller trait
lands in the lesson page again.

### 6. One preview, three modes

`$lib/controller-preview.svelte` takes a controller and a mode, and is the only
thing that draws pads:

| Mode      | Where               | What it shows                                                                               |
| --------- | ------------------- | ------------------------------------------------------------------------------------------- |
| `capture` | wizard              | one pad current and pulsing, captured pads with their note, rest pending; click to audition |
| `map`     | resting lesson page | the lesson's drums named in their family hue, others blank                                  |
| `play`    | during a run        | as `map`, sized up, when there is room                                                      |

Geometry comes from `controller.geometry`, so the same component draws a 4×4
grid, an MD-90 schematic, or a neutral arrangement without the caller choosing.
That is what makes `controller-map.svelte` and `pad-grid.svelte` redundant: they
are the `map` and `capture` modes of this component, written before there was a
controller to ask.

Animation is already right in both of them and is ported, not reinvented — the
lit pad that flares and sinks, the current pad that pulses, and both suppressed
under `prefers-reduced-motion`. The one new animation is the hi-hat: with a
stateful pedal, `controller.hihat` drives an open/closed state on the schematic,
so the picture shows the pedal the student is holding.

_Alternative rejected:_ leaving the wizard's `pad-grid.svelte` alone and only
absorbing `controller-map.svelte`. It is the lower-risk edit, but it leaves two
components drawing the same pads in different states, which is the duplication
this abstraction exists to end.

### 7. Where the preview sits during a run

The highway is sized first, from `lanes.length * laneH` and the compact / medium
/ full `view` the student cycles. The preview then takes what is left, at the
largest of its sizes that fits, and is dropped when nothing is left. It is never
allowed to shrink the highway — the highway is the lesson; the preview is a
reference.

"What is left" is not flow space: while playing, `.highway.full` is
`position: fixed; inset: 0` with the lanes as a band centred in it, so there is
no space below it in the document at all. The room is the empty half of that
field beneath the band — `(winH − bandH) / 2` — and the preview is fixed into it
above the highway's own z-index. `laneH` knows nothing about any of this, which
is what makes "sized first" true rather than merely intended.

Hits are sparse and the highway scrolls in CSS on `.strip`, so lighting a pad
costs a class toggle and cannot contend with the scroll. The rule to hold is
that the preview never reads or writes layout during a run.

### 8. The saved config gains structure and keeps its mirror

```jsonc
{
  "kind": "edrum", // absent  ⇒ legacy grid, read exactly as today
  "profile": "millenium-md-90", // or "custom", or a grid preset id
  "deviceName": "Millenium MD-90",
  "lastUsed": "2026-08-12T09:14:00.000Z",
  "pads": [
    {
      "id": "snare",
      "label": "Snare",
      "role": "snare",
      "note": 38,
      "sound": 38,
    },
  ],
  "hihat": {
    "mode": "stateful",
    "pedal": { "kind": "cc", "data1": 4 },
    "closed": 42,
    "open": 46,
  },
  "notes": [38, 45, 47, 48, 42, 49, 51, 36], // mirror
  "soundNotes": [38, 45, 47, 48, 42, 49, 51, 36], // mirror
  "kit": 1,
  "transport": { "start": null, "stop": null },
}
```

`notes` / `soundNotes` are written from `pads` on every save. A reader that has
not learned the new shape — `warmKit`, anything written next month — still gets
a working map, minus the hi-hat subtlety. `cols` / `rows` are kept for grid
controllers and omitted for kits, which is already how `/lessons/[id]` decides
not to draw a rectangle.

Grid controllers get `pads` too, synthesised from the captured notes with
positional labels ("Pad 7"), so the Controller has one internal shape and only
`geometry` differs. This is the whole reason the abstraction pays: `kind` is
consulted when building a controller and essentially nowhere afterwards.

No version field: `kind` is the discriminator, and its absence means grid.
Metadata is additive — a field that is missing is missing, never a load failure.

### 9. Sharing is an insert-only mailbox

```sql
create table public.device_layouts (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid references auth.users (id) on delete set null,  -- null when signed out
  device_name text not null,
  layout     jsonb not null,
  created_at timestamptz not null default now()
);
```

`insert` granted to `anon` and `authenticated`; **no select policy for either**,
so the table is write-only from the client and read only by the service role.
A signed-out student can still contribute, which matters — the people most
likely to have an unrecognised kit are the least likely to have made an account
first.

_Alternative rejected:_ requiring sign-in. It converts a two-second favour into
a signup funnel and would cost us most of the layouts.

## Risks / Trade-offs

- **The Controller touches the one file that must not break.** `/lessons/[id]`
  is where scoring lives, and this change rewrites how it receives MIDI. The
  mitigation is that the rewrite is a _narrowing_: `registerHit`, `flash`,
  `player.play` and every line below them keep their current signatures and
  behaviour, and only the four lines above them change. Anything that alters
  scoring arithmetic is out of scope here.
- **Absorbing `pad-grid.svelte` risks a working screen.** The wizard's grid
  capture is finished and pleasant, and porting it into a mode of another
  component can only lose. It is ported verbatim — same states, same neumorphic
  pads, same pulse — with the grid path walked end to end as its own
  verification task rather than being assumed from the kit path passing.
- **A facade can grow into a god object.** The line held here: the Controller
  knows what the _device_ is and means. It does not know about lessons, scoring,
  samples or the audio clock. `handle()` returns a fact about a message; what
  that fact is worth is the page's business.
- **Anonymous insert invites junk.** Mitigated by a size check constraint on
  `layout`, a length cap on `device_name`, and the fact that nothing reads the
  table automatically — a bad row costs a moment's triage, not a bad profile.
  If it becomes a problem, the fallback is a signed-in-only policy.
- **The pedal step can misread a kit.** A student who presses the pedal at the
  wrong moment gets the wrong mode. The test step is the safety net: it is where
  a hi-hat that lights the wrong drum shows up, and it offers a jump straight
  back to the pedal step.
- **A `none` hi-hat cannot hit open-hat targets.** Those notes will read as
  misses however well they are played. The setup names this outright rather than
  letting the student discover it in a result screen — see the `edrum-play`
  requirement on unplayable drums.
- **Seven steps is a long wizard.** Pedals and transport are both skippable and
  say so, and the test step is where most students will feel the setup paid off.
  Watch `onboardingStep` — the analytics already report the last step reached,
  which is exactly the measurement needed if the drum path is being abandoned.
- **Two schematic consumers, one asset.** A profile SVG whose ids drift from its
  `pads` table breaks both the wizard and the lesson page. A build-time check
  that every `KitPad.id` exists in its SVG is cheap and worth having.
