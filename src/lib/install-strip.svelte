<script lang="ts">
	// The install affordance, and the precache's progress readout. One strip
	// because they are consecutive moments in the same story, and because a
	// second floating element competing for the same corner is one too many.
	//
	// A strip rather than a modal, deliberately: neither installing nor waiting
	// for samples is something a student should have to finish before they can
	// practise.
	import { pwaState, promptInstall, dismissInstall } from '$lib/pwa.svelte';

	const warming = $derived(pwaState.warming);
	const percent = $derived(warming === null ? 0 : Math.round(warming * 100));
</script>

{#if warming !== null}
	<div class="strip" role="status">
		<span class="text">Saving lessons and sounds for offline… {percent}%</span>
		<div class="bar" aria-hidden="true"><div class="fill" style="width: {percent}%"></div></div>
	</div>
{:else if pwaState.canInstall}
	<div class="strip">
		<span class="text">Install Groove Academy for offline practice</span>
		<div class="actions">
			<button class="install" onclick={() => promptInstall()}>Install</button>
			<button class="not-now" onclick={dismissInstall}>Not now</button>
		</div>
	</div>
{/if}

<style>
	.strip {
		position: fixed;
		left: calc(0.75rem + env(safe-area-inset-left));
		right: calc(0.75rem + env(safe-area-inset-right));
		bottom: calc(0.75rem + env(safe-area-inset-bottom));
		z-index: 40;
		display: flex;
		align-items: center;
		justify-content: space-between;
		flex-wrap: wrap;
		gap: 0.6rem;
		max-width: 34rem;
		margin: 0 auto;
		padding: 0.7rem 0.9rem;
		background: var(--surface-2);
		border: 1px solid var(--border-strong);
		border-radius: var(--radius);
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
	}

	.text {
		font-size: 0.9rem;
	}

	.actions {
		display: flex;
		gap: 0.4rem;
	}

	.install {
		background: var(--gold);
		border-color: var(--gold);
		color: #1a1505;
		font-weight: 650;
	}

	.not-now {
		background: none;
		color: var(--text-muted);
	}

	.bar {
		flex: 1 1 8rem;
		height: 4px;
		border-radius: 2px;
		background: var(--surface-3);
		overflow: hidden;
	}

	.fill {
		height: 100%;
		background: var(--gold);
		transition: width 200ms ease;
	}

	/* The bar's width already carries the progress; the easing is decoration. */
	@media (prefers-reduced-motion: reduce) {
		.fill {
			transition: none;
		}
	}
</style>
