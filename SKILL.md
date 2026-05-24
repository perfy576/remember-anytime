---
name: remember-anytime
description: Persistently load, create, update, and enforce project rules stored in a `.remember_anytime` folder, and maintain an AGENT.md bridge so future agents know when to read those rules. Use when Codex works in a repository that has or should have durable agent instructions, coding standards, component usage rules, architectural constraints, build requirements, server/log/deployment runbooks, remote host information, platform-specific handling, web/mobile/desktop differences, project conventions, or user-defined rules that must survive context compaction; use when the user asks to inspect logs, use server information, deploy, debug remote behavior, code for web or multi-platform apps, remember something permanently, says future agents must always obey a rule, mentions remember_anytime, `.remember_anytime`, AGENT.md instructions not being followed, "always remember", "from now on", persistent project rules, coding norms, component conventions, or project agreements.
---

# Remember Anytime

Use this skill to make user-defined project rules durable and re-loadable. The project source of truth is `.remember_anytime/` at the project root, normally with `rules.md` plus optional function-specific files.

This skill improves automatic recognition in two ways:

1. The skill description contains broad trigger terms for coding, logs, servers, deployment, multi-platform, web, UI, and permanent memory tasks.
2. The scripts maintain a short `AGENT.md` bridge that tells future agents to read `.remember_anytime/` when those workflows appear.

This is persistence, not conversation memory. When the user asks Codex to remember a rule permanently, write it to disk so a future agent can reload it after context compaction or in a new session.

## Required Workflow

1. Resolve the project root before making changes. Prefer the current working directory unless the user names a project subdirectory.
2. Look for `.remember_anytime/` at the project root. If it does not exist and the task is to initialize persistent rules, create it with `scripts/init_remember_anytime.py`.
3. Read every Markdown file directly under `.remember_anytime/` before planning or editing project code.
4. Treat these files as mandatory project constraints for the whole turn. Re-read them after context transitions, long pauses, or when resuming work.
5. Before editing code, explicitly map the relevant rule(s) to the files or behavior being changed.
6. If a user request conflicts with `.remember_anytime` rules, surface the conflict and ask for confirmation before proceeding.
7. After editing code, run the validation required by `.remember_anytime` rules. If validation cannot run, report the reason.

## Automatic Workflow Matching

When this skill is triggered, classify the user's task and search the loaded `.remember_anytime` files for relevant rules before acting.

- Server/log tasks: if the user asks about logs, server status, deployment, SSH, production, remote debugging, backend errors, or "go check the server", look for server host details, login method, log paths, service names, deploy commands, and safety rules in `.remember_anytime/`.
- Coding tasks: if the user asks to edit, refactor, fix, add, remove, compile, test, or review code, load coding workflow, architecture, validation, and forbidden-pattern rules.
- Platform tasks: if the project has web/mobile/desktop variants or the user mentions web, browser, Flutter web, mobile, desktop, Windows, macOS, Linux, Android, or iOS, load platform-specific rules and apply the relevant branch before editing.
- UI/component tasks: if the user mentions UI, page, component, theme, style, layout, localization, copy, or interaction, load UI, component, theme, and l10n rules.

If a `.remember_anytime` file contains server credentials or sensitive connection details, use them only to perform the requested operation. Do not quote secrets back to the user unless explicitly requested and necessary.

## Remembering New Rules

When the user says to remember a command, rule, convention, decision, preference, or constraint permanently, write it to `.remember_anytime/rules.md` in the relevant project.

Trigger phrases include:

- "记住"
- "永远记住"
- "以后都要"
- "不要忘记"
- "这是一条规则"
- "把这个作为项目约定"
- "后续都遵守"
- "always remember"
- "from now on"

Do not only acknowledge the instruction in chat. Persist it to disk unless the user explicitly says not to modify files.

Save only stable, reusable rules. Do not persist one-off task details, temporary debugging observations, secrets, credentials, or instructions that are clearly limited to the current turn.

Use the helper script:

```powershell
python .\scripts\remember_rule.py --project <project-root> --rule "<rule text>" --section "Coding Standards"
```

By default, this also creates or updates the project `AGENT.md` bridge. Use `--no-agent` only when the user explicitly does not want `AGENT.md` touched.

If the rule is ambiguous, ask one concise clarification before saving it. If the target project is ambiguous, use the current working directory.

After saving, tell the user which file changed and summarize the exact rule that was persisted.

## Initialization

Run the script from this skill directory:

```powershell
python .\scripts\init_remember_anytime.py --project <project-root>
```

To migrate an existing instruction file:

```powershell
python .\scripts\init_remember_anytime.py --project <project-root> --source <project-root>\AGENT.md
```

Useful options:

- `--append`: append migrated rules to an existing `.remember_anytime/rules.md`.
- `--overwrite`: replace an existing `.remember_anytime/rules.md`.
- `--title`: set the heading in the generated rules file.
- `--no-agent`: do not create or update the `AGENT.md` bridge.

## Rule File Shape

Keep rules short, imperative, and concrete. Prefer sections like:

- `Coding Workflow`
- `Architecture`
- `UI Components`
- `Localization`
- `Build And Validation`
- `Server Logs And Deployment`
- `Platform Specific Rules`
- `Known Critical Paths`

Put long explanations in separate Markdown files under `.remember_anytime/` and link them from `rules.md`.

For better automatic matching, split durable knowledge by function when it grows:

- `.remember_anytime/rules.md`: global rules that always apply.
- `.remember_anytime/server.md`: server hosts, log locations, SSH/deploy commands, and operational safety rules.
- `.remember_anytime/platforms.md`: web/mobile/desktop differences and platform-specific coding requirements.
- `.remember_anytime/ui.md`: component, theme, localization, and interaction rules.

## Enforcement Notes

- Do not assume `AGENT.md`, `agent.md`, or similar files will always be enough. Use it as a short bridge into `.remember_anytime/`, not as the long-term source of truth.
- Do not bury critical rules in conversation summaries. The durable copy belongs in `.remember_anytime/`.
- Do not rely on having seen the rule earlier in the same conversation. Re-read `.remember_anytime/` whenever this skill is invoked for a project task.
- When changing persistent rules, edit `.remember_anytime/` directly and keep the rule wording precise enough that a future agent can apply it without context from the original conversation.
- Be explicit in final responses when a new rule has been persisted, including the path that was changed.
