# edrum-setup Specification

## Purpose

The setup wizard's second path: everything after a device is chosen, when that
device is an electronic drum kit rather than a grid of pads. Covers detection
and override, capture on the kit's own picture, pedal discovery, the test step,
and the generic flow for a kit no profile describes.

## Requirements

### Requirement: Branch after the device step

The wizard SHALL share its first two steps — connecting and choosing a device —
between both kinds of controller, and SHALL branch at the third step into either
the grid path or the drum path.

The grid path SHALL be unchanged in step order, wording and behaviour.

The progress rail SHALL show the steps of the active path only, so the number of
steps displayed always matches the number the student will walk.

#### Scenario: A grid controller keeps today's flow

- **WHEN** a student selects a device that matches a grid preset or nothing at all
- **THEN** the third step is the grid size picker as it is today
- **AND** the rail shows the grid path's steps

#### Scenario: Going back re-opens the choice

- **WHEN** a student on the drum path returns to the device step
- **THEN** the path selection is discarded
- **AND** choosing a device selects a path afresh

### Requirement: Detected kit with an override

When the selected device matches a kit profile, the wizard SHALL open the drum
path with that profile's schematic already displayed and its name stated.

The student SHALL be able to reject the detection at that point and choose any
other shipped profile, or the generic path, without returning to the device step.

#### Scenario: A recognised kit opens on its own picture

- **WHEN** a device matching a kit profile is selected
- **THEN** the third step shows that kit's schematic and names the kit
- **AND** it offers to choose a different layout

#### Scenario: The detection is wrong

- **WHEN** the student says the detected kit is not theirs
- **THEN** they can pick another profile or the generic path in place
- **AND** the wizard continues from the third step without losing the device

### Requirement: Capture drums on the schematic

The drum path SHALL capture one drum at a time by highlighting it on the
schematic and recording the next distinct note received, marking it captured and
advancing to the next drum.

Repeated note-on messages from a single strike SHALL NOT be recorded as separate
drums.

The student SHALL be able to skip a drum, re-record any already-captured drum,
and restart the capture, without leaving the step.

A drum that is skipped SHALL be left unmapped rather than assigned a placeholder
note.

#### Scenario: A kit is mapped drum by drum

- **WHEN** the student hits the pad for the highlighted drum
- **THEN** that drum's note is recorded and the drum is marked captured on the
  schematic
- **AND** the next drum is highlighted

#### Scenario: A pad the kit does not have is skipped

- **WHEN** the student skips the highlighted drum
- **THEN** that drum is left unmapped
- **AND** the layout is saved with the remaining drums intact

#### Scenario: One strike is one capture

- **WHEN** a pad sends more than one note-on for a single strike
- **THEN** only one drum is captured

### Requirement: Pedal discovery

The drum path SHALL include a pedals step that determines how the kit's hi-hat
behaves by observing three gestures: the pedal alone, the hi-hat struck with the
pedal open, and the hi-hat struck with the pedal closed.

From those observations the system SHALL classify the hi-hat as one of:

- **two notes** — open and closed strikes send different notes, needing no
  pedal state;
- **stateful** — both strikes send the same note and the pedal emits a message
  of its own, which is recorded so pedal position can be tracked;
- **none** — the pedal emits nothing usable, and the hi-hat is a single voice.

Where the two-note form is observed it SHALL be preferred, because it needs no
state to be correct.

The step SHALL also capture the **bass pedal**, ahead of the hi-hat. Pads that
arrive via a footswitch jack SHALL NOT appear in the drum-capture loop: that loop
asks the student to hit the drum lit on the picture, which a foot does not do,
and it left the bass pedal with nowhere to be skipped.

**Every pedal SHALL be skippable on its own, and the step as a whole SHALL be
skippable.** Owning the module without the footswitches is ordinary, and each
pedal is independent of the other. Skipping the bass pedal SHALL leave the kick
unmapped rather than guessed at; skipping the hi-hat gestures SHALL leave a
single-voice hat. Either way the rest of the setup SHALL be complete and usable.

What was skipped SHALL be stated rather than left blank, so a kick that will
never sound is known before a lesson rather than during one.

#### Scenario: A kit with no bass pedal

- **WHEN** the student skips the bass pedal
- **THEN** the kick is left unmapped
- **AND** the setup completes and every other drum still plays
- **AND** the step says the kick will not sound

#### Scenario: A kit with a bass pedal but no hi-hat pedal

