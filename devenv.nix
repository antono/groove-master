{ pkgs, config, inputs, ... }:

let
  # Claude Code MCP config for this project. Follows mcp-servers-nix's
  # claude-code-project example: build a .mcp.json in the store and symlink it in,
  # touching only .mcp.json (unlike the devenv `claude.code` module, which would
  # overwrite the hand-maintained .claude/settings.json).
  mcpConfig = inputs.mcp-servers-nix.lib.mkConfig pkgs {
    flavor = "claude-code";
    programs.chrome-devtools = {
      enable = true;
      args = [
        "--executablePath"
        "${pkgs.google-chrome}/bin/google-chrome-stable"
      ];
    };
  };
in
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
    opencode
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
    ln -sfT ${mcpConfig} "${config.devenv.root}/.mcp.json"
    echo "✦ SvelteKit dev environment ready"
    echo "  dev   – start dev server"
    echo "  build – build for production"
    echo "  check – type-check"
    echo "  lint  – run linter"
    echo "  mcp   – chrome-devtools (.mcp.json)"
  '';

  processes.dev.exec = "pnpm dev --host";
}
