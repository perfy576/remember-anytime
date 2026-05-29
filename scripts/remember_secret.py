#!/usr/bin/env python3
"""Persist an explicitly requested secret in a project's .remember_anytime directory."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_CONTENT = """# Remember Anytime Secrets

This file stores user-approved secrets and credentials for agent workflows.
Use values only for the requested operation. Do not quote values back unless
the user explicitly requests it and it is necessary.
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


def normalize_name(name: str) -> str:
    name = " ".join(name.strip().split())
    if not name:
        raise ValueError("Secret name cannot be empty.")
    if "\n" in name or "\r" in name:
        raise ValueError("Secret name must be a single line.")
    return name


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


def update_gitignore(project: Path, secret_rel: str) -> Path:
    gitignore = project / ".gitignore"
    entry = "/" + secret_rel.replace("\\", "/")
    content = read_text(gitignore) if gitignore.exists() else ""
    lines = content.splitlines()
    if entry not in lines and secret_rel.replace("\\", "/") not in lines:
        suffix = "\n" if content and not content.endswith("\n") else ""
        gitignore.write_text(content + suffix + entry + "\n", encoding="utf-8")
    return gitignore


def replace_or_append_secret(content: str, name: str, value: str, note: str | None) -> str:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    note_line = f"- Note: {note.strip()}\n" if note and note.strip() else ""
    block = (
        f"## {name}\n\n"
        f"- Updated: {now}\n"
        f"{note_line}"
        "- Value:\n\n"
        "```text\n"
        f"{value.rstrip()}\n"
        "```\n"
    )

    heading_pattern = re.compile(rf"^##\s+{re.escape(name)}\s*$", re.MULTILINE)
    match = heading_pattern.search(content)
    if not match:
        return content.rstrip() + "\n\n" + block

    next_heading = re.search(r"^##\s+", content[match.end():], re.MULTILINE)
    end = len(content) if next_heading is None else match.end() + next_heading.start()
    return content[: match.start()].rstrip() + "\n\n" + block.rstrip() + "\n\n" + content[end:].lstrip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Persist an explicitly user-approved secret in .remember_anytime/secrets.md."
    )
    parser.add_argument("--project", required=True, help="Project root directory.")
    parser.add_argument("--name", required=True, help="Stable secret name.")
    parser.add_argument("--value", help="Secret value. Prefer --value-stdin.")
    parser.add_argument(
        "--value-stdin",
        action="store_true",
        help="Read the secret value from stdin.",
    )
    parser.add_argument("--note", help="Optional non-secret note about usage.")
    parser.add_argument(
        "--track",
        action="store_true",
        help="Do not add .remember_anytime/secrets.md to .gitignore.",
    )
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
        name = normalize_name(args.name)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.value and args.value_stdin:
        print("--value and --value-stdin cannot be used together.", file=sys.stderr)
        return 2
    if args.value_stdin:
        value = sys.stdin.read()
    elif args.value is not None:
        value = args.value
    else:
        print("Provide --value or --value-stdin.", file=sys.stderr)
        return 2
    if not value:
        print("Secret value cannot be empty.", file=sys.stderr)
        return 2

    remember_dir = project / ".remember_anytime"
    remember_dir.mkdir(exist_ok=True)

    secrets_path = remember_dir / "secrets.md"
    content = read_text(secrets_path) if secrets_path.exists() else DEFAULT_CONTENT
    updated = replace_or_append_secret(content, name, value, args.note)
    secrets_path.write_text(updated.rstrip() + "\n", encoding="utf-8")

    print(f"Remembered secret in: {secrets_path}")
    if not args.track:
        gitignore_path = update_gitignore(project, ".remember_anytime/secrets.md")
        print(f"Ensured secret file is ignored in: {gitignore_path}")
    if not args.no_agent:
        agent_path = sync_agent_bridge(project)
        print(f"Updated agent bridge in: {agent_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
