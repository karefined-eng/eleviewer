# learning_proposal.md format

Written to `.learn/learning_proposal.md`. The proposal is the only artifact written before approval. Keep it reviewable: a human must be able to approve or reject it without opening any other file.

An approved or rejected proposal is annotated with the outcome, not deleted — the file is the record of what was proposed and what was decided.

## Table of contents

- [Required sections](#required-sections)
- [Writing the exact additions](#writing-the-exact-additions)
- [Diff conventions](#diff-conventions)
- [Worked example](#worked-example)

## Required sections

Write these sections in this order. Omit a section only when it would be empty — never leave a placeholder.

### 1. Target Location

One line per change, as a concrete path:

```
- Workspace: AGENTS.md  (section: "PowerShell on Windows")
- Workspace: skills/parse-drawio/SKILL.md  (new file)
```

Use the path the inventory actually found. A workspace that keeps its rules in `.cursor/rules/`, `.clinerules/`, `RULES.md`, or a `rules/` directory is targeted there instead of in `AGENTS.md` — do not create a second rule file merely because the examples here mention `AGENTS.md`.

Mark global targets explicitly (`Global: ~/AGENTS.md`) and say why the learning is not workspace-specific.

### 2. Classification & Rationale

For each change: kind (rule or skill), scope (global or workspace), and the one or two sentences that justify both. Ground it in evidence.

```
Kind: rule — a single do/don't covers it, no ordered steps needed.
Scope: workspace — depends on this repository's PowerShell-only toolchain.
Evidence: the user corrected `bash make.sh` to `.\make.ps1` at turn 12;
          the shell here is PowerShell 5.1.
```

### 3. Scope

What the learning applies to, and — when it matters — what it explicitly does not. Naming the boundary prevents a narrow fix from being read as a general law.

### 4. Proposed Additions

The exact text to be inserted. See below.

### 5. Conflicts and Alternatives

- Any existing rule this contradicts or supersedes, quoted.
- The update-not-create path considered, and why it was not taken.
- Anything deliberately left out and why.

### 6. Verification Plan

How correctness will be shown after approval: which file was re-read, which format/parse check ran, and what its output was. For a skill, include running any bundled script at least once.

## Writing the exact additions

- Give **literal final text**, in the form it will appear in the file, as a fenced block.
- For an addition into an existing file, give an unambiguous anchor: quote the surrounding heading or line, and state before/after.
- Match the target file's own conventions — its heading depth, list style, and language. Do not impose this document's style on it.
- Prefer the smallest text that fully states the invariant. A rule the user skims past does not work.

## Diff conventions

| Situation | How to present |
|---|---|
| New file | Full intended content in one fenced block |
| Insert into existing section | `anchor:` quoted line, then `+` literal lines |
| Replace existing rule | `-` old literal text, `+` new literal text, with the old text quoted exactly |
| Remove a superseded rule | `-` the exact text, plus the replacement that justifies removal |

Never write `<!-- TODO -->`, `...`, or "similar to above" inside proposed text.

## Worked example

```markdown
## Target Location
- Workspace: AGENTS.md  (new section: "Shell", inserted after "Build")

## Classification & Rationale
Kind: rule — a single do/don't ("invoke python, not python3") states it fully.
Scope: workspace — this machine's PATH exposes `python` only.
Evidence: `python3 --version` failed with CommandNotFoundException at turn 4;
          `python --version` returned 3.13.15 and every later command used it.

## Scope
Applies to all commands run in this workspace. Does not apply to CI configs
outside this repository.

## Proposed Additions
anchor:
```
## Build

<\!-- keep this comment out of the proposal -->
```

text to insert before that anchor:

+ ## Shell
+
+ Invoke `python`, never `python3` or `py` — only `python` is on PATH.

## Conflicts and Alternatives
No existing rule mentions interpreters. Create-instead-of-update was rejected:
AGENTS.md already owns "how commands are run here".

## Verification Plan
Re-read the "Shell" section after the edit and print the inserted lines.
No parser applies to Markdown; confirm the file's other headings still nest correctly.
```
