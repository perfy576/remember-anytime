#!/usr/bin/env python3
"""Append a durable rule to a project's .remember_anytime/rules.md."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


DEFAULT_CONTENT = """# Remember Anytime Rules

## Coding Workflow

## Coding Standards

## Component And API Rules

## Project Conventions
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
- For repeatable workflow tasks, refreshes, report updates, browser automation, catalog syncs, "使用/执行/运行 X 流程", or "run this previous process again" requests, search and read matching `.remember_anytime/workflows/*.md` files, then follow their Procedure and Validation sections.
- When the user asks to remember a permanent rule, write it to `.remember_anytime/rules.md` instead of only acknowledging it in chat.
- When the user explicitly asks to remember a key, password, username, token, credential, host login, or other secret, write it to `.remember_anytime/secrets.md` and do not quote secret values back unless explicitly requested.
- When the user asks "固化 X 流程" or asks to solidify a repeatable process, write it to `.remember_anytime/workflows/<slug>.md`.
{AGENT_BRIDGE_END}
"""


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalize_rule(rule: str) -> str:
    rule = " ".join(rule.strip().split())
    if not rule:
        raise ValueError("Rule text cannot be empty.")
    return rule


def append_to_section(content: str, section: str, rule: str) -> str:
    heading = f"## {section}"
    bullet = f"- {rule}"

    if bullet in content:
        return content

    pattern = re.compile(rf"(^##\s+{re.escape(section)}\s*$)", re.MULTILINE)
    match = pattern.search(content)

    if not match:
        suffix = "" if content.endswith("\n") else "\n"
        return f"{content}{suffix}\n{heading}\n\n{bullet}\n"

    next_heading = re.search(r"^##\s+", content[match.end() :], re.MULTILINE)
    insert_at = len(content) if next_heading is None else match.end() + next_heading.start()

    before = content[:insert_at].rstrip()
    after = content[insert_at:].lstrip("\n")
    inserted = f"{before}\n\n{bullet}\n"
    return inserted if not after else f"{inserted}\n{after}"


def sync_agent_bridge(project: Path) -> Path:
    agent_path = choose_agent_bridge(project)
    if agent_path.exists():
        content = read_text(agent_path)
    else:
        content = "# Agent Instructions\n"

    block_pattern = re.compile(
        rf"{re.escape(AGENT_BRIDGE_START)}.*?{re.escape(AGENT_BRIDGE_END)}",
        re.DOTALL,
    )

    if block_pattern.search(content):
        updated = block_pattern.sub(AGENT_BRIDGE.rstrip(), content)
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
        description="Persist a user-defined rule in .remember_anytime/rules.md."
    )
    parser.add_argument("--project", required=True, help="Project root directory.")
    parser.add_argument("--rule", required=True, help="Rule text to remember.")
    parser.add_argument(
        "--section",
        default="Project Conventions",
        help="Markdown section to append to.",
    )
    parser.add_argument(
        "--no-agent",
        action="store_true",
        help="Do not create or update the AGENT.md bridge.",
    )
    args = parser.parse_args()

    try:
        rule = normalize_rule(args.rule)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    project = Path(args.project).expanduser().resolve()
    if not project.exists() or not project.is_dir():
        print(f"Project directory does not exist: {project}", file=sys.stderr)
        return 2

    remember_dir = project / ".remember_anytime"
    remember_dir.mkdir(exist_ok=True)

    rules_path = remember_dir / "rules.md"
    content = read_text(rules_path) if rules_path.exists() else DEFAULT_CONTENT
    updated = append_to_section(content, args.section.strip(), rule)
    rules_path.write_text(updated.rstrip() + "\n", encoding="utf-8")

    print(f"Remembered rule in: {rules_path}")
    if not args.no_agent:
        agent_path = sync_agent_bridge(project)
        print(f"Updated agent bridge in: {agent_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
