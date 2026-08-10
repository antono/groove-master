<script lang="ts">
	// A lightweight read-out of the background sync state. Renders nothing unless
	// there is something worth saying (i.e. sync is active for a signed-in user).
	import { authState, syncState } from "$lib/auth.svelte";
	import { queueReconcile } from "$lib/sync";

	const label = $derived(
		{
			disabled: "",
			idle: syncState.pending > 0 ? `${syncState.pending} to sync` : "Synced",
			syncing: "Syncing…",
			offline: "Offline — will sync later",
			error: "Sync failed — will retry",
		}[syncState.status],
	);
</script>

{#if authState.user && label}
	<button
		class="sync-badge {syncState.status}"
		title="Click to sync now"
		onclick={() => queueReconcile()}
	>
		<span class="dot"></span>{label}
	</button>
{/if}

<style>
	.sync-badge {
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		font-family: var(--font-mono);
		font-size: 0.78rem;
		color: var(--text-muted);
		background: none;
		border: none;
		padding: 0.2rem 0.3rem;
		cursor: pointer;
	}
	.dot {
		width: 0.55rem;
		height: 0.55rem;
		border-radius: 50%;
		background: var(--text-faint);
	}
	.idle .dot {
		background: var(--green);
	}
	.syncing .dot {
		background: var(--gold);
		animation: pulse 1s ease-in-out infinite;
	}
	.offline .dot {
		background: var(--text-faint);
	}
	.error .dot {
		background: var(--red, #e0607e);
	}
	@keyframes pulse {
		50% {
			opacity: 0.3;
		}
	}
</style>
