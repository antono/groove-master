# layout-sharing Specification

## Purpose

Let a student who has just configured an unrecognised kit hand that layout back,
so it can become a shipped profile — as an explicit, optional favour that costs
them nothing and requires no account.

## Requirements

### Requirement: Opt-in submission

After a generic setup completes, the system SHALL offer to send the layout so
the kit can be added as a profile, and SHALL send nothing unless the student
acts on that offer.

The setup SHALL be complete and saved locally whether or not the layout is
shared, and a failed or refused submission SHALL never block or alter the local
result.

The offer SHALL state plainly what is sent before it is sent.

#### Scenario: Setup completes without sharing

- **WHEN** a student finishes a generic setup and ignores the offer
- **THEN** the layout is saved locally and the kit is ready to play
- **AND** nothing is transmitted

#### Scenario: A submission fails

- **WHEN** the student shares a layout and the request fails
- **THEN** the failure is reported without alarm
- **AND** the local layout is unaffected

#### Scenario: Sharing is offered once per setup

- **WHEN** a layout has been shared
- **THEN** the offer is not repeated for that same layout

### Requirement: What is sent

A submission SHALL carry only the kit's name and its layout — pad labels, roles,
captured notes, assigned sounds, and the hi-hat and pedal classification.

A submission SHALL NOT carry practice history, statistics, lesson progress, or
any identifier beyond the account id of a signed-in submitter.

#### Scenario: A signed-out student shares a layout

- **WHEN** a student with no account shares their layout
- **THEN** the submission is accepted
- **AND** it carries no identifier for that student

#### Scenario: A signed-in student shares a layout

- **WHEN** a signed-in student shares their layout
- **THEN** the submission records their account id
- **AND** still carries no practice data

### Requirement: Write-only storage

Submissions SHALL be stored in a table that clients may insert into but SHALL
NOT be able to read, list or modify — including the submitter's own rows.

The table SHALL bound what a single submission may contain, so that a malformed
or abusive insert is rejected at the database rather than stored.

Stored layouts SHALL NOT be read back into the app automatically; a shipped
profile is authored from them deliberately.

#### Scenario: A client cannot read the table

- **WHEN** any client, signed in or not, attempts to read submitted layouts
- **THEN** the request returns nothing

#### Scenario: An oversized submission is rejected

- **WHEN** a submission exceeds the permitted size
- **THEN** the database rejects it
- **AND** the student's local layout is unaffected

#### Scenario: Submissions do not become profiles on their own

- **WHEN** a layout has been submitted
- **THEN** no shipped profile changes until one is authored from it
