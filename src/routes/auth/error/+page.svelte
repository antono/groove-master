<script lang="ts">
	import { base } from "$app/paths";
</script>

<section class="auth-error">
	<h1>Sign-in link didn't work</h1>
	<p>
		That magic link was invalid or has expired. Links can only be used once and
		time out after a while — request a fresh one and try again.
	</p>
	<a class="button" href="{base}/account">Back to sign in</a>
</section>

<style>
	.auth-error {
		max-width: 32rem;
		margin: 3rem auto;
		text-align: center;
	}
	.auth-error p {
		color: var(--text-muted);
		line-height: 1.6;
	}
	.button {
		display: inline-block;
		margin-top: 1rem;
		padding: 0.5rem 1rem;
		border-radius: var(--radius-sm);
		background: var(--surface-2);
		color: var(--text);
		text-decoration: none;
		font-family: var(--font-mono);
	}
	.button:hover {
		background: var(--surface-3, var(--surface-2));
		color: var(--gold);
	}
</style>
