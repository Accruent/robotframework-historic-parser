# Setuptools 84 Compatibility and Historic Parser 0.2.2 Release Implementation Plan

> **Execution record:** This plan was executed inline in the existing checkout. No subagents, worktrees, or virtual environments were used. Implementation commit and release operations were performed only after their phase gates passed.

**Goal:** Update the historic parser package and CI for setuptools 84 with Python 3.10-3.14 support, then release version 0.2.2 from the merged master commit. Repository and GitHub release evidence are authoritative; QE-7481 field updates are optional for this internal release.

**Architecture:** Keep the existing `setup.py` packaging model and runtime test suite. Change only the dependency constraint, package minimum Python metadata, package version, and the existing GitHub Actions test matrix; use an inline installed-metadata assertion to validate the packaging boundary without adding a separate packaging test module or release workflow.

**Tech Stack:** Python `setuptools`, `pip`, `pytest`, `pytest-cov`, GitHub Actions, Release Drafter, Git, GitHub Releases, Jira.

---

## Current Behavior and Requested Behavior

### Current behavior

- `setup.py` calls `setuptools.setup`, reads all lines from `requirements.txt` into `install_requires`, and has no `python_requires` declaration.
- `requirements.txt` pins `setuptools~=82.0.1`.
- `version.py` declares `VERSION = "0.2.1"`.
- `.github/workflows/run-tests.yml` tests Python 3.9, 3.10, 3.11, and 3.12 with `actions/checkout@v2` and `actions/setup-python@v2`.
- The existing tests are runtime parser tests under `test/`; there is no packaging-metadata test.
- `.github/release-drafter.yml` drafts releases after pushes to `master`, but no workflow creates or publishes tags and releases.
- The latest real tag is `v0.2.1`.

### Requested behavior

- Python 3.9 is no longer a supported project version.
- Package metadata declares Python `>=3.10`.
- The supported and validated CI matrix is exactly Python 3.10, 3.11, 3.12, 3.13, and 3.14.
- The direct setuptools requirement is `setuptools~=84.0.0`.
- Package installation and the existing tests pass on every supported matrix version.
- Package metadata reports version `0.2.2`.
- Git tag and GitHub release `v0.2.2` point to the merged `master` commit and contain maintenance release notes.
- Release evidence is authoritative in the merged commit, Actions run, tag, and GitHub release; QE-7481 release-notes field updates are not required for this internal release.

### Constraints

- Scope rule: do not modify parser behavior, tests, generated artifacts, or Git history beyond the explicitly listed implementation and release operations.
- The implementation should reuse and expand open PR #156 when its branch is writable. If that branch cannot be updated, stop and request a decision before opening a replacement PR.
- Use the existing Release Drafter workflow and manually publish the release; do not add release automation in this ticket.
- Do not create a virtual environment. Use a system Python 3.10 interpreter for the local smoke test when available; otherwise record the limitation and use GitHub Actions for the complete five-version installation matrix.
- Do not commit ignored `build/` or `robotframework_historic_parser.egg-info/` output.
- Do not change parser behavior or refactor the runtime tests unless a reproducible compatibility failure requires a separately agreed scope change.

## Approaches Considered

### Approach 1: Reuse PR #156 with an inline packaging check (recommended)

Update the existing Dependabot PR branch with `requirements.txt`, `setup.py`, `version.py`, and `.github/workflows/run-tests.yml`. The workflow asserts installed version, `Requires-Python`, and the setuptools requirement before running the existing pytest suite. Keep Release Drafter unchanged and publish the tagged release manually.

Trade-offs: smallest change set and one review trail; depends on permission to push to the existing Dependabot branch and keeps packaging validation in CI rather than in a reusable test module.

### Approach 2: Close PR #156 and create a replacement feature branch

Create a normal maintainer branch containing the same four-file implementation and validation. This avoids Dependabot branch permissions but creates another PR and requires explicit closure or supersession handling for #156.

