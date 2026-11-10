---
name: update-from-template
description: >-
  Updates a project adopted from xozoid/python-template while preserving
  project-specific code, configuration, and intentional deviations.
---

# Update from template

Read `.agents/skills/update-from-template/HISTORY.md` for the template source, last
applied revision, and persistent list of intentionally skipped changes. Keep that file
as the only template tracking record. Do not edit this `SKILL.md` during an update.

## Update workflow

1. Read the source and last applied full commit SHA from `HISTORY.md`. Resolve the
   template repository's default branch and its current full commit SHA. Fetch the
   upstream template and verify that the recorded revision exists there.
2. Compare the recorded revision with the current default-branch revision. If they are
   identical, report that no update is needed and leave `HISTORY.md` unchanged. If the
   target revision does not descend from the recorded revision, report divergence and
   stop before applying changes.
3. Review the template changes between the recorded and target revisions. Compare the
   affected files with the project, then apply relevant changes in context. Preserve
   project-specific code, metadata, dependencies, configuration, CI customizations, and
   intentional deviations. Never overwrite uncommitted changes or discard local edits.
4. For intentionally skipped changes, record the affected paths, the template revision
   where each change was first skipped, a short description, and the reason in
   `HISTORY.md`. During every later update, check whether new changes touch the same
   paths or behavior, or depend on a skipped change. Review the template evolution from
   the recorded skip revision through the new target revision to see whether later work
   builds on, replaces, or invalidates the skip. Reconsider the local adaptation when
   needed; do not treat a skip as a permanent instruction to ignore that area. Update
   the history entry with the result after a successful migration.
5. Run relevant tests, linting, formatting, dependency locking, and pre-commit
   synchronization checks. Review generated changes and resolve conflicts with the
   project's conventions.
6. Only after the applicable migration is complete and checks succeed, update
   `HISTORY.md` with the full target template SHA and any intentional skips. Do not
   automatically commit changes unless the user explicitly requests a commit.

## Finding an initial revision

If the revision in `HISTORY.md` is unset or still contains a placeholder, compare the
project's initial state with the template's history and use file contents and timestamps
only as supporting evidence. Do not select a revision solely because it looks like the
closest match. If the origin cannot be identified confidently, describe the candidate
revisions and ask the user to confirm before updating.

## Report

Report the target template revision, applied changes, skipped changes and reasons,
conflicts, and validation results. State clearly when no update was needed or when
divergence or an ambiguous starting revision prevented an update. If a commit is
requested, use a clear summary. Update `HISTORY.md` only when a template migration has
completed successfully; leave it unchanged for a no-op, failed, or incomplete update.
