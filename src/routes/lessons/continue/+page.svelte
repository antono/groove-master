<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import PageMeta from '$lib/page-meta.svelte';
	import { allSessions } from '$lib/stats';
	import { progressByLesson } from '$lib/progress';
	import { continueTarget } from '$lib/catalogue';
	import type { PageData } from './$types';

	// "My next lesson" as a URL.
	//
	// A PWA shortcut, a bookmark and a shared link all have to name a destination
	// in advance, but the destination here is derived from practice history that
	// lives on the device (IndexedDB) and nowhere else — no server can work it
	// out. So this route is the resolver: it computes the target the moment it
	// loads and sends the student on.
	//
	// It uses the same continueTarget() the landing's Continue button uses, which
	// is the point — "continue" must not come to mean two different lessons.

	let { data }: { data: PageData } = $props();

	onMount(() => {
		let cancelled = false;

		void (async () => {
			const manifest = data.manifest;
			// No catalogue means nothing to continue to. The landing says why in
			// language a student can act on, which beats an error page here.
			if (!manifest) {
				if (!cancelled) void goto(`${base}/lessons`, { replaceState: true });
				return;
			}

			// allSessions() is non-throwing by contract; a browser with no IndexedDB
			// yields no history, which resolves to the first written lesson — exactly
			// what a student with no history should get.
			const progress = progressByLesson(await allSessions());
			if (cancelled) return;

			const target = continueTarget(manifest, progress);
			void goto(target ? `${base}/lessons/${target}` : `${base}/lessons`, {
				// replaceState so Back from the lesson returns wherever the student came
				// from. Without it this route sits in the history stack and going back
				// lands on the resolver, which immediately resolves forward again — the
				// Back button stops working.
				replaceState: true
			});
		})();

		return () => {
			cancelled = true;
		};
	});
</script>

<PageMeta title="Continue" description="Pick up where you left off." />

<p class="resolving">Finding your next lesson…</p>

<noscript>
	<p><a href="{base}/lessons">Open the lesson catalogue</a></p>
</noscript>

<style>
	.resolving {
		color: var(--text-muted);
	}
</style>
