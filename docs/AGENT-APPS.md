# Using the kit with different agent apps

Everything has one canonical source: `AGENTS.md` (rules), `skills/<name>/SKILL.md` (skills, Agent Skills format) and `commands/<name>.md` (slash commands). `python3 scripts/sync_agent_files.py` generates what each app expects. Re-run it after editing a skill or command.

| App | Reads rules from | Skills | Commands |
|---|---|---|---|
| **Claude Code** (CLI, desktop, IDE) | `CLAUDE.md` → `AGENTS.md` | `.claude/skills/` (linked to `skills/`), loaded automatically | `.claude/commands/*.md` → `/new-project` etc. |
| **OpenAI Codex** (CLI, IDE) | `AGENTS.md` | `.agents/skills/` (linked to `skills/`) | Optional: `python3 scripts/sync_agent_files.py --codex` installs them as `/nmims-<name>` prompts in `~/.codex/prompts` (asks first) |
| **Google Antigravity** | `AGENTS.md` (and `GEMINI.md`) | Ask the agent to follow `skills/<name>/SKILL.md` | `.agent/workflows/*.md` → `/new-project` etc. |
| **Gemini CLI** | `GEMINI.md` → `AGENTS.md` | Ask the agent to follow `skills/<name>/SKILL.md` | `.gemini/commands/*.toml` → `/new-project` etc. |
| **Cursor** | `AGENTS.md` | Ask the agent to follow `skills/<name>/SKILL.md` | `.cursor/commands/*.md` |
| **GitHub Copilot** (VS Code agent mode) | `.github/copilot-instructions.md` → `AGENTS.md` | Ask the agent to follow `skills/<name>/SKILL.md` | `.github/prompts/*.prompt.md` → `/new-project` etc. |
| **Any other assistant** | Paste or attach `AGENTS.md` | Attach the relevant `SKILL.md` | Paste `commands/<name>.md` |

## Notes
- Symlinks (`.claude/skills`, `.agents/skills`) work on macOS and Linux. On Windows run `python scripts/sync_agent_files.py --copy`.
- The agent needs permission to run shell commands (Node, Python) for builds and checks, and a web search tool for the web part of the originality check.
- Skills reference each other by path inside `skills/`, so keep the folder structure intact when copying.

## Adding a skill
1. Create `skills/<name>/SKILL.md` with front matter: `name` (lowercase, hyphens, matches the folder) and `description` (what it does and when to use it, under 1,024 characters). Put long material in `references/` and runnable helpers in `scripts/` (relative paths only).
2. Add it to the skills table in `AGENTS.md` and `README.md`.
3. Run `python3 scripts/sync_agent_files.py`.

## Adding a command
1. Create `commands/<name>.md` with front matter `description` (and optional `argument-hint`); write the steps; use `$ARGUMENTS` for the user's input.
2. Run `python3 scripts/sync_agent_files.py`.
