{ pkgs, config, ... }:

{
  languages.javascript = {
    enable = true;
    pnpm = {
      enable = true;
      install.enable = true;
    };
  };

  pre-commit.hooks = {
    eslint.enable = true;
    prettier.enable = true;
  };

  packages = with pkgs; [
    typescript-language-server
    vscode-langservers-extracted
  ];

  scripts.dev = {
    exec = "pnpm dev --host";
    description = "Start SvelteKit dev server";
  };

  scripts.build = {
    exec = "pnpm build";
    description = "Build SvelteKit app";
  };

  scripts.check = {
    exec = "pnpm check";
    description = "Type-check SvelteKit app";
  };

  scripts.lint = {
    exec = "pnpm lint";
    description = "Lint SvelteKit app";
  };

  enterShell = ''
    echo "✦ SvelteKit dev environment ready"
    echo "  dev   – start dev server"
    echo "  build – build for production"
    echo "  check – type-check"
    echo "  lint  – run linter"
  '';

  processes.dev.exec = "pnpm dev --host";
}
