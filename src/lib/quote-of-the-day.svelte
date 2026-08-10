<!--
  Quote of the Day — a full-screen interstitial shown between lessons.

  Controlled by `open`: while true it shows one random quote (preferring ones
  the user hasn't seen this cycle; when all are seen the cycle restarts). The
  author's testimonial is revealed on hover, click, or keyboard focus. A like or
  dislike records the rating (offline-first via quote-store, synced by sync.ts)
  and calls `onAdvance`; the "never show quotes" checkbox opts out and advances
  with no rating. Navigation is the parent's job — this only signals `onAdvance`.
-->
<script lang="ts">
  import { base } from "$app/paths";
  import { queueReconcile } from "$lib/sync";
  import {
    markSeen,
    readSeen,
    resetSeen,
    setQuotesOff,
    setRating,
    type RatingValue,
  } from "$lib/quote-store";

  type Quote = {
    id: string;
    citation: string;
    author: string;
    testimonial: string;
  };

  let {
    open = false,
    onAdvance,
  }: {
    open?: boolean;
    onAdvance: () => void;
  } = $props();

  let quotes = $state<Quote[]>([]);
  let loaded = $state(false);
  let current = $state<Quote | null>(null);
  let showTestimonial = $state(false);

  async function ensureLoaded(): Promise<Quote[]> {
    if (loaded) return quotes;
    try {
      const res = await fetch(`${base}/quotes/quotes.json`);
      quotes = res.ok ? await res.json() : [];
    } catch {
      quotes = [];
    }
    loaded = true;
    return quotes;
  }

  function pick(all: Quote[]): Quote | null {
    if (all.length === 0) return null;
    const seen = readSeen();
    let pool = all.filter((q) => !seen.has(q.id));
    if (pool.length === 0) {
      // Whole collection seen — restart the cycle from the beginning.
      resetSeen();
      pool = all;
    }
    const chosen = pool[Math.floor(Math.random() * pool.length)];
    markSeen(chosen.id);
    return chosen;
  }

  // Choose a fresh quote each time the interstitial opens. If quotes fail to
  // load or the collection is empty, advance straight through rather than
  // stranding the student on a blank screen.
  $effect(() => {
    if (!open) {
      current = null;
      showTestimonial = false;
      return;
    }
    let cancelled = false;
    void ensureLoaded().then((all) => {
      if (cancelled) return;
      const chosen = pick(all);
      if (chosen) current = chosen;
      else onAdvance();
    });
    return () => {
      cancelled = true;
    };
  });

  function rate(value: RatingValue) {
    if (current) {
      setRating(current.id, value);
      queueReconcile();
    }
    onAdvance();
  }

  function neverShow() {
    setQuotesOff(true);
    onAdvance();
  }
</script>

{#if open && current}
  <div class="quote-overlay" role="dialog" aria-modal="true" aria-label="Quote of the day">
    <figure class="quote">
      <blockquote>{current.citation}</blockquote>
      <figcaption>
        <button
          type="button"
          class="author"
          aria-expanded={showTestimonial}
          onclick={() => (showTestimonial = !showTestimonial)}
          onmouseenter={() => (showTestimonial = true)}
          onmouseleave={() => (showTestimonial = false)}
          onfocus={() => (showTestimonial = true)}
          onblur={() => (showTestimonial = false)}
        >
          {current.author}
        </button>
        {#if showTestimonial && current.testimonial}
          <p class="testimonial">{current.testimonial}</p>
        {/if}
      </figcaption>
    </figure>

    <div class="rate">
      <button type="button" class="like" onclick={() => rate("like")} aria-label="Like this quote">
        👍 Like
      </button>
      <button
        type="button"
        class="dislike"
        onclick={() => rate("dislike")}
        aria-label="Dislike this quote"
      >
        👎 Dislike
      </button>
    </div>

    <label class="never">
      <input type="checkbox" onchange={neverShow} />
      Never show quotes
    </label>
  </div>
{/if}

<style>
  .quote-overlay {
    position: fixed;
    inset: 0;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2.5rem;
    padding: 2rem;
    background: var(--bg);
    text-align: center;
  }

  .quote {
    margin: 0;
    max-width: 42rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
  }

  blockquote {
    margin: 0;
    font-size: clamp(1.5rem, 4vw, 2.75rem);
    line-height: 1.25;
    font-weight: 600;
    color: var(--text);
  }

  blockquote::before {
    content: "\201C";
  }
  blockquote::after {
    content: "\201D";
  }

  figcaption {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
  }

  .author {
    background: none;
    border: none;
    padding: 0;
    cursor: pointer;
    font: inherit;
    font-size: clamp(1rem, 2.5vw, 1.35rem);
    font-weight: 600;
    color: var(--gold);
    border-bottom: 1px dashed var(--gold-dim);
  }
  .author:hover,
  .author:focus-visible {
    color: var(--gold);
    border-bottom-color: var(--gold);
  }

  .testimonial {
    margin: 0;
    max-width: 34rem;
    font-size: 0.95rem;
    line-height: 1.5;
    color: var(--text-muted);
  }

  .rate {
    display: flex;
    gap: 1rem;
  }

  .rate button {
    font: inherit;
    font-size: 1.1rem;
    padding: 0.65rem 1.5rem;
    border-radius: 0.6rem;
    border: 1px solid var(--border-strong);
    background: var(--surface-2);
    color: var(--text);
    cursor: pointer;
  }
  .rate .like:hover {
    border-color: var(--green);
    color: var(--green);
  }
  .rate .dislike:hover {
    border-color: var(--red);
    color: var(--red);
  }

  .never {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
    color: var(--text-faint);
    cursor: pointer;
  }
</style>
