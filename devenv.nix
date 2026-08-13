{ pkgs, config, inputs, ... }:

let
  # Agent skills live in .agents/skills — the tool-neutral location, so one
  # skill serves every assistant. OpenCode is told about it in its config;
  # Claude Code has no such setting (skillsPaths is a plugin-manifest field and
  # skillsDirs is team-store only), so enterShell mirrors each skill into
  # .claude/skills, which is the only directory it scans.
  skillsDir = ".agents/skills";

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
      # Relative, so it resolves against the project root rather than the store
      # path this file is symlinked from.
      skills.paths = [ skillsDir ];
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

    # Supabase CLI — link the project and push auth/config to the remote
    # (Site URL, redirect allowlist) or run a local stack. `supabase login`
    # once (token in ~/.supabase, outside the repo).
    supabase-cli

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

  # A long session walks the module graph often enough to exhaust V8's default
  # ~4 GB heap and abort the server mid-work ("Ineffective mark-compacts near
  # heap limit"). Nothing is leaking that a restart wouldn't also fix — the
  # ceiling is simply too low for a dev server left running for hours. Raised
  # for the dev server alone; build and check are short-lived and don't need it.
  scripts.dev = {
    exec = "NODE_OPTIONS=--max-old-space-size=8192 pnpm dev --host";
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

  # Vercel CLI isn't packaged in this nixpkgs (nodePackages was removed
  # upstream), so run it through npx on the node the JS toolchain already
  # provides. `vercel login` once (token in ~/.local/share/com.vercel.cli,
  # outside the repo), then `vercel env` / `vercel deploy` are non-interactive.
  scripts.vercel = {
    exec = ''npx --yes vercel@latest "$@"'';
    description = "Vercel CLI (via npx)";
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

    # Mirror ${skillsDir} into .claude/skills — one relative symlink per skill,
    # dangling ones pruned. A skill added after entering the shell needs a
    # re-entry to show up in Claude Code; OpenCode reads the directory directly.
    mkdir -p "${config.devenv.root}/.claude/skills"
    for skill in "${config.devenv.root}/${skillsDir}"/*/; do
      [ -d "$skill" ] || continue
      name=$(basename "$skill")
      ln -sfn "../../${skillsDir}/$name" "${config.devenv.root}/.claude/skills/$name"
    done
    for link in "${config.devenv.root}/.claude/skills"/*; do
      if [ -L "$link" ] && [ ! -e "$link" ]; then rm -f "$link"; fi
    done

    echo "✦ SvelteKit dev environment ready"
    echo "  dev   – start dev server"
    echo "  build – build for production"
    echo "  check – type-check"
    echo "  lint  – run linter"
    echo "  toot  – Mastodon CLI (run 'toot login' once)"
    echo "  audit-samples / repair-samples – drum sample health"
  '';

  processes.dev.exec = "NODE_OPTIONS=--max-old-space-size=8192 pnpm dev --host";
}
