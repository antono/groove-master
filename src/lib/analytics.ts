// Thin wrapper over the gtag.js tag loaded in app.html.
//
// Every call is a no-op unless the tag is actually there: it is absent during
// SSR and prerender, and an ad blocker removes it in the browser too. Nothing
// the app does should depend on an event landing, so this never throws and
// never returns anything to branch on.

import { browser } from "$app/environment";

type Params = Record<string, string | number | boolean>;

declare global {
  interface Window {
    gtag?: (command: "event", name: string, params?: Params) => void;
  }
}

function track(event: string, params?: Params) {
  if (!browser) return;
  try {
    window.gtag?.("event", event, params);
  } catch {
    // Analytics must never break a lesson.
  }
}

/** A run of a lesson has begun (the transport started, count-in included). */
export const lessonStarted = (lessonId: string) =>
  track("lesson_started", { lesson_id: lessonId });

/** A run played all the way to the end of the pattern and was scored. */
export const lessonFinished = (lessonId: string) =>
  track("lesson_finished", { lesson_id: lessonId });

/** The setup wizard was opened. */
export const onboardingStarted = () => track("onboarding_started");

/** The student reached a step of the wizard, forwards or back. */
export const onboardingStep = (step: string) =>
  track("onboarding_step", { step });

/** The wizard was carried through to its final screen. */
export const onboardingFinished = () => track("onboarding_finished");
