## ADDED Requirements

### Requirement: Sync coverage for all local data

The app SHALL provide a registered sync routine for every dataset it persists on
the device (`localStorage` or `IndexedDB`), each with a documented merge strategy
and an explicit pull-back decision (whether remote data flows to a fresh device).
Introducing a new locally-persisted dataset SHALL include its sync routine; a
dataset that is intentionally device-only SHALL be recorded as such.

#### Scenario: An existing local dataset is covered

- **WHEN** reconcile runs for a signed-in user
- **THEN** every synced dataset (progress, stats, quote ratings) is pushed to
  Supabase and, where its pull-back decision is yes, pulled back to the device

#### Scenario: A new local dataset registers a sync routine

- **WHEN** a feature is added that persists a new dataset locally
- **THEN** it registers a sync routine with a defined merge strategy and pull-back
  decision, rather than remaining device-only by omission

#### Scenario: Signed-out use is unaffected

- **WHEN** no user is signed in
- **THEN** all datasets remain device-local and no sync routine runs

### Requirement: Fault-isolated reconcile

Reconcile SHALL sync each registered dataset independently, so that one dataset
failing — a table not yet provisioned, a transient error, or a permission denial
— neither aborts nor hides the sync of the others. The datasets that succeed
SHALL persist their results; the overall status SHALL reflect that a failure
occurred so it is retried, without discarding the successful work.

#### Scenario: One dataset failing does not block the others

- **WHEN** one dataset's sync throws during a reconcile
- **THEN** the other datasets still complete their push/pull
- **AND** the failed dataset stays queued for the next reconcile

#### Scenario: Status reflects a partial failure

- **WHEN** at least one dataset fails and at least one succeeds in the same run
- **THEN** the sync status is reported as failed (retry pending)
- **AND** the successful datasets' results are not rolled back

#### Scenario: All datasets succeed

- **WHEN** every dataset syncs without error
- **THEN** the sync status is reported as idle/synced