Trade-offs: more control over branch history; more operational work and a greater chance of leaving the original PR unresolved.

### Approach 3: Add a packaging test and release automation

Add a test module for installed metadata and a GitHub workflow for tagging or publishing releases.

Trade-offs: more reusable automation, but it expands the ticket beyond the repository's existing conventions, duplicates the CI install-boundary check, and introduces release-token and workflow maintenance risk.

### Decision

Use Approach 1. Reuse PR #156, keep the repository's current packaging and release structure, modernize the two action pins as part of the CI change, and use an inline metadata assertion plus the existing full test suite.

## File Map

### Files modified during implementation

- `requirements.txt`: replace the direct setuptools constraint with `setuptools~=84.0.0`.
- `setup.py`: add `python_requires='>=3.10'` to the existing `setup(...)` call.
- `version.py`: change `VERSION` from `0.2.1` to `0.2.2`.
- `.github/workflows/run-tests.yml`: replace the matrix with quoted Python 3.10-3.14 values, set `fail-fast: false`, update action pins, use the selected interpreter for pip commands, and assert installed metadata.

### Files that remain unchanged

- `test/db_test.py`
- `test/function_test.py`
- `test/parserargs_test.py`
- `test/rfhistoricparser_test.py`
- `.github/release-drafter.yml`
- `README.md`
- `.gitignore`
- All parser implementation modules and generated `*.egg-info` files.

### Operational artifacts outside the repository

- Existing PR #156 and its branch.
- The GitHub Actions run produced by the merged implementation.
- The GitHub tag and release `v0.2.2`.
- QE-7481 verification comments/evidence are optional operational artifacts.
- QE-7459, which the live ticket currently identifies as blocking QE-7481; it is an external dependency and is not modified by this plan.

## Implementation Phases

### Phase 1: Prepare and verify the existing PR branch

**Files:** None.

- [x] Confirm PR #156 is still open and points at `master` from `dependabot/pip/setuptools-approx-eq-84.0.0`.

  Run:

  ```powershell
  git ls-remote --heads origin dependabot/pip/setuptools-approx-eq-84.0.0
  git fetch origin master dependabot/pip/setuptools-approx-eq-84.0.0
  ```

  Expected: the Dependabot branch resolves to a commit and the fetch completes without changing the working tree.

- [x] Switch the existing checkout to the branch underlying PR #156 rather than creating a worktree.

  Run:

  ```powershell
  git switch --track origin/dependabot/pip/setuptools-approx-eq-84.0.0
  git status --short
  ```

  Expected: the branch is checked out and only intentionally untracked research files, if any, are present. Do not stage `.context/research/archive/2026-08-19-qe-7481-setuptools-84-compatibility-release-research.md` as part of the implementation.

- [x] Verify the baseline files before editing.

  Run:

  ```powershell
  Select-String -Path requirements.txt -Pattern 'setuptools'
  Select-String -Path setup.py -Pattern 'setup\(|python_requires'
  Select-String -Path version.py -Pattern 'VERSION'
  Select-String -Path .github/workflows/run-tests.yml -Pattern 'python-version|actions/checkout|actions/setup-python'
  ```

  Expected: the baseline shows `setuptools~=82.0.1`, no `python_requires`, version `0.2.1`, the old 3.9-3.12 matrix, and action pins `@v2`.

  Actual PR-branch note: `requirements.txt` already contains `setuptools~=84.0.0` because PR #156 is the Dependabot update; the diff against `origin/master` confirms this is the only pre-existing PR change.

- [x] The branch was checked out successfully; the fallback replacement-PR path was not needed.

### Phase 2: Update package metadata and dependency declarations

**Files:** `requirements.txt`, `setup.py`, `version.py`.

