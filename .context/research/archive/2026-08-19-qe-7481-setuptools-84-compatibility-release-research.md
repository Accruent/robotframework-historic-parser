# QE-7481 Research: Setuptools 84 Compatibility and Historic Parser Release

Research date: 2026-08-19
Ticket: [QE-7481](https://accruent.atlassian.net/browse/QE-7481)
Status: Develop
Research status: Complete historical baseline; final execution outcome is recorded in the addendum below. Production code and tests were not modified during research.

## Final Execution Addendum

The research sections below capture the repository and Jira state observed before implementation. Their descriptions of the old dependency, CI matrix, open PR, release-notes field, open questions, proposed next steps, and blockers are historical research context rather than remaining work items.

Final execution outcome on 2026-08-19:

- `requirements.txt` uses `setuptools~=84.0.0`; `setup.py` declares `python_requires='>=3.10'`; and `version.py` declares `VERSION = "0.2.2"`.
- The workflow validates quoted Python 3.10 through 3.14 values, excludes Python 3.9, uses `actions/checkout@v7` and `actions/setup-python@v6`, and performs the installed-metadata assertion.
- Implementation commit `0cbeb80` was pushed to the reused PR branch after the package and workflow changes passed review.
- PR [#156](https://github.com/Accruent/robotframework-historic-parser/pull/156) merged into `master` at `72bd45e67a9c892accb5717d9cb917f6ebddd84a` after all five matrix jobs passed in [Actions run 32295175795](https://github.com/Accruent/robotframework-historic-parser/actions/runs/32295175795).
- Annotated tag `v0.2.2` and the published [GitHub release](https://github.com/Accruent/robotframework-historic-parser/releases/tag/v0.2.2) both target `72bd45e67a9c892accb5717d9cb917f6ebddd84a` and contain maintenance notes.
- Python 3.10 was unavailable locally, so no local 3.10 installation or test pass is claimed. A separate Python 3.14 local suite invocation returned `46 passed, 10 failed` because the installed `mysql.connector` namespace lacked `connect`; the successful GitHub matrix is the authoritative compatibility result.
- The QE-7481 release-notes custom field remained unchanged by decision because this is an internal, non-public-facing release. The installed `acli` also rejected arbitrary custom-field updates. The field decision is non-blocking; repository and GitHub release evidence are authoritative.
- QE-7459 remains in `Develop`; it is the remaining external dependency for final QE-7481 closure.

## Context Format and Naming

The repository did not contain a `.context` directory when this research started. A tracked-file search found no prior context or research documents, and `.gitignore` does not ignore `.context`. There is therefore no repository-local format or naming convention to reproduce.

This document used a conservative date-prefixed name and was initially stored in `research/current`; it is now archived in `research/archive` after execution:

`2026-08-19-qe-7481-setuptools-84-compatibility-release-research.md`

The path can be moved if the repository later adopts a different shared context convention.

## Ticket Summary

QE-7481 is a Story in the Quality Engineering project with the summary **Admin | Resolve setuptools 84.0.0 compatibility and release historic parser**.

- Assignee and reporter: Neil Howell
- Status: Develop (In Progress category)
- Component: Overhead
- Labels: `dependencies`, `release`, `robotframework-historic-parser`
- Priority: Not Set
- Parent and epic link: [QE-7279](https://accruent.atlassian.net/browse/QE-7279), `2026 QE Admin Work`
- Created: 2026-08-19 12:50:09 -05:00
- Updated/status-category change: 2026-08-19 13:00:34 -05:00

## Objective and Requirements

The ticket was created after GitHub PR [#156](https://github.com/Accruent/robotframework-historic-parser/pull/156) attempted to update `setuptools` from `~=82.0.1` to `~=84.0.0`. Setuptools 84 requires Python 3.10 or later, so the existing Python 3.9 CI job cannot resolve the dependency.

The requested modernization and release work is:

1. Remove Python 3.9 from the supported test matrix.
2. Declare Python `>=3.10` in package metadata.
3. Support and validate Python 3.10, 3.11, 3.12, 3.13, and 3.14.
4. Update the direct setuptools requirement to `setuptools~=84.0.0`.
5. Make package installation succeed with setuptools 84 on every supported Python version.
6. Update the package version from `0.2.1` to `0.2.2`.
7. Create the GitHub tag and release `v0.2.2` from the merged `master` commit, with maintenance release notes.
8. Record the local test command and result, GitHub Actions run URL, final PR status, and release URL in Jira.

The acceptance criteria are embedded in the main Jira description. The dedicated Acceptance Criteria field (`customfield_10035`) and Test Plan field (`customfield_10183`) were empty in the all-fields response.

## Jira Comments and Decisions

The all-fields Jira response returned no comments (`comment.total = 0`), no issue links (`issuelinks` is empty), no subtasks, and no worklogs. The parent relationship is present through both the parent field and epic-link field `customfield_10014 = QE-7279`.

The main description is the available decision record:

- The Python 3.9 support decision is intentional, not a temporary CI workaround.
- The supported matrix is explicitly Python 3.10 through 3.14.
- PR #156 should be resolved or superseded as part of the modernization.
- The version bump and release are part of the same validated change.
- Release evidence must be added back to the ticket.

At research time, the Jira release-notes field (`customfield_11748`) contained the placeholder `NO RELEVANT FUNCTIONALITY FOR RELEASE NOTES (edit this if there is)`, which appeared to conflict with the then-understood acceptance criterion requiring maintenance release notes. Final execution established that this field is non-blocking for the internal release and it was intentionally left unchanged; the GitHub release contains the authoritative maintenance notes.

## Linked GitHub PR Evidence

PR [#156](https://github.com/Accruent/robotframework-historic-parser/pull/156) was read through the GitHub API on 2026-08-19.

- Title: `Update setuptools requirement from ~=82.0.1 to ~=84.0.0`
- State: Open, not draft, not merged; GitHub reports it as mergeable.
- Base/head: `master` / `dependabot/pip/setuptools-approx-eq-84.0.0`
- Head commit: `4506bc2efceeb35259baf91b37f681ed7063bd43`
- Changed files: only `requirements.txt`, one line added and one removed.
- Review and issue comments: none returned.
- Check results: `run-tests (3.9)` failed; `run-tests (3.12)` passed; `run-tests (3.10)` and `run-tests (3.11)` were cancelled. The combined commit status was still pending.

The corresponding remote branch commit changes only:

```diff
-setuptools~=82.0.1
+setuptools~=84.0.0
```

That change alone cannot satisfy the ticket because it leaves Python 3.9 in CI, does not declare a minimum Python version, and does not add Python 3.13 or 3.14.

## Current Repository Implementation

### Package metadata

In [`setup.py`](../../../setup.py), the package calls `setuptools.setup`, reads every line of `requirements.txt` into `install_requires`, and takes its version from `version.VERSION`. There is currently no `python_requires` declaration.

[`requirements.txt`](../../../requirements.txt) currently contains:

```text
robotframework>=6.0
setuptools~=82.0.1
mysql-connector~=2.2.9
```

[`version.py`](../../../version.py) currently declares `VERSION = "0.2.1"`.

### GitHub Actions

[`run-tests.yml`](../../../.github/workflows/run-tests.yml) currently runs a matrix of Python 3.9, 3.10, 3.11, and 3.12. Each job checks out with `actions/checkout@v2`, installs the package with `pip install .`, installs `coveralls`, `mock`, and `pytest-cov`, runs pytest with coverage, and uploads to Coveralls.

The workflow has no Python 3.13 or 3.14 entries. The existing matrix also mixes an unquoted `3.9` with quoted version strings; all versions should be represented carefully when the matrix is changed because YAML numeric parsing can alter values such as `3.10`.

### Release configuration

[`release-drafter.yml`](../../../.github/release-drafter.yml) defines release categories and a `What's Changed` template, including a Maintenance category. The repository has no dedicated release workflow in `.github/workflows`; the other workflow files are `codeql.yml`, `release-drafter.yml`, and `run-tests.yml`.

The latest real Git tag is `v0.2.1`. Existing version bump commits update `version.py` directly and use generic messages such as `Update version.py`; there is no repository-local automated v0.2.2 tagging or publishing procedure.

### Generated artifacts

The ignored [`robotframework_historic_parser.egg-info/PKG-INFO`](../../../robotframework_historic_parser.egg-info/PKG-INFO) and `requires.txt` were last written on 2026-08-19 and report target-looking values: version `0.2.2`, `Requires-Python: >=3.10`, and `setuptools~=84.0.0`. These files are ignored generated metadata and conflict with the tracked source files above, so they are not evidence that the source implementation is complete. They should not be committed as part of this research task.

## Open Questions

- What exact release procedure should create the GitHub tag and release: Release Drafter, a manual GitHub release, or another existing organizational process?
- Should the current Release Drafter template be amended for the v0.2.2 maintenance note, or should the release note be supplied manually?
- Does `actions/setup-python@v2` support the Python 3.14 runner/toolcache required by the final matrix, or should the action versions be modernized as part of the CI change?
- Is the current package installation path, including `mysql-connector~=2.2.9` and `robotframework>=6.0`, known to work on Python 3.13 and 3.14?
- Should the old GitHub PR #156 be closed after the replacement change is opened, or can it be updated and reused?
- Which concrete local command and environment should be used for the evidence required in Jira, given that this task must not create a virtual environment?

## Assumptions

- The five-version matrix means exactly Python 3.10, 3.11, 3.12, 3.13, and 3.14.
- The dependency constraint remains `setuptools~=84.0.0`, as stated in the ticket.
- `python_requires='>=3.10'` or its equivalent package metadata is the intended implementation of the minimum-version requirement.
- Existing fixture text mentioning Robot/Python 3.9 is historical XML input data and is not itself a supported-runtime declaration.
- The ignored egg-info files are stale or generated from an uncommitted target state; source files remain authoritative.

## Risks

- Updating the dependency without removing Python 3.9 will continue to fail the matrix, as demonstrated by PR #156.
- A Python 3.14 matrix may expose unsupported transitive dependencies or action/toolcache limitations that are not visible in the current 3.9-3.12 workflow.
- `setup.py` currently has no explicit Python requirement, so pip can attempt an install on Python 3.9 unless metadata is changed.
- The lack of a release workflow means the version bump, tag, release notes, and evidence can be split across manual steps and become inconsistent.
- Ignored generated metadata already advertises values different from tracked source, which can make local validation misleading if the artifacts are not regenerated from a clean source state.

## Proposed Next Steps

1. Decide the release procedure and whether PR #156 will be superseded or reused.
2. Update `requirements.txt`, `setup.py`, `version.py`, and the GitHub Actions matrix in one focused implementation change; keep changes to tests limited to coverage needed by changed behavior.
3. Validate package metadata and installation on Python 3.10 through 3.14 using the repository's existing system tooling, without creating a virtual environment for this research task.
4. Run the full test matrix in GitHub Actions and retain the run URL and per-version results.
5. Update the release-notes field, merge the validated change to `master`, create `v0.2.2`, and record the final PR and release URLs in QE-7481.

## Sources Reviewed

- Jira QE-7481 all-fields JSON fetched with `acli jira workitem view QE-7481 --fields '*all' --json` on 2026-08-19.
- Jira QE-7481 main description, custom fields `customfield_10035`, `customfield_10183`, and `customfield_11748`, parent/epic link, comment collection, issue links, changelog, and status metadata.
- Jira parent QE-7279 summary and status returned in the QE-7481 parent field.
- GitHub PR [Accruent/robotframework-historic-parser#156](https://github.com/Accruent/robotframework-historic-parser/pull/156), including body, changed-file list, comments, and commit checks, read on 2026-08-19.
- Tracked repository files: [`setup.py`](../../../setup.py), [`requirements.txt`](../../../requirements.txt), [`version.py`](../../../version.py), [`run-tests.yml`](../../../.github/workflows/run-tests.yml), [`release-drafter.yml`](../../../.github/release-drafter.yml), [`README.md`](../../../README.md), and [`.gitignore`](../../../.gitignore).
- Git history for the setuptools update branch, version bumps, CI matrix changes, and tags.

## Blockers

- No Jira comments or issue links were available to clarify release ownership or the final PR strategy.
- No repository-local `.context` precedent exists, so this document's location and name are a documented convention choice rather than a copied one.
- The ticket requires future CI and release evidence; those cannot be recorded until implementation, validation, merge, and release work occur.