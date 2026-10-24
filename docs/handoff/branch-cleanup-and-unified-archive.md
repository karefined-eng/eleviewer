# Branch Cleanup & `unified` Archive — 2026-10-24

## What happened

The repository accumulated stale branches from past agent sessions and one
historical branch holding content that no longer exists anywhere else. All
branches were audited against `main` and cleaned up. Verified state after
cleanup: **local** = `main` only; **remote** = `main` only; tags untouched.

## Deleted branches (all verified fully merged, zero unique commits)

| Branch | Was at | Note |
|---|---|---|
| `%karefined-eng%-redesigned-pancake` (local) | `e8daa2f` | v1.3.6 prep, 2 behind main |
| `%karefined-eng%-scaling-dollop` (local) | `4a2477f` | dup of onboarding-update |
| `%karefined-eng%-stunning-adventure` (local) | `4f907a1` | welcome onboarding work, merged |
| `elevonprospera-eng-commit-onboarding-update` (local + remote) | `4a2477f` | merged |
| `elevonprospera-eng-package-size-optimization` (local) | `0f5f9c7` | 15 behind main, merged |

Deletions used `git branch -d` (safe mode — refuses unmerged work) and
`git push origin --delete`; GitHub accepted all of them. No open PRs
referenced any branch at deletion time (checked via `gh pr list --state all`).

## The `archive/unified-skills` tag (IMPORTANT — do not lose)

The remote branch `unified` was **not** simply deleted. Its tree was identical
to the old `eleviewer` branch state (`ca6b9d3`) which is in main's history —
but main **subsequently deleted that content**, so `unified` was the only
surviving copy of ~583 files / ~63,600 lines. It was preserved as the tag
`archive/unified-skills` (pushed to origin) before the branch was removed.

### What the archive contains (last touched 2026-07-31)

- `.agents/skills/FaFi/` — AI-automation suite: adapters for Claude, ChatGPT
  Codex, Google ecosystem, Microsoft 365 Copilot, HubSpot, Perplexity, Manus,
  Abacus AI; connectors (Google Ads, Make.com, WhatsApp Business, sipgate,
  Ricoh360); research/content-creator agents; its own npm backend (dependabot
  PRs #52–57, #86 targeted it).
- `.agents/skills/ponytail-*` family (audit, debt, gain, help, review) plus
  `eleviewer-seo-geo`, `eleviewer-ui-tester`, `eleviewer-workstation-dev`,
  `github-gem-seeker`, `internet-skill-finder`.
- `LICENSE_GPL.txt` / GPL-3.0 license sync.

### How to resurrect

```bash
git branch unified archive/unified-skills   # recreate locally
git push origin unified                     # recreate on remote, if ever needed
```

## Decision record

If the FaFi/ponytail skills ecosystem is ever declared dead for good, the tag
can be deleted too — but that erases the last copy of that content, so it
should be an explicit decision, not housekeeping.
