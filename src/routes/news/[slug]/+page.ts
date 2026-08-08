// A missing post has to answer 404, not an empty 200 — these URLs get shared and
// indexed, so a typo'd or retired slug must say so to a crawler and not just to
// a reader. Only the load can set the status, hence this file.
import { error } from "@sveltejs/kit";

import { findNews } from "$lib/news";

export function load({ params }: { params: { slug: string } }) {
  const entry = findNews(params.slug);
  if (!entry) error(404, `No news item "${params.slug}"`);
  // The body is a component, so it is looked up again in the page rather than
  // returned through here — load data has to survive serialisation to the client.
  return { slug: entry.slug, title: entry.title, summary: entry.summary };
}
