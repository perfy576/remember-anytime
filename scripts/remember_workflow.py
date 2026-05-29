#!/usr/bin/env python3
"""Persist a repeatable workflow under a project's .remember_anytime directory."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


DEFAULT_RULES = """# Remember Anytime Rules

## Coding Workflow

## Coding Standards

## Component And API Rules

## Project Conventions

## Workflow Index
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


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    if not value:
        raise ValueError("Workflow slug must contain at least one ASCII letter or digit.")
    return value[:80]


def choose_agent_bridge(project: Path) -> Path:
    agents_path = project / "AGENTS.md"
    agent_path = project / "AGENT.md"
    if agents_path.exists():
        return agents_path
    if agent_path.exists():
        return agent_path
    return agents_path


def sync_agent_bridge(project: Path) -> Path:
    agent_path = choose_agent_bridge(project)
    content = read_text(agent_path) if agent_path.exists() else "# Agent Instructions\n"
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


def build_template(title: str, triggers: list[str], body: str | None) -> str:
    if body:
        return body.rstrip() + "\n"

    trigger_lines = "\n".join(f"- {trigger}" for trigger in triggers) or "- Add trigger phrases."
    return f"""# {title}

## Trigger Phrases

{trigger_lines}

## Scope

- Describe what this workflow owns.
- Describe what it must not change.

## Inputs

- Add required paths, URLs, browser ports, source files, credentials assumptions, and environment requirements.

## Procedure

1. Add the repeatable steps in execution order.
2. Include stable tool commands or scripts when they reduce ambiguity.

## Output Contract

- Define output paths, formats, naming, sorting, layout, merge, and dedupe rules.

## Validation

- Define checks that must pass before responding.

## Safety Notes

- List destructive actions to avoid, account/session caveats, and approval boundaries.
"""


def ensure_workflow_index(rules_path: Path, slug: str, title: str, triggers: list[str]) -> None:
    content = read_text(rules_path) if rules_path.exists() else DEFAULT_RULES
    heading = "## Workflow Index"
    if heading not in content:
        content = content.rstrip() + f"\n\n{heading}\n"

    trigger_text = "; ".join(triggers) if triggers else "manual trigger"
    bullet = f"- `{slug}`: {title}. Triggers: {trigger_text}. See `.remember_anytime/workflows/{slug}.md`."

    lines = content.splitlines()
    filtered = [
        line for line in lines
        if not line.startswith(f"- `{slug}`:")
    ]
    content = "\n".join(filtered).rstrip() + "\n"

    pattern = re.compile(rf"(^##\s+Workflow Index\s*$)", re.MULTILINE)
    match = pattern.search(content)
    if not match:
        content = content.rstrip() + f"\n\n{heading}\n\n{bullet}\n"
    else:
        next_heading = re.search(r"^##\s+", content[match.end():], re.MULTILINE)
        insert_at = len(content) if next_heading is None else match.end() + next_heading.start()
        before = content[:insert_at].rstrip()
        after = content[insert_at:].lstrip("\n")
        content = f"{before}\n\n{bullet}\n"
        if after:
            content += "\n" + after
    rules_path.write_text(content.rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Persist a repeatable workflow in .remember_anytime/workflows."
    )
    parser.add_argument("--project", required=True, help="Project root directory.")
    parser.add_argument("--slug", required=True, help="Stable workflow slug.")
    parser.add_argument("--title", required=True, help="Human-readable workflow title.")
    parser.add_argument(
        "--trigger",
        action="append",
        default=[],
        help="Trigger phrase. May be passed multiple times.",
    )
    parser.add_argument("--body", help="Workflow Markdown body.")
    parser.add_argument("--body-file", help="Path to a Markdown body file.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing workflow file.")
    parser.add_argument(
        "--no-agent",
        action="store_true",
        help="Do not create or update the AGENT.md/AGENTS.md bridge.",
    )
    args = parser.parse_args()

    project = Path(args.project).expanduser().resolve()
    if not project.exists() or not project.is_dir():
        print(f"Project directory does not exist: {project}", file=sys.stderr)
        return 2

    try:
        slug = slugify(args.slug)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.body and args.body_file:
        print("--body and --body-file cannot be used together.", file=sys.stderr)
        return 2

    body = args.body
    if args.body_file:
        body_path = Path(args.body_file).expanduser().resolve()
        if not body_path.exists() or not body_path.is_file():
            print(f"Body file does not exist: {body_path}", file=sys.stderr)
            return 2
        body = read_text(body_path)
    elif not body and not sys.stdin.isatty():
        stdin_body = sys.stdin.read()
        body = stdin_body if stdin_body.strip() else None

    remember_dir = project / ".remember_anytime"
    workflows_dir = remember_dir / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    workflow_path = workflows_dir / f"{slug}.md"
    if workflow_path.exists() and not args.overwrite:
        print(f"Workflow already exists: {workflow_path}")
        print("Use --overwrite to replace it.")
        return 1

    workflow_path.write_text(
        build_template(args.title.strip(), args.trigger, body),
        encoding="utf-8",
    )
    rules_path = remember_dir / "rules.md"
    ensure_workflow_index(rules_path, slug, args.title.strip(), args.trigger)

    print(f"Remembered workflow in: {workflow_path}")
    print(f"Updated workflow index in: {rules_path}")
    if not args.no_agent:
        agent_path = sync_agent_bridge(project)
        print(f"Updated agent bridge in: {agent_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
