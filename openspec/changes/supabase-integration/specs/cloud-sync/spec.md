## ADDED Requirements

### Requirement: Owner-scoped cloud schema

The system SHALL persist lesson progress and run stats in Supabase tables where
every row is owned by a Supabase user, and row-level security MUST restrict all
reads and writes to rows owned by the requesting user (`auth.uid()`).

- Progress SHALL be stored per user and per lesson, capturing the unlocked BPM
  ceiling and the selected tier, plus the set of unlocked lessons.
- Run stats SHALL be stored one row per finished run, mirroring the local
  `SessionStat` shape, and each run SHALL carry a stable client-generated
  identifier used for de-duplication.

#### Scenario: A user cannot read another user's rows

- **WHEN** an authenticated user queries progress or stats
- **THEN** only rows owned by that user are returned
- **AND** rows owned by any other user are never returned

#### Scenario: A user cannot write rows for another user

- **WHEN** an authenticated user inserts or updates a progress or stats row
- **THEN** the row is accepted only if it is owned by that user
- **AND** an attempt to write a row owned by another user is rejected

#### Scenario: Unauthenticated access is denied at the database

- **WHEN** a request reaches the tables without an authenticated Supabase session
- **THEN** no progress or stats rows are readable or writable

### Requirement: Offline-first local source of truth

The system SHALL keep `localStorage` (progress) and `IndexedDB` (stats) as the
local source of truth. Reads, playback, unlocking, and stat recording MUST
succeed with no network and no account.

#### Scenario: Recording a run offline

- **WHEN** a user finishes a run while offline or signed out
- **THEN** the run is written to the local `sessions` store as it is today
- **AND** it is queued for upload if and when the user is signed in and online

#### Scenario: Progress updates offline

- **WHEN** a user clears a rung and unlocks a higher BPM ceiling while offline
- **THEN** the new ceiling and any newly unlocked lesson are persisted locally
- **AND** are queued to sync when possible

### Requirement: Background synchronization

For a signed-in user, the system SHALL synchronize progress and stats between
the device and Supabase in the background, pushing local changes up and pulling
remote changes down without blocking playback.

#### Scenario: Push local changes after sign-in

- **WHEN** a user signs in with local data that is newer than the cloud
- **THEN** the local progress and any un-uploaded runs are pushed to Supabase

#### Scenario: Pull remote changes to a fresh device

- **WHEN** a user signs in on a device with no local data
- **THEN** their cloud progress and stats are pulled down and made available
  locally

#### Scenario: Sync failures do not disrupt use

- **WHEN** a sync attempt fails (offline, error, or permission denied)
- **THEN** the app continues to function on local data
- **AND** the pending changes remain queued for a later attempt

#### Scenario: Sync status is visible

- **WHEN** a sync is pending, in progress, or failed
- **THEN** the UI surfaces a lightweight indicator of the current sync state

### Requirement: Deterministic progress merge

When merging progress between device and cloud, the system SHALL take the
highest BPM ceiling per lesson and the union of unlocked lessons, so that merges
never regress a user's progress.

#### Scenario: Higher ceiling wins

- **WHEN** the local ceiling for a lesson is 100 and the cloud ceiling is 80
- **THEN** the merged ceiling for that lesson is 100 on both device and cloud

#### Scenario: Unlocked lessons are unioned

- **WHEN** the device has unlocked lesson A and the cloud has unlocked lesson B
- **THEN** after merge both A and B are unlocked on device and cloud

#### Scenario: Merge is idempotent

- **WHEN** a merge runs repeatedly with no new local or remote changes
- **THEN** the resulting progress is unchanged after the first merge

### Requirement: Append-only, de-duplicated stats

The system SHALL treat run stats as append-only and MUST NOT count the same run
twice, using each run's stable client-generated identifier to de-duplicate
across device and cloud.

#### Scenario: A run uploads exactly once

- **WHEN** a locally recorded run is pushed to the cloud and the device later
  re-syncs
- **THEN** the run appears exactly once in the cloud
- **AND** exactly once in the merged history shown on the stats page

#### Scenario: Merged history combines both sources

- **WHEN** the stats page loads for a signed-in user
- **THEN** it shows the union of local and cloud runs with no duplicates
- **AND** aggregation by calendar day reflects every distinct run once

### Requirement: First-login adoption of local data

On a user's first sign-in on a device, the system SHALL adopt existing
device-local progress and stats into that account rather than discarding them.

#### Scenario: Existing local data is claimed

- **WHEN** a user with pre-existing local progress and runs signs in for the
  first time
- **THEN** that local progress and those runs are uploaded and associated with
  the account
- **AND** no pre-existing local data is lost
