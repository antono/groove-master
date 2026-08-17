## MODIFIED Requirements

### Requirement: Continue shortcut

The landing SHALL offer a shortcut that takes the student directly to their next
lesson without drilling through the hierarchy. The target SHALL be the first
written, non-`planned` lesson in curriculum order that the history does not mark
cleared; if every written lesson is cleared, it SHALL be the last written lesson.

That target SHALL additionally be reachable at a stable URL, `/lessons/continue`,
which resolves it and takes the student to that lesson. The URL exists so that a
destination fixed in advance — an installed app's shortcut, a bookmark, a shared
link — can point at "my next lesson" even though the target is derived from
practice history held on the device. The landing's shortcut and the URL SHALL
resolve to the same lesson, so there is one definition of continuing.

Resolution SHALL happen on the device that holds the history. Where the target
cannot be resolved — the catalogue is unavailable — the student SHALL be taken
to the catalogue landing rather than shown an error.

#### Scenario: Continue jumps to the next uncleared lesson

- **WHEN** a student activates the continue shortcut on the landing
- **THEN** they navigate straight to the first written lesson in curriculum order not marked cleared

#### Scenario: Continue with no history

- **WHEN** there is no practice history
- **THEN** the continue shortcut targets the first written lesson

#### Scenario: The continue URL resolves to the same lesson

- **WHEN** a student opens `/lessons/continue`
- **THEN** they arrive at the same lesson the landing's continue shortcut would have taken them to

#### Scenario: The continue URL with no history

- **WHEN** a student opens `/lessons/continue` on a device with no practice history
- **THEN** they arrive at the first written lesson

#### Scenario: The continue URL when the catalogue cannot be read

- **WHEN** `/lessons/continue` is opened and the catalogue cannot be loaded
- **THEN** the student arrives at the catalogue landing rather than an error page

#### Scenario: Continue does not accumulate in history

- **WHEN** a student opens `/lessons/continue` and then goes back
- **THEN** they return to where they came from rather than to the resolver

### Requirement: Reserved navigation slugs

The lesson generator SHALL reject `tier`, `stage` and `continue` as lesson
slugs, so the static navigation routes can never be shadowed by a lesson at
`/lessons/<slug>`.

#### Scenario: A lesson slug cannot collide with a route segment

- **WHEN** a lesson is defined with the slug `tier`, `stage` or `continue`
- **THEN** generation fails with an error naming the reserved slug
