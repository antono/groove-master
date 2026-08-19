# controller-preview Specification

## Purpose

One picture of the student's instrument, drawn from the controller and reused
everywhere it helps: while mapping it in setup, beside the chart on a resting
lesson, and at full size during a run when there is room. It answers _where_,
while the chart and the highway answer _when_.

## Requirements

### Requirement: One renderer for every controller

The system SHALL render a controller's preview from the controller itself, so a
pad grid and a drum kit are drawn by the same component and no page chooses a
renderer.

The preview SHALL take its geometry from the controller: a grid's captured
rows and columns, a profiled kit's schematic, or the neutral arrangement for a
kit with no schematic.

A controller SHALL be previewable at any point after its pads exist, including
part-way through setup.

#### Scenario: A grid and a kit are drawn by the same component

- **WHEN** a pad-grid controller and a drum-kit controller are each previewed
- **THEN** both are rendered by the same component
- **AND** each is drawn in its own geometry, not the other's

#### Scenario: A kit without a schematic still draws

- **WHEN** a custom kit with no schematic is previewed
- **THEN** its pads are drawn in the neutral arrangement
- **AND** every mode behaves as it does for a profiled kit

### Requirement: Preview modes

The preview SHALL support three modes over the same geometry:

- **capture** — one pad marked as awaiting a press, captured pads showing their
  note, others pending; a captured pad may be activated to audition it.
- **map** — pads the current lesson uses named in their drum's family hue, the
  rest left blank so the picture keeps the shape of the real device.
- **play** — the same as map, sized for a run, with lesson names and hit
  feedback legible at a glance.

Switching mode SHALL NOT change the geometry, so a pad occupies the same place
in setup as it does during a lesson.

#### Scenario: Capture marks the pad awaiting a press

- **WHEN** setup is waiting for a particular pad
- **THEN** the preview marks that pad as current and the already-captured pads as
  done
- **AND** the pads not yet reached are shown pending

#### Scenario: Map names only the lesson's drums

- **WHEN** a lesson is open on the resting page
- **THEN** the pads that lesson uses are named in their drum's family hue
- **AND** the remaining pads are drawn blank rather than hidden

#### Scenario: A pad keeps its place across modes

- **WHEN** the same controller is previewed in capture and then in map mode
- **THEN** each pad is in the same position in both

### Requirement: Animated feedback

The preview SHALL animate what is happening on the instrument: a pad or drum
struck SHALL flare and settle, a pad awaiting capture SHALL pulse, and a
controller with a stateful hi-hat SHALL show the hi-hat's open or closed
position as the pedal moves.

All animation SHALL be suppressed under a reduced-motion preference, with the
same information still conveyed by colour and state.

Animation SHALL NOT be the mechanism by which state is understood: a screen
reader SHALL be given the same facts in text.

#### Scenario: A hit is visible on the preview

- **WHEN** the student strikes a mapped pad
- **THEN** that pad flares and settles in its drum's hue

#### Scenario: The pedal position is visible

- **GIVEN** a controller with a stateful hi-hat
- **WHEN** the student moves the hi-hat pedal
- **THEN** the preview shows the hi-hat as open or closed accordingly

#### Scenario: Reduced motion is respected

- **WHEN** the student prefers reduced motion
- **THEN** no pad animates
- **AND** hits, capture progress and pedal position remain distinguishable

#### Scenario: The preview is described in text

- **WHEN** the preview is reached by a screen reader
- **THEN** it conveys which drums this lesson uses and where they sit
- **AND** it does not rely on animation to do so

### Requirement: Preview during a run

While a lesson is being played, the preview SHALL be shown at its largest
comfortable size when there is room for it alongside the highway, and SHALL be
omitted when there is not.

The preview SHALL NEVER take space from the highway: the highway's size is
chosen first, and the preview occupies what remains.

The preview SHALL NOT degrade the smoothness of the scrolling highway.

#### Scenario: A short lesson leaves room

- **WHEN** a run is playing and the highway leaves enough room
- **THEN** the preview is shown alongside it at the largest size that fits

#### Scenario: A tall highway leaves none

- **WHEN** the highway occupies the available height
- **THEN** the preview is omitted
- **AND** the highway is unchanged in size and position

#### Scenario: Hits light during the run

- **WHEN** the student hits a mapped pad during a run
- **THEN** the preview lights that pad in step with the highway's own feedback
