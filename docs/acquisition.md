# Git acquisition

The scan reads a commit range, not the whole history. It runs Gitleaks
with these log options:

    BASE..HEAD --text --no-ext-diff --no-textconv --no-renames
    --diff-merges=first-parent

Each option closes a measured bypass:

- --text exposes content that a .gitattributes entry marked binary.
- --no-ext-diff and --no-textconv stop external diff drivers.
- --no-renames makes a rename visible as a delete and an add, so a
  credential moved out of an allowlisted path stays visible.
- --diff-merges=first-parent gives merge commits a stable patch shape.

A first-parent merge diff re-adds content inherited from the target base
at a clean merge. The scan therefore reports JSON and attributes each
merge finding to the merge commit's direct parents. It drops a finding
only when the same path and a contiguous line span are proven inherited
unchanged from at least one direct parent. A finding on genuinely new
merge-resolution lines stays effective. A parent that is missing, is not
a regular file, or is a symlink cannot prove inheritance.

A trusted receipt wrapper records whether the real Git acquisition calls
completed. The scan captures the runner Git path before it changes PATH.
The wrapper records the return status of every log and cat-file call. A
receipt that is missing, is incomplete, or records a failed acquisition
call refuses the scan.

The exit contract is:

- 0: complete acquisition, zero effective findings.
- 1: credential findings.
- 2: a missing or incomplete acquisition receipt, or an unset range.
- 3: a missing, empty, malformed or contradicted report.

A missing or empty report is a report error, not an acquisition error,
and its message says so. The report stays a private, redacted temporary
file outside the checkout; no artifact is uploaded.
