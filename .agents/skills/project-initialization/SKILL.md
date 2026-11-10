---
name: project-initialization
description: >-
  Guides adapting this Python package template into a new project. Use this skill when
  the user asks to initialize, rename, or configure a project created from this
  template. Do not perform initialization unless requested.
---

# Project initialization

Use this checklist when the user requests template initialization. First inspect the
current repository and confirm the intended distribution name, import package name,
repository, supported Python versions, and whether the project will publish to PyPI.

## Adopting this template

When adopting `xozoid/python-template`, resolve the latest full commit SHA from the
template repository's default branch at adoption time. Preserve the target repository's
existing Git history and project-specific configuration. Perform the initialization
checklist below without replacing the target repository or resetting its history.

Record the resolved upstream SHA in `Template-Revision` in the sibling
`.agents/skills/update-from-template/HISTORY.md`. This value identifies the upstream
template commit used for adoption, not a commit in the target repository. Preserve the
target repository's existing history and project-specific configuration. Leave its
history intact and do not create a commit unless the user requests one.

- [ ] Rename the distribution and import package consistently. Rename `new_project/` and
      update imports rather than applying blind text substitutions.
- [ ] Update project metadata and package paths in `pyproject.toml`, including the
      Hatchling wheel package, basedpyright include paths, and coverage source. Review
      the README, tests, and GitHub workflow references to the old package name.
- [ ] Update CI and release workflow references for the package, Python versions, and
      chosen publishing target. Keep package metadata, lockfiles, CI, and hooks aligned.
- [ ] Update npm package metadata in `package.json` and regenerate `package-lock.json`
      with npm when metadata or dependencies change.
- [ ] Update README badges and repository URLs, plus any repository references in
      contributor or release documentation.
- [ ] If publishing to PyPI, configure trusted publishing for the repository and
      publishing workflow. Review the `pypi` GitHub environment and workflow URL/name.
      Skip this step for projects that do not publish to PyPI.
- [ ] Verify the renamed package builds and imports from the built wheel, and update or
      run tests and checks using the commands documented in `CONTRIBUTING.md`.

After adoption is complete, replace the placeholder `Template-Revision` in `HISTORY.md`
with the full upstream SHA resolved at the start. Do not edit the update skill's
instructions or alter the target repository's existing history.

Do not rename files, change metadata, or configure publishing without a user request.
Resolve any project-specific choices from the request or ask only for details that
cannot be inferred safely.