- [x] Update the direct setuptools requirement in `requirements.txt`.

  The final dependency lines must be:

  ```text
  robotframework>=6.0
  setuptools~=84.0.0
  mysql-connector~=2.2.9
  ```

  Do not change the Robot Framework or MySQL connector constraints in this ticket.

  Execution note: the PR branch already contained the intended `setuptools~=84.0.0` Dependabot change, so no additional edit was required in this step.

- [x] Add the minimum Python declaration to the existing `setup(...)` call in `setup.py`.

  Keep the existing version source and dependency loading. The relevant package metadata must include:

  ```python
  setup(
      name='robotframework-historic-parser',
      version=version.VERSION,
      python_requires='>=3.10',
      description='Parser to push robotframework execution results to MySQL',
  ```

  Do not replace the current `install_requires=REQUIREMENTS` mechanism or move packaging to a new configuration format.

- [x] Bump the source version in `version.py`.

  The final assignment must be:

  ```python
  VERSION = "0.2.2"
  ```

- [x] Run a focused source diff check before editing the workflow.

  Run:

  ```powershell
  git diff --check
  git diff -- requirements.txt setup.py version.py
  ```

  Expected: only the three intended source changes are present, with no whitespace errors and no generated metadata staged or modified for commit.

### Phase 3: Modernize the GitHub Actions matrix and add install-boundary validation

**File:** `.github/workflows/run-tests.yml`, job `run-tests`.

- [x] Replace the matrix and action pins while preserving the existing push and pull request triggers.

  The complete target workflow is:

  ```yaml
  name: run-tests
  on:
    push:
      branches:
        - master
    pull_request:
      branches:
        - master
  jobs:
    run-tests:
      runs-on: ubuntu-latest
      strategy:
        fail-fast: false
        matrix:
          python-version: ['3.10', '3.11', '3.12', '3.13', '3.14']
      steps:
        - uses: actions/checkout@v7
        - name: Set up Python ${{ matrix.python-version }}
          uses: actions/setup-python@v6
          with:
            python-version: ${{ matrix.python-version }}

        - name: Install dependencies
          run: |
            python -m pip install --upgrade pip
            python -m pip install .

        - name: Verify installed package metadata
          run: |
            python - <<'PY'
            from importlib.metadata import distribution
            import setuptools

            package = distribution('robotframework-historic-parser')
            assert package.version == '0.2.2', package.version
            assert package.metadata['Requires-Python'] == '>=3.10'
            assert any(
                requirement.startswith('setuptools~=84.0.0')
                for requirement in (package.requires or [])
            )
            assert setuptools.__version__.startswith('84.0.'), setuptools.__version__
            print(package.version)
            print(package.metadata['Requires-Python'])
            print(setuptools.__version__)
            PY

        - name: Install test dependencies
          run: |
            python -m pip install coveralls mock pytest-cov
        - name: Run Unit Tests
          run: |
            pytest --cov-config=test/.coveragerc --cov=robotframework_historic_parser -v
        - name: Coveralls
          env:
            GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
            flag-name: run-${{ matrix.python-version }}
            parallel: true
          run: |
            coveralls --service=github
  ```

  `actions/checkout@v7` and `actions/setup-python@v6` are the current major versions verified against the official action documentation during planning on 2026-08-19. Reconfirm action availability immediately before implementation because action majors can change independently of this repository.

- [x] Confirm the workflow has no unquoted numeric Python versions and no Python 3.9 entry.

  Run:

  ```powershell
  Select-String -Path .github/workflows/run-tests.yml -Pattern "3\.9|3\.10|3\.11|3\.12|3\.13|3\.14|fail-fast|actions/checkout|actions/setup-python"
  git diff --check
  ```

  Expected: only quoted `3.10` through `3.14` appear; `3.9` does not appear; `fail-fast: false`, `@v7`, and `@v6` are present.

