# quote-ratings Specification

## Purpose

TBD - created by archiving change quote-of-the-day. Update Purpose after archive.

## Requirements

### Requirement: Offline-first rating capture

The system SHALL record a user's like or dislike of a quote to device-local
storage immediately, with no dependency on a network connection or an account.
Each quote SHALL carry at most one current rating per user; re-rating replaces
the previous value.

#### Scenario: Rating recorded while signed out or offline

- **WHEN** a signed-out or offline user likes or dislikes a quote
- **THEN** the rating is written to device-local storage immediately
- **AND** it is queued to sync when the user is signed in and online

#### Scenario: Re-rating replaces the previous value

- **WHEN** a user changes a quote's rating from like to dislike (or clears it)
- **THEN** the quote's current rating reflects the latest choice only
- **AND** the quote never carries two conflicting ratings for that user

### Requirement: Owner-scoped rating storage

The system SHALL persist ratings for signed-in users in a Supabase table where
every row is owned by a Supabase user, and row-level security MUST restrict all
reads and writes to rows owned by the requesting user (`auth.uid()`). A rating
row SHALL identify the quote by its stable quote id and record the like/dislike
value.

#### Scenario: A user cannot read another user's ratings

- **WHEN** an authenticated user queries quote ratings
- **THEN** only rows owned by that user are returned

#### Scenario: A user cannot write ratings for another user

- **WHEN** an authenticated user inserts or updates a rating row
- **THEN** the row is accepted only if it is owned by that user
- **AND** an attempt to write a row owned by another user is rejected

#### Scenario: Unauthenticated database access is denied

- **WHEN** a request reaches the ratings table without an authenticated session
- **THEN** no rating rows are readable or writable

### Requirement: Rating synchronization

For a signed-in user, the system SHALL synchronize quote ratings between the
device and Supabase in the background without blocking the interstitial or
navigation, and MUST NOT lose a rating if a sync attempt fails.

#### Scenario: Rating syncs after being recorded

- **WHEN** a signed-in, online user rates a quote
- **THEN** the rating is written locally and pushed to Supabase
- **AND** navigation to the next lesson is not blocked by the sync

#### Scenario: Sync failure keeps the rating queued

- **WHEN** a sync attempt fails (offline, error, or permission denied)
- **THEN** the local rating is retained
- **AND** it remains queued for a later attempt

#### Scenario: Ratings converge to one value per quote

- **WHEN** the same quote has a local rating and a remote rating for the same
  user
- **THEN** after sync both device and cloud hold a single agreed current value

### Requirement: First-login adoption of local ratings

On a user's first sign-in on a device, the system SHALL adopt existing
device-local quote ratings into that account rather than discarding them.

#### Scenario: Existing local ratings are claimed

- **WHEN** a user with pre-existing device-local ratings signs in for the first
  time
- **THEN** those ratings are uploaded and associated with the account
- **AND** no pre-existing local rating is lost
