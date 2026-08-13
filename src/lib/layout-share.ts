// Opt-in submission of a custom controller layout, so a kit we don't recognise
// can become a shipped profile.
//
// A favour, not a feature: the wizard has already saved the layout locally by
// the time this is offered, and nothing here can affect that. It is one shot,
// never automatic, and it works signed out — the people most likely to own an
// unrecognised kit are the least likely to have made an account first.
//
// What goes: the kit's name and its layout. What doesn't: practice history,
// statistics, lesson progress, or any identifier beyond the account id of a
// signed-in submitter — and that one is filled in by the database from
// auth.uid(), never sent from here.

import { createBrowserSupabase, supabaseConfigured } from "$lib/supabase";
import type { Controller } from "$lib/controller.svelte";

/**
 * Whether there is anywhere to send a layout at all. Running with no Supabase
 * configured is a perfectly normal way to run this app, and offering a favour
 * that cannot be done is worse than not offering it.
 */
export const canShareLayouts = supabaseConfigured;

/** Exactly what a submission carries, so it can be shown before it is sent. */
export function layoutPayload(controller: Controller) {
  return {
    kind: controller.kind,
    profile: controller.profile,
    pads: controller.pads.map((p) => ({
      label: p.label,
      role: p.role,
      note: p.note,
      sound: p.sound,
      ...(p.altNote != null
        ? { altNote: p.altNote, altSound: p.altSound }
        : {}),
    })),
    hihat: {
      mode: controller.hihat.mode,
      pedal: controller.hihat.pedal,
    },
  };
}

/**
 * Best-effort: a failure is reported to the caller and changes nothing locally.
 * Returns false when there is no Supabase configured at all, which is a
 * perfectly normal way to run this app.
 */
export async function shareLayout(controller: Controller): Promise<boolean> {
  if (!supabaseConfigured) return false;
  try {
    const supabase = createBrowserSupabase(fetch);
    const { error } = await supabase.from("device_layouts").insert({
      device_name: controller.name.slice(0, 120) || "Unnamed kit",
      layout: layoutPayload(controller),
    });
    return !error;
  } catch {
    return false;
  }
}
