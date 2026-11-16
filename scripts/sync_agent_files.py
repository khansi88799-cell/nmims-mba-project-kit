#!/usr/bin/env python3
"""Generate every agent app's files from the canonical skills/ and commands/ folders.

    python3 scripts/sync_agent_files.py            # symlink skills, write command wrappers
    python3 scripts/sync_agent_files.py --copy     # copy skills instead of symlinking (Windows)
    python3 scripts/sync_agent_files.py --codex    # also install the commands as Codex prompts in ~/.codex/prompts (asks first)

Canonical sources (edit these only):
  skills/<name>/SKILL.md      Agent Skills format (name + description front matter)
  commands/<name>.md          front matter: description, optional argument-hint; body uses $ARGUMENTS

Generated (do not edit by hand):
  .claude/skills  -> skills         Claude Code skills
  .agents/skills  -> skills         Codex and other Agent Skills readers
  .claude/commands/<name>.md        Claude Code slash commands  (/name)
  .gemini/commands/<name>.toml      Gemini CLI commands          (/name)
  .agent/workflows/<name>.md        Antigravity workflows        (/name)
  .cursor/commands/<name>.md        Cursor commands              (/name)
  .github/prompts/<name>.prompt.md  GitHub Copilot prompt files  (/name)
"""
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEN_NOTE = "Generated from commands/{name}.md by scripts/sync_agent_files.py. Edit the source, not this file."


def parse(md: str):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", md, re.S)
    meta, body = {}, md
    if m:
        body = m.group(2).lstrip("\n")
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
    return meta, body


def link(target_dir: Path, link_path: Path, copy: bool):
    link_path.parent.mkdir(parents=True, exist_ok=True)
    if link_path.is_symlink() or link_path.is_file():
        link_path.unlink()
    elif link_path.is_dir():
        shutil.rmtree(link_path)
    if copy:
        shutil.copytree(target_dir, link_path)
    else:
        os.symlink(os.path.relpath(target_dir, link_path.parent), link_path)


def clean(folder: Path, pattern: str):
    if folder.exists():
        for f in folder.glob(pattern):
            if f.is_file() and "Generated from commands/" in f.read_text(encoding="utf-8", errors="ignore"):
                f.unlink()


def main():
    copy = "--copy" in sys.argv
    skills = ROOT / "skills"
    link(skills, ROOT / ".claude" / "skills", copy)
    link(skills, ROOT / ".agents" / "skills", copy)

    targets = {
        "claude": ROOT / ".claude" / "commands",
        "gemini": ROOT / ".gemini" / "commands",
        "antigravity": ROOT / ".agent" / "workflows",
        "cursor": ROOT / ".cursor" / "commands",
        "copilot": ROOT / ".github" / "prompts",
    }
    for t in targets.values():
        t.mkdir(parents=True, exist_ok=True)
    clean(targets["claude"], "*.md"); clean(targets["gemini"], "*.toml"); clean(targets["antigravity"], "*.md")
    clean(targets["cursor"], "*.md"); clean(targets["copilot"], "*.prompt.md")

    cmds = sorted((ROOT / "commands").glob("*.md"))
    for c in cmds:
        name = c.stem
        meta, body = parse(c.read_text(encoding="utf-8"))
        desc = meta.get("description", name)
        hint = meta.get("argument-hint", "")
        note = GEN_NOTE.format(name=name)
        # Claude Code
        fm = f"---\ndescription: {desc}\n" + (f"argument-hint: {hint}\n" if hint else "") + "---\n"
        (targets["claude"] / f"{name}.md").write_text(f"{fm}<!-- {note} -->\n\n{body}", encoding="utf-8")
        # Gemini CLI (TOML, {{args}})
        # TOML literal multi-line string ('''...''') so backslashes in commands need no escaping
        prompt = body.replace("$ARGUMENTS", "{{args}}").replace("'''", '"""')
        desc_lit = desc.replace("'", "’")
        (targets["gemini"] / f"{name}.toml").write_text(f"# {note}\ndescription = '{desc_lit}'\nprompt = '''\n{prompt}'''\n", encoding="utf-8")
        # Antigravity workflow
        (targets["antigravity"] / f"{name}.md").write_text(f"---\ndescription: {desc}\n---\n<!-- {note} -->\n\nArguments from the user, if any, follow the command name.\n\n{body.replace('$ARGUMENTS', 'the arguments the user gave')}", encoding="utf-8")
        # Cursor command (plain markdown)
        (targets["cursor"] / f"{name}.md").write_text(f"<!-- {note} -->\n# {desc}\n\n{body.replace('$ARGUMENTS', 'the text the user typed after the command')}", encoding="utf-8")
        # Copilot prompt file
        (targets["copilot"] / f"{name}.prompt.md").write_text(f"---\ndescription: {desc}\nmode: agent\n---\n<!-- {note} -->\n\n{body.replace('$ARGUMENTS', '${input:args}')}", encoding="utf-8")
    print(f"Linked skills into .claude/skills and .agents/skills ({'copied' if copy else 'symlinked'}); wrote {len(cmds)} commands for Claude, Gemini, Antigravity, Cursor and Copilot.")

    if "--codex" in sys.argv:
        dest = Path.home() / ".codex" / "prompts"
        ans = input(f"Install {len(cmds)} prompts into {dest} (existing files with the same names are replaced)? [y/N] ").strip().lower()
        if ans == "y":
            dest.mkdir(parents=True, exist_ok=True)
            for c in cmds:
                shutil.copy(c, dest / f"nmims-{c.stem}.md")
            print(f"Installed as /nmims-<name> prompts in {dest}")
        else:
            print("Skipped Codex prompts.")


if __name__ == "__main__":
    main()
