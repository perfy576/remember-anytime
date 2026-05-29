---
name: remember-anytime
description: Persistently load, create, update, and enforce project rules, secrets, credentials, and reusable workflows stored in `.remember_anytime`, and maintain an AGENT.md/AGENTS.md bridge. Use when a repository needs durable agent instructions, coding standards, component/API rules, architecture constraints, build/deploy/server runbooks, platform rules, project conventions, remembered API keys/passwords/usernames, or workflows; use when the user asks to remember something permanently, solidify a repeatable process, save/use/run a workflow, says future agents must obey a rule, mentions remember_anytime, `.remember_anytime`, AGENT.md/AGENTS.md, "always remember", "from now on", "固化xx流程", "使用xx流程", or "执行xx流程".
---

# Remember Anytime

Use this skill to make user-defined project rules and repeatable workflows durable and re-loadable. The project source of truth is `.remember_anytime/` at the project root, normally with `rules.md`, optional function-specific files, and optional workflow files under `.remember_anytime/workflows/`.

This skill improves automatic recognition in two ways:

1. The skill description contains broad trigger terms for coding, logs, servers, deployment, multi-platform, web, UI, and permanent memory tasks.
2. The scripts maintain a short `AGENT.md` or `AGENTS.md` bridge that tells future agents to read `.remember_anytime/` when those workflows appear.

This is persistence, not conversation memory. When the user asks Codex to remember a rule permanently, write it to disk so a future agent can reload it after context compaction or in a new session.

## Required Workflow

1. Resolve the project root before making changes. Prefer the current working directory unless the user names a project subdirectory.
2. Look for `.remember_anytime/` at the project root. If it does not exist and the task is to initialize persistent rules, create it with `scripts/init_remember_anytime.py`.
3. Read every Markdown file directly under `.remember_anytime/` before planning or editing project code.
4. If the user asks to repeat, update, continue, or automate a named workflow, read matching Markdown files under `.remember_anytime/workflows/` before acting.
5. Treat these files as mandatory project constraints for the whole turn. Re-read them after context transitions, long pauses, or when resuming work.
6. Before editing code, explicitly map the relevant rule(s) to the files or behavior being changed.
7. If a user request conflicts with `.remember_anytime` rules or workflows, surface the conflict and ask for confirmation before proceeding.
8. After editing code, run the validation required by `.remember_anytime` rules. If validation cannot run, report the reason.

## Automatic Workflow Matching

When this skill is triggered, classify the user's task and search the loaded `.remember_anytime` files for relevant rules before acting.

- Server/log tasks: if the user asks about logs, server status, deployment, SSH, production, remote debugging, backend errors, or "go check the server", look for server host details, login method, log paths, service names, deploy commands, and safety rules in `.remember_anytime/`.
- Coding tasks: if the user asks to edit, refactor, fix, add, remove, compile, test, or review code, load coding workflow, architecture, validation, and forbidden-pattern rules.
- Platform tasks: if the project has web/mobile/desktop variants or the user mentions web, browser, Flutter web, mobile, desktop, Windows, macOS, Linux, Android, or iOS, load platform-specific rules and apply the relevant branch before editing.
- UI/component tasks: if the user mentions UI, page, component, theme, style, layout, localization, copy, or interaction, load UI, component, theme, and l10n rules.
- Repeatable workflow tasks: if the user asks to repeat a previous workflow, update a generated artifact from fresh data, sync a catalog, refresh a report, reuse a prompt, or says "固化流程"/"以后用一句提示词", search `.remember_anytime/workflows/` by filename, title, trigger phrases, and described outputs.

## Prompt Intent Routing

Treat workflow prompts as direct actions:

- `固化 X 流程`, `把 X 流程固化下来`, `记住 X 流程`, `save X workflow`: create or update `.remember_anytime/workflows/<x>.md`. If the process is underspecified, ask one concise clarification or save a template with known facts and TODOs.
- `使用 X 流程`, `执行 X 流程`, `运行 X 流程`, `按 X 流程来`, `use/run X workflow`: search `.remember_anytime/workflows/` and `rules.md` workflow index for `X`, load the best match, then execute its Procedure and Validation sections.
- If multiple workflows match, list the matching workflow names and ask the user to choose. If none match, say no saved workflow was found and offer to solidify one.

