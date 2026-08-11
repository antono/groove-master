<script lang="ts">
	import { page } from "$app/state";
	import { base } from "$app/paths";
	import { authState } from "$lib/auth.svelte";
	import { supabaseConfigured } from "$lib/supabase";
	import { signinLinkFailed, signinLinkSent } from "$lib/analytics";
	import PageMeta from "$lib/page-meta.svelte";
	import SyncBadge from "$lib/sync-badge.svelte";
	import type { SupabaseClient } from "@supabase/supabase-js";

	const supabase = $derived(page.data.supabase as SupabaseClient | null);

	let email = $state("");
	let sent = $state(false);
	let busy = $state(false);
	let error = $state<string | null>(null);

	async function sendLink(event: Event) {
		event.preventDefault();
		if (!supabase || !email) return;
		busy = true;
		error = null;
		// The link comes back to /auth/confirm, which sets the session cookie.
		const redirectTo = `${location.origin}${base}/auth/confirm?next=${encodeURIComponent(
			base + "/account",
		)}`;
		const { error: err } = await supabase.auth.signInWithOtp({
			email,
			options: { emailRedirectTo: redirectTo },
		});
		busy = false;
		if (err) {
			error = err.message;
			signinLinkFailed();
		} else {
			sent = true;
			signinLinkSent();
		}
	}

	async function signOut() {
		if (!supabase) return;
		await supabase.auth.signOut();
		// onAuthStateChange in the layout clears authState and re-runs load.
	}
</script>

<PageMeta
	title="Account"
	description="Sign in to back up your practice progress and stats across devices."
/>

<section class="account">
	<h1>Account</h1>

	{#if !supabaseConfigured}
		<p class="muted">
			Cloud sync isn't configured for this build. Your progress and stats are
			saved on this device only.
		</p>
	{:else if authState.user}
		<p>
			Signed in as <strong>{authState.user.email}</strong>. Your progress and
			stats sync to the cloud in the background.
		</p>
		<div class="row">
			<SyncBadge />
		</div>
		<button class="button" onclick={signOut}>Sign out</button>
		<p class="muted small">
			Signing out keeps this device's progress and stats — it just stops syncing.
		</p>
	{:else if sent}
		<p>
			Check your inbox — we sent a sign-in link to <strong>{email}</strong>. Open
			it on this device to finish signing in.
		</p>
	{:else}
		<p class="muted">
			Sign in to back up your progress and stats and pick up on any device.
			Optional — the app works fully without an account.
		</p>
		<form onsubmit={sendLink}>
			<input
				type="email"
				bind:value={email}
				placeholder="you@example.com"
				autocomplete="email"
				required
				disabled={busy}
			/>
			<button class="button" type="submit" disabled={busy || !email}>
				{busy ? "Sending…" : "Email me a link"}
			</button>
		</form>
		{#if error}<p class="error">{error}</p>{/if}
	{/if}
</section>

<style>
	.account {
		max-width: 34rem;
		margin: 2rem auto;
	}
	.muted {
		color: var(--text-muted);
		line-height: 1.6;
	}
	.small {
		font-size: 0.85rem;
	}
	.row {
		margin: 0.75rem 0;
	}
	form {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
		margin-top: 1rem;
	}
	input {
		flex: 1 1 14rem;
		padding: 0.5rem 0.7rem;
		border-radius: var(--radius-sm);
		border: 1px solid var(--border);
		background: var(--surface);
		color: var(--text);
		font-size: 1rem;
	}
	.button {
		padding: 0.5rem 1rem;
		border-radius: var(--radius-sm);
		border: none;
		background: var(--surface-2);
		color: var(--text);
		font-family: var(--font-mono);
		cursor: pointer;
	}
	.button:hover:not(:disabled) {
		color: var(--gold);
	}
	.button:disabled {
		opacity: 0.6;
		cursor: default;
	}
	.error {
		color: var(--red, #e0607e);
	}
</style>
