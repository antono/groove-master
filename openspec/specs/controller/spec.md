# controller Specification

## Purpose

One object that stands for the student's instrument. It owns what the device is
(identity, kind, profile, metadata), what its inputs mean (controller note to GM
note, pedals, transport buttons), what it can and cannot play, and how it is
stored — so no page has to know the shape of a saved config or the difference
between a pad grid and a drum kit.

## Requirements

### Requirement: Controller as a facade over device input

The system SHALL provide a single controller object that interprets raw MIDI
messages from the student's device, returning for each message what it means:
a drum hit with a resolved GM note and velocity, a pedal movement, a transport
press, or nothing.

Consumers SHALL NOT interpret raw MIDI themselves. Note mapping, pedal state,
bounce handling and transport matching SHALL live behind this one call, so a
page reacts to meaning rather than to bytes.

A note from a control the controller has no pad for SHALL be reported as
unmapped, carrying that note, so a caller can say what arrived. Any other
unrecognised message SHALL be reported as nothing rather than guessed at.

Where one note is bound both to a pad and to a transport button, the pad SHALL
win: an instrument always plays its drum.

#### Scenario: A pad hit is reported as a drum

- **WHEN** a note-on arrives from a mapped pad
- **THEN** the controller reports a hit carrying the resolved GM note and the
  velocity
- **AND** the caller does not inspect the raw bytes

#### Scenario: A transport button is reported as transport

- **WHEN** a message matching a captured Play or Stop binding arrives
- **THEN** the controller reports a transport press
- **AND** it is not reported as a hit

#### Scenario: An unmapped pad is reported as such

- **WHEN** a note arrives from a pad that was never captured
- **THEN** the controller reports it as unmapped, carrying the note
- **AND** it is not a hit, so no sample plays and no score changes

#### Scenario: A pad outranks a stale transport binding

- **GIVEN** a note bound both to a pad and to a transport button
- **WHEN** that note arrives
- **THEN** the controller reports a hit
- **AND** does not report a transport press

### Requirement: Pedal-aware note resolution

Where a controller describes a stateful hi-hat, it SHALL track the pedal's
position from the recorded pedal message and SHALL resolve a hi-hat strike to
the closed or open GM note according to that position, before reporting the hit.

Where it describes a two-note hi-hat, resolution SHALL be the static map
recorded at setup and SHALL NOT depend on pedal state.

Resolution SHALL be complete by the time a hit is reported, so that scoring,
sample playback and highlighting all see one unambiguous note.

#### Scenario: Closed and open strikes resolve differently

- **GIVEN** a controller with a stateful hi-hat
- **WHEN** the hi-hat is struck with the pedal down and then with it up
- **THEN** the first hit reports the closed hi-hat note and the second the open
  one

#### Scenario: Pedal position survives between hits

- **WHEN** the pedal is moved and no hi-hat is struck for several beats
- **THEN** the next hi-hat strike uses the pedal's current position
- **AND** no stale position from an earlier bar is applied

#### Scenario: A two-note hi-hat ignores pedal state

- **GIVEN** a controller with a two-note hi-hat
- **WHEN** either hi-hat note arrives
- **THEN** it resolves to its recorded sound regardless of any pedal traffic

### Requirement: A pinned hi-hat voice overrides the pedal

A controller SHALL accept a pinned hi-hat voice, and while one is pinned every
hi-hat strike SHALL resolve to it, whatever the pedal is doing and however the
hat is wired. Clearing the pin SHALL return the hat to pedal control.

A pinned voice SHALL count as producible, so an instrument that cannot natively
send that voice is not reported as unable to play it.

The controller SHALL NOT decide when to pin: it knows what the device means and
nothing about what is being played on it.

Callers SHALL pin the voice a lesson asks for whenever that lesson uses exactly
one, because such a lesson teaches the pattern rather than pedal technique. A
lesson using both voices SHALL leave the pedal in charge.

#### Scenario: A closed-hat lesson with the pedal at rest

- **GIVEN** a stateful hi-hat whose pedal is up, and a lesson using closed hats
  only
- **WHEN** the student strikes the hi-hat without touching the pedal
- **THEN** the hit resolves to the closed hi-hat and is scored against the lesson
- **AND** the student is not required to hold the pedal down to be heard

#### Scenario: A lesson using both voices leaves the pedal in charge

- **GIVEN** a stateful hi-hat and a lesson using both open and closed hats
- **WHEN** the student strikes the hi-hat with the pedal down and then with it up
- **THEN** the first resolves to closed and the second to open

#### Scenario: A single-voice kit meets a lesson written for the other voice

- **GIVEN** a controller whose hi-hat sends one voice only
- **WHEN** a lesson uses only the voice it does not natively send
- **THEN** that voice is pinned, the strikes score, and no gap is reported

### Requirement: Pedal traffic is control, not performance

A message recorded as a pedal's own signal SHALL be reported as a pedal
movement, never as a hit. It SHALL NOT play a sample, SHALL NOT be matched
against a target, and SHALL NOT be counted as an extra note.

#### Scenario: Working the pedal does not damage a score

- **WHEN** the student opens and closes the hi-hat pedal repeatedly during a run
- **THEN** no sample is played by the pedal itself
- **AND** the run's extra-note count is unaffected

#### Scenario: A footswitch mapped as a drum still scores

- **WHEN** a footswitch was captured as the kick drum rather than as a pedal
  signal
- **THEN** it is reported as a hit and sounds and scores like any pad

### Requirement: Controller metadata

A controller SHALL carry, and persist, at least: the MIDI port id it was
configured against, its display name, its kind (a pad grid or a drum kit), the
profile or preset it came from if any, its chosen drum kit for samples, its
transport bindings, its pedal and hi-hat configuration, its full pad list, and
when it was last used.

Metadata SHALL be additive: a controller stored before a field existed SHALL
load with that field absent rather than failing.

#### Scenario: A controller describes itself

- **WHEN** a page asks a loaded controller what it is
- **THEN** it answers with its name, kind, profile and pad count without the page
  reading storage

#### Scenario: An older stored controller still loads

- **WHEN** a controller stored before a metadata field was introduced is loaded
- **THEN** it loads successfully with that field absent
- **AND** nothing rewrites it on read

### Requirement: Capability query

A controller SHALL be able to say which GM drum notes it can produce, and
whether it can produce a given one.

Where a lesson requires a drum the controller cannot produce — most commonly an
open hi-hat on a kit with no pedal — the resting lesson page SHALL say so before
the run starts. The lesson SHALL remain playable and the affected notes SHALL
score as they normally would rather than being silently excused.

#### Scenario: A no-pedal kit meets an open hi-hat

- **GIVEN** a controller whose hi-hat is a single voice
- **WHEN** a lesson containing open hi-hat notes is opened
- **THEN** the page states that this controller cannot play those notes
- **AND** the Play button remains available

#### Scenario: A fully capable controller says nothing

- **WHEN** the controller can produce every drum a lesson uses
- **THEN** no warning is shown

### Requirement: Persistence and registry

Loading and saving a controller SHALL go through the controller object, and no
other module SHALL read or write the stored configuration directly.

The system SHALL be able to list every controller configured on the device, so a
device chooser can name a controller and describe it rather than showing a bare
MIDI port name.

Persistence SHALL be non-throwing: a browser with storage blocked SHALL still
yield a usable in-memory controller for the session.

#### Scenario: A configured controller is recognised on return

- **WHEN** a student returns and selects a MIDI port they have configured before
- **THEN** the stored controller loads with its map, pedals, transport and kit
