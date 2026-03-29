# Recipe: Set Up a Project Workspace

## Goal

Create a *ProjectName* workspace from the foundational SEJA framework, linking
it to the *ProjectName* codebase -- keeping framework configuration, design
artifacts, and source code physically separated.

## Prerequisites

- Claude Code or Codex CLI installed
- The foundational SEJA framework available (as a cloned repo or quickstart
  kit zip)
- An existing *ProjectName* codebase (git repository) you want to work with

## Quick path (automated)

If you have the foundational SEJA framework locally, run `/quickstart --workspace` / `$quickstart --workspace`
and follow the prompts. This automates everything below: creates the workspace
directory, runs `git init`, copies framework files from the foundational
framework, creates `_output/`, generates `project-conventions.md` with absolute
paths to the codebase, and creates launcher scripts. Then skip to step 5 below.

Alternatively, from the command line:
```bash
python .claude/skills/scripts/create_workspace.py \
  --from <path-to-foundational-seja-framework> \
  --workspace d:/workspaces/my-project \
  --target d:/git/my-project
```

## Manual steps (if not using the automated path)

1. **Create and initialize the workspace directory**
   ```bash
   mkdir -p d:/workspaces/my-project
   cd d:/workspaces/my-project
   git init
   ```
   The *MyProject* workspace is its own git repo. It tracks framework
   configuration, project-specific references, conceptual design, and all
   output artifacts (plans, advisories, briefs) -- giving you version history
   and audit trails for the entire design and decision-making process,
   independent of the *MyProject* codebase.

2. **Extract the foundational SEJA framework into the workspace**
   ```bash
   unzip seja-quickstart-kit.zip -d .
   ```
   This creates `.claude/` or `.codex/` and `.agent-resources/` inside the workspace.

3. **Run `/quickstart .` / `$quickstart .` and walk through the questionnaire**
   Answer the prompts to generate project-specific files. Point the conceptual
   design at the existing system in the codebase.

4. **Edit `project-conventions.md` to set absolute paths**
   Set `OUTPUT_DIR` to a path inside the workspace (so output artifacts are
   committed alongside framework configuration), and point source directories
   at the *MyProject* codebase:
   ```markdown
   OUTPUT_DIR = D:/workspaces/my-project/_output
   BACKEND_DIR = D:/git/my-project/backend
   FRONTEND_DIR = D:/git/my-project/frontend
   ```
   Python's path resolution treats absolute paths as anchors, so this works
   without any framework code changes.

## After setup (both paths)

1. **Start the agent from the workspace**
   Run the generated launcher script:
   ```bash
   ./launch.sh          # Unix / Git Bash / WSL
   launch.bat           # Windows Command Prompt / PowerShell
   ```
   This starts the agent in the workspace and adds the *MyProject* codebase
   as an additional directory. Edit the script if the codebase moves.

   Alternatively, start the agent in the workspace and add `D:/git/my-project` as an additional directory if your host supports that pattern.

2. **Verify and commit**
   ```
   /check validate   # Claude
   $check validate   # Codex
   ```
   Confirm that all paths resolve correctly. Then commit the initial workspace:
   ```bash
   git add -A
   git commit -m "Initial MyProject workspace setup"
   ```

## How it all connects

```
foundational SEJA framework        the single source of truth
  (repo or quickstart kit)         (skills, scripts, templates, references)
          |
          | /quickstart --workspace (Claude)
          | $quickstart --workspace (Codex)
          v
MyProject workspace                its own git repo
  d:/workspaces/my-project/
    .claude/ or .codex/            copied from foundational framework
    .agent-resources/              copied + project-specific files generated
    _output/                       plans, advisories, briefs (version-controlled)
    launch.sh / launch.bat         starts the agent with the codebase attached
          |
          | additional-directory access (no framework files added)
          v
MyProject codebase                 stays completely clean
  d:/git/my-project/
    (source code only)
```

## Tips

- The workspace pattern is recommended for teams (each member gets their own
  workspace) and agencies (one workspace per client codebase).
- When upgrading the foundational framework, run `/quickstart --upgrade` / `$quickstart --upgrade` in
  the workspace -- it preserves all project-specific files and `_output/`.
- The workspace git repo captures your entire design and decision history
  (conceptual design, plans, advisories, briefs) independently of the
  codebase. This is especially valuable for audit trails in regulated domains
  and for agencies tracking work per client.

## Related journeys

- [Growing Team](../journeys/journey-growing-team.md)
- [Agency Multi-Project](../journeys/journey-agency-multi-project.md)
- [Enterprise Evolution](../journeys/journey-enterprise-evolution.md)
