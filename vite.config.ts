import adapter from "@sveltejs/adapter-auto";
import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [
    sveltekit({
      serviceWorker: {
        // src/service-worker.ts caches the one-shots on demand instead of
        // precaching them, so keep the 531 audio paths out of the
        // `$service-worker` file manifest — otherwise they ship as dead
        // strings in the worker bundle (14 kB of it).
        files: (filename) =>
          !filename.endsWith(".oga") && !/\.DS_Store/.test(filename),
      },

      compilerOptions: {
        // Force runes mode for the project, except for libraries. Can be removed in svelte 6.
        runes: ({ filename }) =>
          filename.split(/[/\\]/).includes("node_modules") ? undefined : true,
      },

      // adapter-auto only supports some environments, see https://svelte.dev/docs/kit/adapter-auto for a list.
      // If your environment is not supported, or you settled on a specific environment, switch out the adapter.
      // See https://svelte.dev/docs/kit/adapters for more information about adapters.
      adapter: adapter(),
    }),
  ],
});
