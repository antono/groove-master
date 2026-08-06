## ADDED Requirements

### Requirement: Optional passwordless sign-in

The system SHALL allow a user to sign in with an email magic link via Supabase
Auth. Authentication MUST be optional: an unauthenticated user retains full
access to lessons, playback, and device-local progress and stats.

#### Scenario: Request a magic link

- **WHEN** a signed-out user submits a valid email address in the sign-in form
- **THEN** the system requests a magic link from Supabase Auth for that email
- **AND** shows a confirmation that a link has been sent

#### Scenario: Complete sign-in from the link

- **WHEN** the user opens the magic link from their email
- **THEN** the system establishes an authenticated Supabase session
- **AND** the UI reflects the signed-in state (the user's email is shown)

#### Scenario: Invalid email is rejected

- **WHEN** a user submits an input that is not a valid email address
- **THEN** the system does not request a magic link
- **AND** shows a validation message

#### Scenario: Unauthenticated use is unaffected

- **WHEN** a user has never signed in
- **THEN** all lessons, playback, progress, and stats behave exactly as they do
  today, backed by device-local storage only

### Requirement: Session persistence

The system SHALL persist an authenticated session across page reloads and app
restarts until the user signs out or the session expires.

#### Scenario: Session survives reload

- **WHEN** a signed-in user reloads the app
- **THEN** the user remains signed in without re-entering their email

#### Scenario: SSR renders the correct auth state

- **WHEN** any page is server-rendered for a request that carries a valid
  Supabase session cookie
- **THEN** the server resolves the authenticated user before rendering
- **AND** the client hydrates in the same signed-in state without a flash of
  signed-out UI

#### Scenario: Expired or missing session falls back to signed-out

- **WHEN** a request carries no valid Supabase session
- **THEN** the app renders in the signed-out, device-local mode

### Requirement: Sign out

The system SHALL allow a signed-in user to sign out, ending the Supabase
session while leaving device-local data intact.

#### Scenario: User signs out

- **WHEN** a signed-in user chooses to sign out
- **THEN** the Supabase session is terminated on both client and server
- **AND** the UI returns to the signed-out state
- **AND** device-local progress and stats remain available for offline use
