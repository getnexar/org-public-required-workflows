# secret-scan

Public source for the secret-scan required check. This workflow runs as
a repository-required workflow for repositories that cannot resolve an
internal required-workflow source.

It is a prepared release artifact. Publishing it to a fresh public
repository, applying organization targeting, and proving the live gate
are separate work. Local results here do not establish organization
coverage.

## What the check does

The check runs on pull_request events. It scans only the commits the
pull request introduces, using a pinned Gitleaks 8.28.0 binary and the
pinned default ruleset. It refuses an empty or unresolvable commit
range. It separates a tool failure from a credential finding: a tool,
ruleset or report failure exits with a distinct nonzero status, while a
credential finding exits 1 and prints a redacted explanation.

## Configuration boundary

- The ruleset is the Gitleaks default. This release carries no
  per-repository allowlist and no per-repository exception data.
- The ruleset is written to a private runner temporary path and passed
  with --config, outside the scanned checkout. A repository-supplied
  .gitleaks.toml cannot select or extend it.
- GITLEAKS_CONFIG is unset in the pin step and emptied in the scan step.
- A repository-supplied .gitleaksignore file is removed from the working
  tree before the scan. The file stays in history and the scanned range
  is unchanged.
- No script from the scanned repository executes. The attribution helper
  runs under python3 -I, so the scanned repository cannot shadow json,
  subprocess, pathlib or sitecustomize.

## Detection boundary

The job pins Gitleaks 8.28.0 and verifies the Linux x64 archive checksum
before execution. A canary must detect the expected fixture and rule
identities, not an arbitrary finding count. The pin step refuses a
missing, empty, malformed or stale canary report and refuses when the
pinned rules did not load.

Git acquisition keeps text mode, no external diff, no textconv, no
rename detection and first-parent merge diffs. A merge finding is
dropped only when the same path and a contiguous line span are proven
inherited unchanged from at least one direct parent. See
docs/acquisition.md.

## Known limit: inline suppression markers

Gitleaks honors an inline gitleaks:allow marker on the same line and
suppresses that finding. This release preserves that behavior; it does
not change it. The check therefore does not claim unconditional
prevention of every credential. It proves that the selected scanner
policy ran and that the pinned rules loaded.

## Reporting a finding

Do not paste a detected value into a pull request, an issue, or a chat
channel. Treat it as compromised and rotate it. Remove it from the
branch by amending or rewriting the commits that carry it; deleting it
in a later commit is not enough, because it stays in the branch history.
Report the exposure through your organization's internal security
process, not a public issue.

## Release boundary and updates

This directory is a prepared publication candidate. Approval to publish
depends on a recorded, independent review of every exported byte.
docs/release.md records how it is reconstructed, how published bytes are
compared, and how an update is reviewed and published without bypass.