- [x] Create one focused implementation commit only after the package and workflow diff passes review, then push it to the branch for PR #156.

  Execution command record:

  ```powershell
  git add requirements.txt setup.py version.py .github/workflows/run-tests.yml
  git commit -m "QE-7481 update setuptools compatibility"
  git push origin dependabot/pip/setuptools-approx-eq-84.0.0
  ```

  Expected: PR #156 updates with the complete four-file change and no test, parser, release-workflow, or generated-artifact changes.

  Execution note: the initial push attempt was rejected with HTTP 403 because the active account had `viewerPermission: READ`. After switching the active GitHub account to `neiljhowell` (`viewerPermission: ADMIN`), commit `0cbeb80` pushed successfully and the remote PR branch resolved to that commit.

### Phase 4: Run local package and test validation without a virtual environment

**Files:** None beyond the Phase 2 and Phase 3 implementation files.

- [x] Remove only disposable ignored packaging output before the smoke test, after confirming it contains no user-owned work.

  Run:

  ```powershell
  Remove-Item -Recurse -Force .\build, .\robotframework_historic_parser.egg-info -ErrorAction SilentlyContinue
  ```

  Expected: stale ignored metadata is absent; tracked source files are unchanged. Do not run `git clean` broadly and do not remove tracked files.

- [x] Confirm the local Python 3.10 interpreter exists. Do not create a virtual environment if it does not.

  Run:

  ```powershell
  py -3.10 --version
  py -3.10 -m pip --version
  ```

  Expected: Python 3.10.x and a pip associated with that interpreter. If Python 3.10 is unavailable, record local validation as blocked and use the GitHub Actions matrix for version coverage; do not install another interpreter or create a virtual environment as part of this ticket.

  Execution note: `py --list` reports only Python 3.14.7; `py -3.10 --version` and `py -3.10 -m pip --version` report no suitable runtime. The Python 3.10-dependent local install, metadata assertion, full test, and optional Python 3.9 negative check were skipped. The pushed GitHub Actions matrix is authoritative for supported-version coverage.

- [x] Handle local package installation: skipped because Python 3.10 is unavailable; the GitHub Actions matrix provides the supported-version installation evidence.

  Run:

  ```powershell
  py -3.10 -m pip install --user --upgrade pip
  py -3.10 -m pip install --user .
  ```

  Expected: pip resolves `setuptools~=84.0.0`, builds and installs `robotframework-historic-parser` version `0.2.2`, and reports no Python-version rejection.

- [x] Handle local installed-metadata assertion: skipped because Python 3.10 is unavailable; the workflow's inline assertion passed on all five supported versions.

  Run:

  ```powershell
  py -3.10 -c "from importlib.metadata import distribution; import setuptools; d=distribution('robotframework-historic-parser'); assert d.version == '0.2.2'; assert d.metadata['Requires-Python'] == '>=3.10'; assert any(r.startswith('setuptools~=84.0.0') for r in (d.requires or [])); assert setuptools.__version__.startswith('84.0.'); print(d.version); print(d.metadata['Requires-Python']); print(setuptools.__version__)"
  ```

  Expected: three output lines showing `0.2.2`, `>=3.10`, and a setuptools `84.0.x` version.

- [x] Handle the local full unit test command: skipped because Python 3.10 is unavailable; the workflow's existing test command passed on all five supported versions.

  Run:

  ```powershell
  py -3.10 -m pip install --user coveralls mock pytest-cov
  py -3.10 -m pytest --cov-config=test/.coveragerc --cov=robotframework_historic_parser -v
  ```

  Expected: pytest exits with code 0 and reports all collected tests passing. Record the exact summary line for the Jira evidence.

- [x] Handle the optional Python 3.9 negative check: not applicable because `py --list` reports only Python 3.14.7.

  Run:

  ```powershell
  py -3.9 -m pip install --dry-run --ignore-installed .
  ```

  Expected: pip refuses the package with a message that the project requires Python `>=3.10`. This is an optional negative check; the supported CI matrix must not include Python 3.9.

