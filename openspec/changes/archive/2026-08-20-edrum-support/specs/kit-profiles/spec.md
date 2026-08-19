## Purpose

Describe an electronic drum kit to the app: which kits are recognised, how a
kit's schematic makes each drum addressable, and the vocabulary of drum roles a
pad can hold. A profile is the description of a model; what a particular
student's instrument turned out to be belongs to the controller.

## ADDED Requirements

### Requirement: Kit profile catalogue

The system SHALL ship a catalogue of electronic-kit profiles, each carrying a
stable id, a display label, a name pattern matched case-insensitively against
the MIDI input name, a schematic reference, and an ordered list of pads. A
profile SHALL be matched by the same entry point that matches grid presets, so
one lookup answers "what is this device" for both kinds.

A profile SHALL NOT declare a MIDI note for any pad. Pad notes are reassignable
from a module's own front panel and are therefore never a property of the model.

#### Scenario: A recognised kit is identified from its port name

- **WHEN** a MIDI input whose name matches a profile's pattern is selected
- **THEN** that profile is returned, carrying its schematic and pad list
- **AND** no pad in it asserts a MIDI note

#### Scenario: An unrecognised device falls through unchanged

- **WHEN** a MIDI input matches no kit profile and no grid preset
- **THEN** the lookup returns nothing
- **AND** the device remains fully configurable through the generic path

### Requirement: Addressable schematic

Each profile SHALL reference a schematic SVG in which every drum is an element
whose id equals the corresponding pad's id, so a single renderer can mark any
drum as pending, captured, or lit without per-kit code.

Schematics SHALL be loaded only from first-party assets shipped with the app.
Externally supplied or user-submitted content SHALL NEVER be rendered as a
schematic.

#### Scenario: A drum is highlighted by id

- **WHEN** a component asks the renderer to light the pad with a given id
- **THEN** the matching element in that kit's schematic is marked as lit
- **AND** no other drum's appearance changes

#### Scenario: Profile and schematic are checked against each other

- **WHEN** the project is built
- **THEN** every pad id in every profile is verified to exist in that profile's
  schematic
- **AND** a profile whose ids have drifted from its picture fails the build

### Requirement: Drum roles

The system SHALL define a closed vocabulary of drum roles covering at least
kick, snare, tom, hi-hat, crash and ride, and each profile pad SHALL declare one
role and a suggested GM percussion note.

The suggested note SHALL be editable by the student; the role SHALL be what
pedal handling and playability checks reason about, so a kit whose hi-hat is
assigned an unusual sound is still understood to have a hi-hat.

#### Scenario: A suggested sound is changed without losing the role

- **WHEN** a student assigns a different GM note to a pad whose role is hi-hat
- **THEN** the pad's sound changes
- **AND** the pad is still treated as the kit's hi-hat by pedal handling

### Requirement: A profile builds a controller

A profile SHALL be the template from which a drum-kit controller is built: its
pads become the controller's pads, its schematic becomes the controller's
preview geometry, and its suggested sounds become the controller's starting
sounds.

A profile SHALL hold no student-specific state. Captured notes, pedal
classification and edited sounds belong to the controller, so the same profile
serves every student who owns that model.

#### Scenario: Two students share one profile

- **WHEN** two students configure the same model and map its pads differently
- **THEN** both controllers reference the same profile
- **AND** neither student's captured notes appear in the other's controller

#### Scenario: A profile change reaches existing controllers safely

- **WHEN** a shipped profile's label or schematic is corrected
- **THEN** controllers built from it show the correction
- **AND** their captured notes, sounds and pedal settings are unaffected
