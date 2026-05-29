# Built-In Workflows

## doublecheck

Trigger phrases:

- `doublecheck`
- `double-check`
- `再检查一下`
- `再核对一遍`

Goal:

- Re-audit the current task from the full conversation history and current workspace state.
- Ignore earlier conclusions unless they are re-proven by current evidence.

Procedure:

1. Reconstruct the original objective from the full thread, including any later clarifications.
2. Inspect the current workspace state, relevant diffs, generated artifacts, validation output, and commit status.
3. Check for missing requirements, wrong file targets, skipped validation, stale docs, or uncommitted follow-up work.
4. Separate proven facts from assumptions.
5. If a gap exists, reopen the task and continue modifying until the gap is closed or a blocker is proven.
6. If the task is complete, report the remaining evidence succinctly.

Output contract:

- Findings first.
- Then the concrete evidence used.
- Then any remaining risks or follow-up work.

Safety:

- Do not discard user changes.
- Do not treat the previous answer as evidence by itself.
- Do not stop at a plausible summary; require current-state proof.
- Do not end the workflow while a verified gap still exists.

## workflow-solidify

Trigger phrases:

- `固化 X 流程`
- `把 X 流程固化下来`
- `记住 X 流程`
- `save X workflow`

Goal:

- Create or update `.remember_anytime/workflows/<slug>.md`.

Procedure:

1. Extract the stable trigger phrases.
2. Capture scope, inputs, procedure, output contract, validation, and safety notes.
3. Write the workflow file and update the workflow index.

## workflow-use

Trigger phrases:

- `使用 X 流程`
- `执行 X 流程`
- `运行 X 流程`
- `按 X 流程来`
- `use/run X workflow`

Goal:

- Find the best-matching saved workflow and execute it.

Procedure:

1. Search `.remember_anytime/workflows/` and the workflow index in `rules.md`.
2. Load the most specific match.
3. Follow its Procedure and Validation sections.
4. If multiple matches remain, ask the user to choose.