- [x] Verify source diff hygiene after local validation.

  Run:

  ```powershell
  git diff --check
  git diff --name-only
  git status --short --untracked-files=all
  ```

  Expected: the diff names only `requirements.txt`, `setup.py`, `version.py`, and `.github/workflows/run-tests.yml`; ignored build metadata is not staged. The pre-existing research file remains untracked and is not included in the implementation commit.

### Phase 5: Validate the complete GitHub Actions matrix and merge PR #156

**Files:** None; validation occurs in GitHub.

- [x] Wait for the `run-tests` workflow on PR #156 to complete.

  Expected: five jobs appear, named for Python 3.10 through 3.14; all five install the package, pass the inline metadata assertion, pass the existing pytest/coverage command, and complete their Coveralls step. No Python 3.9 job is created.

  Execution evidence: successful run `https://github.com/Accruent/robotframework-historic-parser/actions/runs/32295175795` for head `0cbeb80`; `run-tests (3.10)`, `(3.11)`, `(3.12)`, `(3.13)`, and `(3.14)` all completed successfully.

- [x] Treat any Python 3.13 or 3.14 dependency failure as a compatibility blocker rather than silently changing transitive requirements.

  The first diagnosis should identify whether the failure comes from `mysql-connector~=2.2.9`, `robotframework>=6.0`, setuptools resolution, the runner/toolcache, or parser runtime behavior. Changes to those constraints or parser code require a new scope decision because the research did not establish a supported replacement.

  Execution evidence: no Python 3.13 or 3.14 dependency failure occurred; no transitive dependency or parser changes were made.

- [x] Verify PR #156 is reviewable and mergeable only after all five required jobs pass, then merge it according to repository permissions.

  Expected: PR #156 is merged into `master`; its merge commit contains the four intended files and source version `0.2.2`.

  Execution evidence: PR `https://github.com/Accruent/robotframework-historic-parser/pull/156` is merged into `master` at `72bd45e67a9c892accb5717d9cb917f6ebddd84a`; `origin/master:version.py` contains `VERSION = "0.2.2"`.

- [x] Capture the successful Actions run URL and the final PR URL/status immediately after merge. These values are required Jira evidence and must be recorded verbatim, not inferred from a branch or commit URL.

  Execution evidence: Actions run URL `https://github.com/Accruent/robotframework-historic-parser/actions/runs/32295175795`; PR URL `https://github.com/Accruent/robotframework-historic-parser/pull/156`; final status `MERGED`.

### Phase 6: Prepare and publish `v0.2.2` from merged `master`

**Files:** None in the repository; use the existing Release Drafter configuration.

- [x] Confirmed that the Jira release-notes field is not required for this internal release; leave `customfield_11748` and the empty Acceptance Criteria/Test Plan fields unchanged.

  Execution decision: the ticket field is non-blocking. The maintenance notes remain required on the GitHub release itself.

- [x] Refresh local refs and verify the merged master source before tagging.

  Run:

  ```powershell
  git fetch origin master --tags
  git show origin/master:version.py
  git rev-parse origin/master
  ```

  Expected: `version.py` on `origin/master` contains `VERSION = "0.2.2"`; the printed SHA is the merge commit that will receive the tag.

  Execution evidence: `origin/master` is `72bd45e67a9c892accb5717d9cb917f6ebddd84a`; `version.py` reports `VERSION = "0.2.2"`.

- [x] Create and push the annotated tag from the exact merged master commit.

  Run:

  ```powershell
  git tag -a v0.2.2 origin/master -m "Release v0.2.2"
  git push origin v0.2.2
  $masterSha = (git rev-parse origin/master).Trim()
  $tagSha = (git rev-list -n 1 v0.2.2).Trim()
  if ($masterSha -ne $tagSha) { throw "v0.2.2 does not point to origin/master" }
  ```

  Expected: the tag push succeeds and the final comparison produces no exception.

  Execution evidence: annotated tag `v0.2.2` pushed successfully; both the local tag and remote peeled tag resolve to `72bd45e67a9c892accb5717d9cb917f6ebddd84a`.