## Built-In Workflows

- `doublecheck`: re-audit the task from the full conversation history and current workspace state, ignore prior assumptions, and look for missing requirements, incorrect file targets, weak evidence, skipped validation, or inconsistent output. Read `references/builtin-workflows.md` for the execution pattern.
- `固化 X 流程` / `使用 X 流程`: treat these as workflow-management commands, not ordinary edits; use the workflow save/run routing above.

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

Save only stable, reusable rules. Do not persist one-off task details, temporary debugging observations, or instructions that are clearly limited to the current turn.

Use the helper script:

```powershell
python .\scripts\remember_rule.py --project <project-root> --rule "<rule text>" --section "Coding Standards"
```

By default, this also creates or updates the project `AGENT.md` or `AGENTS.md` bridge. Use `--no-agent` only when the user explicitly does not want the bridge touched.

If the rule is ambiguous, ask one concise clarification before saving it. If the target project is ambiguous, use the current working directory.

After saving, tell the user which file changed and summarize the exact rule that was persisted.

## Remembering Sensitive Information

When the user explicitly asks to remember a key, password, username, token, credential, host login, or other secret, persist it. Do not refuse solely because it is sensitive.

Use a dedicated secret file instead of ordinary rules:

```powershell
python .\scripts\remember_secret.py --project <project-root> --name "<secret name>" --value-stdin
```

Default storage is `.remember_anytime/secrets.md`. Treat that file as sensitive operational memory:

- Use saved secrets only to perform the requested operation.
- Do not quote secret values back to the user unless explicitly requested and necessary.
- Prefer `--value-stdin` over command-line `--value` to avoid shell history leaks.
- If the user asks for shared/team/committed credentials, save them as requested. Otherwise, recommend keeping `.remember_anytime/secrets.md` local or ignored by git.
- If a project already has a preferred secret store, record a pointer or retrieval instruction in `.remember_anytime/secrets.md`.

## Remembering Reusable Workflows

When the user asks to solidify a process, make a prompt reusable, or ensure a future agent can repeat a completed workflow, save a workflow file under `.remember_anytime/workflows/`.

Save workflows for repeatable procedures, not one-off observations. Good candidates include browser automation procedures, data refreshes, report generation, AI-assisted content pipelines, deployment runbooks, import/export tasks, and artifact update flows.

Use the helper script:

```powershell
python .\scripts\remember_workflow.py --project <project-root> --slug <workflow-slug> --title "<workflow title>" --trigger "<trigger phrase>" --body-file <workflow.md>
```

Workflow files should be concise and executable by a future agent without conversation context. Prefer this shape:

- `# <Workflow Title>`
- `## Trigger Phrases`: user phrases that should load this workflow.
- `## Scope`: what the workflow owns and what it must not change.
- `## Inputs`: required paths, browser ports, URLs, credentials assumptions, or source files.
- `## Procedure`: concrete steps in order, including tools and commands when stable.
- `## Output Contract`: exact output files, layout, naming, sorting, and merge/dedupe rules.
- `## Validation`: checks to run before responding.
- `## Safety Notes`: permissions, destructive actions to avoid, account/session caveats.

When updating an existing workflow, preserve stable trigger phrases and output contracts unless the user explicitly changes them.

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
- `--no-agent`: do not create or update the `AGENT.md` or `AGENTS.md` bridge.

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
- `.remember_anytime/secrets.md`: user-approved keys, passwords, usernames, tokens, credentials, or retrieval instructions.
- `.remember_anytime/workflows/<slug>.md`: repeatable workflow instructions loaded only when the task matches their trigger phrases.

## Enforcement Notes

- Do not assume `AGENT.md`, `AGENTS.md`, `agent.md`, or similar files will always be enough. Use it as a short bridge into `.remember_anytime/`, not as the long-term source of truth.
- Do not bury critical rules in conversation summaries. The durable copy belongs in `.remember_anytime/`.
- Do not rely on having seen the rule earlier in the same conversation. Re-read `.remember_anytime/` whenever this skill is invoked for a project task.
- When changing persistent rules, edit `.remember_anytime/` directly and keep the rule wording precise enough that a future agent can apply it without context from the original conversation.
- Be explicit in final responses when a new rule has been persisted, including the path that was changed.
