## Purpose

Makes Groove Academy installable to the home screen of the device a student
actually drums on, and makes the installed copy a real app: it launches without
a network, opens straight into the lesson they were on, and has the sounds it
needs already on the machine.

## ADDED Requirements

### Requirement: Web app manifest

The site SHALL publish a web app manifest, linked from every page, that declares
the application's name, a short name for a home-screen label, a start URL, a
navigation scope covering the whole site, a standalone display mode, and
background and theme colours. The site SHALL also declare a theme colour to the
browser, matching the active colour scheme.

#### Scenario: The manifest is served and linked

- **WHEN** any page of the site is loaded
- **THEN** it links a web app manifest that the browser fetches and parses without error

#### Scenario: The browser offers installation

- **WHEN** the site is opened in a browser that supports installation
- **THEN** the browser reports the site as installable

#### Scenario: Launching runs standalone

- **WHEN** the installed app is launched from the home screen
- **THEN** it opens without browser navigation chrome, at the start URL

#### Scenario: Theme colour follows the colour scheme

- **WHEN** the device is set to dark and to light appearance in turn
- **THEN** the declared theme colour matches the scheme in use

### Requirement: Application icons

The manifest SHALL declare an icon set sufficient for installation on desktop
and mobile, including at least 192px and 512px square icons and a maskable
variant that survives being cropped to a circle or a squircle without losing the
mark. Icons SHALL be generated from the existing brand mark rather than drawn
separately, so the installed icon and the site's favicon cannot drift apart.

#### Scenario: Icons cover the required sizes

- **WHEN** the manifest is validated
- **THEN** it declares at least a 192px and a 512px icon, and at least one maskable icon

#### Scenario: A masked icon keeps the mark

- **WHEN** the maskable icon is cropped to a circle
- **THEN** the brand mark remains complete and centred within the crop

### Requirement: App shortcuts

The manifest SHALL declare shortcuts, reachable from the installed icon's
context menu, for **Continue lesson**, **Stats** and **News**. Each shortcut
SHALL name its destination in the student's terms and SHALL resolve to a working
page when activated, including on a first launch with no practice history.

#### Scenario: Shortcuts are offered on the installed icon

- **WHEN** the student opens the context menu of the installed app icon
- **THEN** it offers Continue lesson, Stats and News

#### Scenario: A shortcut opens its destination

- **WHEN** the student activates any of the three shortcuts
- **THEN** the app opens on that destination

#### Scenario: Continue works before any practice

- **WHEN** the Continue lesson shortcut is activated on a device with no practice history
- **THEN** the app opens on a lesson rather than an error

### Requirement: Offline launch

The installed app SHALL open when the device has no network connection, showing
the application rather than a browser error page. The app's primary routes — the
catalogue and the pages reachable from the navigation — SHALL be available
offline. A navigation to a route that has neither been visited nor precached
SHALL be answered with an in-app offline page that keeps the navigation usable,
never the browser's error page.

#### Scenario: Launching with no network shows the app

- **WHEN** the installed app is launched with the network unavailable
- **THEN** the application is shown and can be navigated

#### Scenario: Primary routes work offline

- **WHEN** the app is offline and the student navigates to the catalogue, statistics or news
- **THEN** each page renders

#### Scenario: An unreachable route falls back to an in-app page

- **WHEN** an offline navigation targets a route that was never visited or precached
- **THEN** an in-app offline page is shown, from which the student can navigate to a page that is available

### Requirement: Precaching on install

Installation of the app SHALL trigger a background download of the audio and
lesson data the app needs to work offline: the student's currently configured
drum kit, the backing bass samples, the lesson manifest and the lesson MIDIs.
Kits the student has not selected SHALL NOT be downloaded. This SHALL be
triggered by the application being installed, and SHALL NOT be triggered merely
by a first visit from a browser where the app is not installed.

#### Scenario: Installing fetches the offline set

- **WHEN** the app is installed
- **THEN** the configured kit's samples, the basses, the lesson manifest and the lesson MIDIs are fetched into the cache

#### Scenario: Unselected kits are left alone

- **WHEN** the precache completes
- **THEN** no samples belonging to a kit other than the configured one have been downloaded

#### Scenario: A visit without installing downloads nothing extra

- **WHEN** a visitor opens the site in a browser and does not install it
- **THEN** only the existing warm-on-idle behaviour fetches audio

#### Scenario: A lesson plays with no network

- **WHEN** the precache has completed and the device is taken offline
- **THEN** a lesson can be opened, played and scored with its drum and backing sounds

### Requirement: Precache is resumable and repeatable

The precache SHALL run in the background without blocking use of the app, SHALL
report its progress, SHALL skip anything already cached, and SHALL be safe to
interrupt and re-run — a partially completed precache SHALL be completed by the
next run rather than restarted. It SHALL be re-triggerable rather than
once-ever, so that an emptied cache can be refilled by the installed app.

#### Scenario: Practising during the precache is unaffected

- **WHEN** the precache is running
- **THEN** the student can navigate and play lessons, and progress is shown

#### Scenario: Interrupting and resuming

- **WHEN** the precache is interrupted by going offline or closing the app, and later runs again
- **THEN** it fetches only what is still missing

#### Scenario: Refilling an emptied cache

- **WHEN** the sample cache has been dropped and the installed app is opened
- **THEN** the offline set can be fetched again without reinstalling the app

### Requirement: Lesson data stays fresh when online

The lesson manifest and lesson MIDIs SHALL be served from the network when the
network is available, with the cached copy used only as an offline fallback. A
precached lesson SHALL NOT prevent an edited pattern from reaching the student.

#### Scenario: An edited lesson reaches a returning student

- **WHEN** a lesson's MIDI has been re-rendered and the student opens that lesson online
- **THEN** the new pattern is played

#### Scenario: The cached copy answers offline

- **WHEN** the student opens a lesson with no network
- **THEN** the precached manifest and MIDI are used

### Requirement: In-app install affordance

Where the browser exposes an installation prompt to the page, the app SHALL
offer an install affordance. It SHALL be dismissible, SHALL stay dismissed, and
SHALL NOT be shown when the app is already installed or when the browser exposes
no prompt.

#### Scenario: The affordance appears where installation is possible

- **WHEN** the browser signals that the app can be installed
- **THEN** an install affordance is shown

#### Scenario: Dismissal is remembered

- **WHEN** the student dismisses the affordance
- **THEN** it is not shown again on that device

#### Scenario: Nothing is offered once installed

- **WHEN** the app is running as an installed application
- **THEN** no install affordance is shown

### Requirement: Install analytics

The install funnel SHALL be recorded as analytics events: the affordance being
offered, the outcome of the installation prompt as accepted or dismissed, and
the application being installed. The installed event SHALL be recorded however
the installation was performed, including through the browser's own menu without
the in-app affordance. Recording SHALL be best-effort: a blocked or absent
analytics tag SHALL NOT affect installation or any other behaviour.

#### Scenario: Offering the affordance is recorded

- **WHEN** the install affordance is shown
- **THEN** an event recording that it was offered is sent

#### Scenario: The prompt's outcome is recorded

- **WHEN** the student accepts or dismisses the installation prompt
- **THEN** an event recording that outcome is sent

#### Scenario: Installation is recorded whatever its route

- **WHEN** the app is installed through the browser's own menu, without the in-app affordance
- **THEN** an installed event is still sent

#### Scenario: A blocked analytics tag changes nothing

- **WHEN** the analytics tag is absent or blocked
- **THEN** installation, the affordance and the precache behave exactly as they otherwise would