- [x] Publish the Release Drafter draft as GitHub release `v0.2.2`.

  In the existing draft, set the tag to `v0.2.2`, target the merged `master` commit, replace the generated notes with:

  ```markdown
  ## Maintenance
  - Updated setuptools compatibility to 84.0.0.
  - Dropped Python 3.9 support and validated Python 3.10 through 3.14.
  - Released package version 0.2.2.
  ```

  Publish the release from the GitHub Releases UI. Do not create a second release workflow or publish a different tag.

  Execution evidence: existing Release Drafter draft `151188102` was retargeted and published as `Robot Framework Historic Parser v0.2.2`.

- [x] Verify the published release and tag.

  Run, if the GitHub CLI is available:

  ```powershell
  gh release view v0.2.2 --json tagName,targetCommitish,isDraft,publishedAt,url
  ```

  Expected: `tagName` is `v0.2.2`, `isDraft` is `false`, the target is the merged master commit, `publishedAt` is non-null, and the output includes the public release URL. If `gh` is unavailable, verify the same fields in the GitHub Releases UI.

  Execution evidence: published `2026-08-19T20:02:16Z`; release URL `https://github.com/Accruent/robotframework-historic-parser/releases/tag/v0.2.2`; target `72bd45e67a9c892accb5717d9cb917f6ebddd84a`.

### Phase 7: Record QE-7481 evidence and complete the acceptance checklist

**External target:** QE-7481.

- [x] Record the local validation limitation and authoritative CI evidence; a QE-7481 field update is not required for this internal release.

  Execution evidence: Python 3.10 was unavailable locally and no local pass is claimed; the GitHub Actions run `https://github.com/Accruent/robotframework-historic-parser/actions/runs/32295175795` passed Python 3.10 through 3.14.

- [x] Confirm that adding the successful GitHub Actions run URL and per-version outcome to QE-7481 is optional for this internal release.

  The evidence must state that Python 3.10, 3.11, 3.12, 3.13, and 3.14 passed and that no Python 3.9 job remains.

- [x] Confirm that adding the final PR #156 URL and status to QE-7481 is optional for this internal release.

  Expected status: merged. If PR #156 could not be reused and a replacement was approved, record both the replacement PR and the disposition of #156 instead.

- [x] Confirmed that no QE-7481 release-notes field update is required for this internal release; do not block publication on `customfield_11748`.

- [x] Re-read the ticket acceptance criteria and confirm every repository/release item has evidence: `Requires-Python >=3.10`, install with setuptools 84 on all five versions, all five CI jobs passing, package version `0.2.2`, and tag/release from merged `master`. QE-7481 release-notes and URL fields are not required for this internal release.

  Execution evidence: package metadata and CI checks passed, PR #156 merged, `v0.2.2` and its GitHub release target merge commit `72bd45e67a9c892accb5717d9cb917f6ebddd84a`, and the release notes are published at the verified release URL.

  External dependency status: QE-7459 remains in `Develop` as of final verification. The 0.2.2 implementation and release are complete, but QE-7481 closure remains subject to the owning process for that linked blocker.

## Automated Validation Summary

Validation record:

```powershell
git diff --check
py -3.10 -m pip install --user .
py -3.10 -m pytest --cov-config=test/.coveragerc --cov=robotframework_historic_parser -v
```

Actual local result: no diff whitespace errors; Python 3.10 is unavailable, so no local 3.10 installation, metadata, or pytest pass is claimed. A separate Python 3.14 suite invocation returned `46 passed, 10 failed` because the installed local `mysql.connector` namespace lacked `connect`; this environment-specific result was not used as the release gate. The successful GitHub Actions run `https://github.com/Accruent/robotframework-historic-parser/actions/runs/32295175795` is authoritative for Python 3.10 through 3.14.

