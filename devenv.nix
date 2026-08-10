{ pkgs, config, inputs, ... }:

let
  # Generate Claude Code and OpenCode MCP configs in the store, so their shared
  # server definitions cannot drift. Unlike devenv's Claude module, this leaves
  # the hand-maintained .claude/settings.json untouched.
  mcpSettings = {
    programs.chrome-devtools = {
      enable = true;
      args = [
        "--executablePath"
        "${pkgs.google-chrome}/bin/google-chrome-stable"
      ];
    };
    # Supabase MCP over HTTP. A remote transport, so no local command — the URL
    # carries the project_ref and the enabled feature groups. Equivalent to
    # `claude mcp add --scope project --transport http supabase <url>`.
    settings.servers.supabase = {
      type = "http";
      url = "https://mcp.supabase.com/mcp?project_ref=dbfmnbnjjjmbywbeuqts&features=docs,account,database,debugging,development,functions,branching";
    };
  };
  claudeMcpConfig = inputs.mcp-servers-nix.lib.mkConfig pkgs (mcpSettings // {
    flavor = "claude-code";
  });
  opencodeMcpConfig = inputs.mcp-servers-nix.lib.mkConfig pkgs (mcpSettings // {
    flavor = "opencode";
    settings = mcpSettings.settings // {
      "$schema" = "https://opencode.ai/config.json";
    };
  });
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

    # Announcing releases on the fediverse. One-time `toot login` per account
    # stores the token in ~/.config/toot/config.json (outside the repo), after
    # which `toot post` is non-interactive.
    toot

    # Sample pipeline — scripts/render-{drums,bass}.py shell out to these.
    python3
    fluidsynth # renders the .sf2 SoundFonts to one-shots
    ffmpeg # pitch-shifts stand-ins for GM notes the .sf2 leaves unmapped

    # Inspecting what came out. macOS has no Ogg Vorbis decoder, so afinfo and
    # QuickTime are both useless on static/**/*.oga:
    #   ogginfo <f>            bitrate, duration, channels
    #   sox <f> -n stat        peak/RMS — catches a silent render
    #   ffmpeg -i <f> -af volumedetect -f null -
    vorbis-tools
    sox
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

  scripts.audit-samples = {
    exec = "python3 scripts/render-drums.py --audit";
    description = "Check static/drums for silently-rendered samples";
  };

  scripts.repair-samples = {
    exec = "python3 scripts/render-drums.py --repair";
    description = "Substitute silent samples in place (needs ffmpeg, not the .sf2)";
  };

  enterShell = ''
    ln -sfT ${claudeMcpConfig} "${config.devenv.root}/.mcp.json"
    ln -sfT ${opencodeMcpConfig} "${config.devenv.root}/opencode.json"
    echo "✦ SvelteKit dev environment ready"
    echo "  dev   – start dev server"
    echo "  build – build for production"
    echo "  check – type-check"
    echo "  lint  – run linter"
    echo "  toot  – Mastodon CLI (run 'toot login' once)"
    echo "  audit-samples / repair-samples – drum sample health"
  '';

  processes.dev.exec = "pnpm dev --host";
}