- **WHEN** the student captures the bass pedal and skips the hi-hat gestures
- **THEN** the kick is mapped and the hi-hat is classified as a single voice
- **AND** both outcomes are stated together

#### Scenario: Feet are not asked for by hand

- **WHEN** the drum-capture loop runs on a kit with a footswitch-driven kick
- **THEN** that kick is not one of the drums it asks the student to hit

#### Scenario: A kit sending two hi-hat notes

- **WHEN** the open and closed strikes are observed to send different notes
- **THEN** the hi-hat is classified as two notes
- **AND** the open note is assigned the open hi-hat sound and the closed note the
  closed one

#### Scenario: A kit with a stateful pedal

- **WHEN** both strikes send the same note and the pedal emits its own message
- **THEN** the hi-hat is classified as stateful
- **AND** the pedal's message is recorded so its position can be tracked at play
  time

#### Scenario: No pedal connected

- **WHEN** the pedal emits nothing during the step
- **THEN** the hi-hat is classified as a single voice
- **AND** the student is told which hi-hat sound it will play

#### Scenario: The whole step is skipped

- **WHEN** the student skips the pedals step outright
- **THEN** setup completes with a single-voice hi-hat and no kick pedal
- **AND** the student can return to the step later without re-mapping the pads

### Requirement: A known controller is checked, not re-mapped

Where the selected device already has a stored controller with mapped pads, the
wizard SHALL load it and go straight to the test step, skipping layout and
capture entirely. Pressing every pad again to arrive back where you started is a
chore, not a setup.

The test step SHALL then name both the pad struck and the drum it plays, and
sound that drum, so the mapping can be checked rather than merely seen.

Re-mapping SHALL be available from there, and SHALL drop into the full path for
whatever kind of instrument it is. A re-map SHALL preserve everything except the
captured notes, so edited sounds, labels and a correct hi-hat classification
survive it.

#### Scenario: A previously configured controller is reconnected

- **WHEN** the student selects a device this machine has already been set up
  against
- **THEN** the wizard opens the test step with the stored mapping loaded
- **AND** no layout or capture step is shown

#### Scenario: The check names what each pad plays

- **WHEN** the student strikes a mapped pad on the test step
- **THEN** the pad and the drum it plays are both named, and that drum sounds

#### Scenario: Re-mapping from the check

- **WHEN** the student chooses to re-map from the test step
- **THEN** the full capture path for that kind of instrument is entered
- **AND** sounds, labels and pedal settings are retained while notes are cleared

#### Scenario: A half-finished setup is not treated as known

- **WHEN** a stored controller has no mapped pads
- **THEN** the wizard routes into layout and capture as it would for a new device

### Requirement: Test step

The drum path SHALL include a test step in which the student plays freely and
every recognised hit lights its drum on the schematic and names it.

A hit whose note is not mapped SHALL be reported as unmapped rather than
ignored silently, so a missed pad is visible.

The step SHALL offer a direct return to the drum capture and to the pedals step,
so a wrong assignment can be corrected where it is discovered.

#### Scenario: A mapped drum is confirmed

- **WHEN** the student hits a mapped pad
- **THEN** the matching drum lights on the schematic and its name is shown

#### Scenario: An unmapped pad is surfaced

- **WHEN** the student hits a pad that was skipped or never captured
- **THEN** the test step reports an unmapped hit rather than showing nothing

#### Scenario: A wrong assignment is corrected in place

- **WHEN** the student sees the wrong drum light up
- **THEN** they can return to capture or pedals from the test step
- **AND** on returning, the drums already correct are still captured

### Requirement: Generic kit setup

For a kit with no matching profile the wizard SHALL offer a generic drum path in
which the student states the kit's name and how many pads it has, then labels and
captures each pad with a drum role.

The generic path SHALL produce a controller of the same shape and completeness
as a profiled one, and SHALL support the pedals and test steps in the same way.

Where no schematic exists, the wizard SHALL present the pads in a neutral
arrangement rather than refusing to continue.

#### Scenario: An unlisted kit is fully configured

- **WHEN** a student completes the generic path for a kit with no profile
- **THEN** the saved controller carries every pad's label, role, note and sound
- **AND** lessons play on it exactly as they would on a profiled kit

#### Scenario: Pedals and test are available without a profile

- **WHEN** a generic setup reaches the pedals and test steps
- **THEN** both behave as they do for a profiled kit
- **AND** the test step lights the pads in their neutral arrangement