Additional checks: Python compilation passed; workspace diagnostics reported no errors; Flake8 and Ruff reported pre-existing repository issues; Pylance reported warnings only and no type errors.

GitHub Actions must independently provide the five-version result because this plan forbids virtual environments and does not assume five local interpreters are installed.

## Completed Manual Validation

- PR #156 was inspected and merged after the five required jobs passed.
- The merged `master` commit contains `VERSION = "0.2.2"`.
- `v0.2.2` resolves to that exact merge commit.
- The existing Release Drafter draft was published with maintenance notes.
- The published release was inspected for its tag, target commit, notes, and public URL.
- QE-7481 release-notes field inspection is not required for this internal release; inspect repository and GitHub release evidence instead.
- QE-7459 remains in `Develop`; final QE-7481 closure remains subject to the owning team's process for that linked blocker.

## Risks and Mitigations

- **Python 3.14 tooling:** The current official `actions/setup-python` documentation supports Python `3.14` and uses quoted matrix values. Pin the current action majors, keep `fail-fast: false`, and treat an unavailable toolcache as a CI infrastructure blocker.
- **Transitive dependency compatibility:** `mysql-connector~=2.2.9` and `robotframework>=6.0` were not proven on Python 3.13 or 3.14 by the research. Diagnose a resolver or import failure before changing either constraint; request a new decision if a dependency update is needed.
- **Dependabot branch permissions:** PR #156 may not accept maintainer pushes. Do not silently create a replacement PR; stop and get approval for the alternate branch approach.
- **Stale ignored metadata:** Existing `robotframework_historic_parser.egg-info` advertises target values that do not match tracked source. Remove disposable generated output before local validation, inspect the installed distribution, and never stage generated metadata.
- **Release target mismatch:** A tag created from the wrong ref would violate acceptance. Compare the tag commit with `origin/master` before publishing and verify the release target afterward.
- **Local environment limitation:** Only a system Python 3.10 smoke test is required locally. The GitHub matrix is the authoritative five-version installation validation; do not create a virtual environment to manufacture local coverage.
- **Jira evidence drift:** If operational evidence is recorded on QE-7481, capture URLs and results immediately after each successful operation; the release-notes field is not a release gate.

## External Dependencies and Final Status

- Resolved: maintainer permission to update and merge PR #156.
- Resolved: GitHub-hosted runner availability for Python 3.10 through 3.14 and the current checkout/setup action majors.
- Resolved: package installation and the existing tests on Python 3.10 through 3.14 through the successful Actions run.
- Resolved: permission to publish the GitHub release and push the `v0.2.2` tag.
- Optional: permission to add operational comments/evidence to QE-7481; no field update is required for this internal release.
- Open external dependency: QE-7459 remains in `Develop`. This plan does not resolve that sub-task.

## Success Criteria

- `requirements.txt` contains `setuptools~=84.0.0`.
- Installed package metadata declares `Requires-Python: >=3.10` and version `0.2.2`.
- `run-tests.yml` tests exactly quoted Python `3.10`, `3.11`, `3.12`, `3.13`, and `3.14`, with no 3.9 job, `fail-fast: false`, `actions/checkout@v7`, and `actions/setup-python@v6`.
- Local Python 3.10 installation and the existing pytest command pass, or any local interpreter limitation is explicitly recorded without claiming a local pass.
- All five GitHub Actions jobs pass on the merged implementation.
- PR #156 is merged, or an explicitly approved replacement PR is merged and #156 is resolved.
- Tag `v0.2.2` and the published GitHub release both point to the merged `master` commit and contain maintenance release notes.
- QE-7481 release-notes field updates are not required for this internal release; repository and GitHub release evidence satisfy the release record.

## Execution Closure

This plan was executed on 2026-08-19. The package, CI workflow, merged PR, tag, and published GitHub release are complete and verified. The local Python 3.10 limitation and non-authoritative Python 3.14 test result are recorded above. QE-7459 remains the only external dependency relevant to final QE-7481 closure.