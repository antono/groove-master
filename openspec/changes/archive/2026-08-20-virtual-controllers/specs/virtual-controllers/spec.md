## Purpose

Lets a student play and score a lesson using a computer keyboard or an on-screen
touch pad grid, so the app is playable with no MIDI hardware and on devices that
have no Web MIDI at all.

## ADDED Requirements

### Requirement: Virtual input sources are selectable

The system SHALL offer a computer keyboard and an on-screen touch pad grid as
input sources for playing a lesson, listed alongside any connected Web MIDI
ports. The student SHALL be able to select one of them as the active input, and
the selection SHALL persist across sessions the same way a chosen Web MIDI device
does.

#### Scenario: Virtual sources listed with hardware

- **WHEN** the student opens the input/device selection with or without a Web MIDI controller connected
- **THEN** the keyboard and on-screen touch pads appear as selectable sources in addition to any connected Web MIDI ports

#### Scenario: No hardware and no Web MIDI support

- **WHEN** the browser has no Web MIDI support, or no controller is connected
- **THEN** the app still reaches a state where a lesson can be played, because at least one virtual source is available and selectable

#### Scenario: Selection persists

- **WHEN** the student selects a virtual source and later reopens the app
- **THEN** that virtual source is the active input again without reselecting it

### Requirement: Keyboard plays a lesson

The system SHALL map computer-keyboard keys to pads using a built-in default
layout, so that pressing a mapped key while the keyboard source is active
produces a drum hit that is scored identically to a MIDI hit. Auto-repeat from a
held key SHALL NOT produce additional hits.

#### Scenario: Key press scores a hit

- **WHEN** the keyboard source is active during a scored run and the student presses a mapped key
- **THEN** the corresponding pad's drum sounds and the hit is scored against the lesson's timing windows exactly as a MIDI hit would be, contributing to the result report and per-pad breakdown

#### Scenario: Unmapped key is ignored

- **WHEN** the student presses a key that is not in the layout
- **THEN** no drum sounds and nothing is scored

#### Scenario: Held key does not repeat

- **WHEN** the student holds a mapped key down past the keyboard auto-repeat threshold
- **THEN** exactly one hit is produced, not a stream of repeats

### Requirement: On-screen touch pads play a lesson

The system SHALL present an on-screen pad grid, sized for touch, that produces a
scored drum hit when a pad is tapped while the touch source is active. A tap
SHALL be scored identically to a MIDI hit.

#### Scenario: Tap scores a hit

- **WHEN** the touch source is active during a scored run and the student taps a pad
- **THEN** that pad's drum sounds and the hit is scored against the lesson's timing windows exactly as a MIDI hit would be

#### Scenario: Playable on a touchscreen with no Web MIDI

- **WHEN** the student is on a phone or tablet with no Web MIDI support
- **THEN** the on-screen pads are available and a lesson can be played to its result screen

### Requirement: Each virtual source has its own editable mapping

Each virtual source SHALL carry its own pad-to-GM-drum mapping, defaulting to a
sensible built-in layout and editable by the student. Because a virtual source
emits no controller note to capture, its mapping SHALL be chosen or edited
directly rather than learned from hardware, and edits SHALL persist across
sessions.

#### Scenario: Default mapping is usable immediately

- **WHEN** a virtual source is used for the first time with no prior configuration
- **THEN** it already has a complete default pad-to-drum mapping and can play a lesson without any setup

#### Scenario: Edited mapping persists

- **WHEN** the student changes which drum a pad triggers for a virtual source
- **THEN** the new mapping is used for that source and is retained when the app is reopened

### Requirement: Keyboard transport hotkeys

The system SHALL let the student start or resume, and stop or pause, a lesson run
from the keyboard while the keyboard source is active, so a keyboard-only student
can run a lesson end to end without hardware transport controls. The on-screen
touch controller SHALL rely on its existing visible start/pause controls and
requires no additional transport binding.

#### Scenario: Start and resume from the keyboard

- **WHEN** the keyboard source is active and the lesson is at rest or paused, and the student presses the transport start hotkey
- **THEN** the run starts, or resumes from where it was paused

#### Scenario: Stop and pause from the keyboard

- **WHEN** a run is in progress and the student presses the transport stop hotkey
- **THEN** the run pauses, and a subsequent stop press ends the run, matching how a hardware Stop button behaves

### Requirement: Virtual runs are attributed in practice stats

A scored run played on a virtual source SHALL be recorded in practice stats with
a stable identity for that source, so the run is attributed to the keyboard or
the touch pads rather than recorded as having no controller.

#### Scenario: Keyboard run is attributed

- **WHEN** a lesson is played to the result screen with the keyboard source active
- **THEN** the recorded session identifies the keyboard as the controller, distinct from `null` and from any Web MIDI device

#### Scenario: Touch run is attributed

- **WHEN** a lesson is played to the result screen with the touch source active
- **THEN** the recorded session identifies the on-screen touch pads as the controller, distinct from the keyboard and from any Web MIDI device
