---
name: learn
description: Persist reusable behaviors, guardrails, and procedural knowledge discovered during a session into durable workspace or global customizations. Use when the user says "/learn", "learn from this", "remember this for next time", "make that a rule", "save that as a skill", "turn that into a skill", or right after a correction, a stated constraint, a command that failed and was then fixed, or an environment quirk that should not be rediscovered.
---

# Learn

Turn session-specific corrections and discovered procedures into durable customizations — without ever writing to a customization file before the user approves it.

## Hard rules

1. **Never edit a customization target before approval.** The only write permitted before approval is the new `.learn/learning_proposal.md` document itself.
2. **Never invent a learning.** Every entry must trace to something that actually happened in this session: a user correction, an explicit constraint, a command that failed and then worked, or a verified environment fact. If there is none, say so and stop (Step 2).
3. **Never weaken or delete an existing rule to make room.** A new rule that contradicts an existing one is worse than reporting the conflict.
4. **Never rewrite governance files as a side effect of other work.** This skill exists so the user decides; the agent proposes.
5. **Never claim a change is applied until it is on disk and re-read.**

## Step 1 — Extract candidate learnings

Scan the recent interaction for:

- explicit corrections ("don't do X", "use Y instead", "that's wrong")
- stated constraints, preferences, and definitions
- a failed command plus the change that made it work — record the **cause**, not just the fix
- environment facts about this machine or this repository that were expensive to discover

Drop one-off task details, restatements of the request, and facts already visible in the repository.

For each surviving candidate, capture three things:

| Field | Meaning |
|---|---|
| Trigger | The situation in which it applies |
| Invariant | What must (or must not) happen |
| Evidence | Where in this session it came from |

## Step 2 — Verify necessity

If no candidate is both new and reusable, tell the user what you considered and why each item is not durable, then terminate. Do not create or modify any file, including the proposal.

## Step 3 — Classify: rule or skill

| Learning | Kind | Usual target |
|---|---|---|
| Strict constraint, coding standard, formatting rule, environment trap | Rule | `AGENTS.md` (workspace) or the global rules file |
| Multi-step procedure, tool chain, CLI flags, domain cheatsheet | Skill | `skills/<skill_name>/SKILL.md` |
| Preference about how work should be done | Rule | Same as rule targets |

Two tests decide it:

- **Kind:** "Can a sentence of do/don't fully satisfy this?" → rule. "Does it need ordered steps, exact flags, or reusable code?" → skill.
- **Scope:** "True in every project on this machine?" → global. "Only true for this repository, stack, or team?" → workspace. When scope is genuinely unclear, propose workspace scope and say why.

## Step 4 — Create vs update

Prefer updating. Do not guess at what already exists — inventory it first:

```bash
python scripts/inspect_targets.py --workspace .
python scripts/inspect_targets.py --workspace . --global --topic "<topic>"
```

- Topic already covered by a file → propose a targeted diff into that file.
- Topic entirely unhandled → propose one new file.
- Topic covered by two files → report the split and ask which file owns it instead of adding a third.

## Step 5 — Emit `.learn/learning_proposal.md` and request approval

Write the proposal to **`.learn/learning_proposal.md`** (create `.learn/` if absent), following [references/proposal-format.md](references/proposal-format.md). It must state the target location, the classification and its rationale, the scope, and the **exact** proposed additions as literal text — never "add an appropriate section".

If that file already exists, treat it as an earlier proposal the user never answered: re-read it and ask about it before overwriting. Do not silently discard an unanswered proposal.

Then ask the user to approve, and say what will change on approval. Apply nothing until they answer. If they approve only part of it, apply exactly that part. Record the outcome in the proposal rather than deleting it, so the decision stays auditable.

## Step 6 — Apply and report

After explicit approval:

1. **Re-read each target file immediately before editing.** The user or another agent may have changed it since the proposal was written.
2. Apply exactly the approved text — nothing extra, no bundled cleanups.
3. **Verify:** re-read the edited region; report the file path, the section, and the literal text added; run the format/parse check the file's own toolchain provides, and report its raw output.
4. **Report leftovers:** items deferred, items approved but not applied, and conflicts found along the way.

## Must not do

- Write the proposal and then skip asking.
- Overwrite an unanswered `.learn/learning_proposal.md` instead of raising it.
- Widen an approved change to "while I was in there" edits.
- Promote a one-off instruction to a permanent rule the user did not ask to make permanent.
- Delete a superseded rule silently — propose the replacement and the removal together.
