#!/usr/bin/env python3
"""Create or update a project's .remember_anytime rule directory."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


DEFAULT_RULES = """# Remember Anytime Rules

## Coding Workflow

1. Add the project's mandatory pre-edit workflow here.
2. Add the required validation commands here.
3. Add rules for how broad or narrow code changes should be.

## Coding Standards

1. Add naming, architecture, abstraction, error handling, and compatibility rules here.
2. Add rules about generated code, comments, tests, and documentation here.

## Component And API Rules

1. Add required component libraries, helper functions, hooks, services, or APIs here.
2. Add forbidden legacy APIs or replacement patterns here.

## Project Conventions

1. Add localization, theme, configuration, storage, sync, routing, and state management rules here.
2. Add critical business logic or edge cases that must never be forgotten here.
"""

AGENT_BRIDGE_START = "<!-- remember-anytime:start -->"
AGENT_BRIDGE_END = "<!-- remember-anytime:end -->"
AGENT_BRIDGE = f"""{AGENT_BRIDGE_START}
## Remember Anytime

Before working in this project, read `.remember_anytime/` if it exists. Treat its Markdown files as durable project rules and reusable workflows that survive context compaction.

Automatic routing:

- For coding, refactor, test, build, review, or bug-fix tasks, read `.remember_anytime/rules.md` and any coding/architecture rules.
- For server, log, deploy, SSH, production, or remote-debugging tasks, read `.remember_anytime/server.md` if present.
- For web, browser, Flutter web, mobile, desktop, Windows, macOS, Linux, Android, iOS, or multi-platform tasks, read `.remember_anytime/platforms.md` if present.
- For UI, component, theme, style, localization, copy, or interaction tasks, read `.remember_anytime/ui.md` if present.
- For repeatable workflow tasks, refreshes, report updates, browser automation, catalog syncs, or "run this previous process again" requests, search and read matching `.remember_anytime/workflows/*.md` files.
- When the user asks to remember a permanent rule, write it to `.remember_anytime/rules.md` instead of only acknowledging it in chat.
- When the user asks to solidify a repeatable process, write it to `.remember_anytime/workflows/<slug>.md`.
{AGENT_BRIDGE_END}
"""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def build_rules(source: Path | None, title: str) -> str:
    if source is None:
        return DEFAULT_RULES.rstrip() + "\n"

    body = read_text(source).strip()
    return f"# {title}\n\nMigrated from `{source.name}`.\n\n{body}\n"


def sync_agent_bridge(project: Path) -> Path:
    agent_path = choose_agent_bridge(project)
    if agent_path.exists():
        content = read_text(agent_path)
    else:
        content = "# Agent Instructions\n"

    start = content.find(AGENT_BRIDGE_START)
    end = content.find(AGENT_BRIDGE_END)
    if start != -1 and end != -1 and end > start:
        end += len(AGENT_BRIDGE_END)
        updated = content[:start] + AGENT_BRIDGE.rstrip() + content[end:]
    else:
        updated = content.rstrip() + "\n\n" + AGENT_BRIDGE.rstrip() + "\n"

    agent_path.write_text(updated.rstrip() + "\n", encoding="utf-8")
    return agent_path


def choose_agent_bridge(project: Path) -> Path:
    agents_path = project / "AGENTS.md"
    agent_path = project / "AGENT.md"
    if agents_path.exists():
        return agents_path
    if agent_path.exists():
        return agent_path
    return agents_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create .remember_anytime/rules.md for a project."
    )
    parser.add_argument("--project", required=True, help="Project root directory.")
    parser.add_argument("--source", help="Existing rules file to migrate, such as AGENT.md.")
    parser.add_argument("--title", default="Remember Anytime Rules")
    parser.add_argument("--append", action="store_true", help="Append to existing rules.md.")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing rules.md.")
    parser.add_argument(
        "--no-agent",
        action="store_true",
        help="Do not create or update the AGENT.md bridge.",
    )
    args = parser.parse_args()

    if args.append and args.overwrite:
        parser.error("--append and --overwrite cannot be used together")

    project = Path(args.project).expanduser().resolve()
    if not project.exists() or not project.is_dir():
        print(f"Project directory does not exist: {project}", file=sys.stderr)
        return 2

    source = Path(args.source).expanduser().resolve() if args.source else None
    if source and (not source.exists() or not source.is_file()):
        print(f"Source file does not exist: {source}", file=sys.stderr)
        return 2

    remember_dir = project / ".remember_anytime"
    remember_dir.mkdir(exist_ok=True)

    rules_path = remember_dir / "rules.md"
    new_rules = build_rules(source, args.title)

    if rules_path.exists() and not args.append and not args.overwrite:
        print(f"Rules already exist: {rules_path}")
        print("Use --append or --overwrite to modify it.")
        return 1

    if args.append and rules_path.exists():
        existing = read_text(rules_path).rstrip()
        rules_path.write_text(existing + "\n\n---\n\n" + new_rules, encoding="utf-8")
    else:
        rules_path.write_text(new_rules, encoding="utf-8")

    print(f"Created/updated: {rules_path}")
    if not args.no_agent:
        agent_path = sync_agent_bridge(project)
        print(f"Updated agent bridge in: {agent_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
