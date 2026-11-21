---
name: upgrade-dependencies
description: Upgrades the dependencies of molecule-lima (Python packages in pyproject.toml and GitHub Actions in the CI workflow). Applies patch and minor upgrades automatically, proposes major upgrades to the user, tests each change, rolls back an upgrade that fails, and delivers one tested commit with a summary. Use when the user asks to upgrade, update, or bump dependencies, or asks which dependencies are outdated.
---

# Upgrade dependencies

If the user only asks which dependencies are outdated, do section 2 and report the result. Do not change a file.

## Concepts

- `pyproject.toml` declares each Python package as a floor (`name>=X`). The repository has no lock file.
- To upgrade a package is to raise its floor to the target version.
- A new install takes the latest version that the declaration permits.
- Apply a patch upgrade or a minor upgrade without a question. A major upgrade needs the approval of the user.
- [Version rules](REFERENCE.md#version-rules) tells you which change is a major change.

## Procedure

- A checkpoint commit is `git commit -am "checkpoint: <text>"`. Make one only after the tests pass. The changelog commit in section 6 is the only exception.
- The rollback command is `git restore --staged --worktree :/`. It goes back to the last checkpoint commit.
- "Run the tests" means: do all the steps in [Tests](REFERENCE.md#tests).

### 1. Prepare

1. Run `git status --porcelain --untracked-files=no`. If it prints a line, stop and ask the user.
2. Record the start commit (`git rev-parse HEAD`) and the start branch.
3. If the start branch is the default branch, create a work branch. See [Work branch](REFERENCE.md#work-branch).
4. Run the tests. If a test fails, obey [Baseline failures](REFERENCE.md#baseline-failures) before you continue.

### 2. Find the upgrades

1. List each declared dependency. See [Where to look](REFERENCE.md#where-to-look).
2. Find the available versions of each one. See [How to find versions](REFERENCE.md#how-to-find-versions).
3. For each dependency, record the latest version in the current major version and the latest version in total.
4. If no newer version exists, go to section 6.

### 3. Automatic upgrades

1. Raise each floor to the latest version in its current major version that its upper bound permits.
2. Make an exception for a version that needs a newer Python. See [Python version](REFERENCE.md#python-version).
3. Run the tests. If they pass, make a checkpoint commit.
4. If they fail, find the upgrade that causes the failure. Do section 5 for it.

### 4. Major upgrades

1. For each newer major version, read the upstream release notes. Find the changes that can break this project.
2. Ask the user which major upgrades to apply. Give the current version, the target, the risk, and your recommendation.
3. Tell the user that a declined Python package gets an upper bound.
4. Do not apply a major upgrade that the user did not approve.
5. Apply the approved upgrades one at a time. Test each one.
6. Make a checkpoint commit when the upgrade passes. Do section 5 when it fails.
7. For each declined Python package, add an upper bound. An example is `"mypy>=2.4.1,<3"`.
8. Do not add the upper bound if the user wants to keep the range open.
9. Change nothing for a declined action.
10. Run the tests after you add upper bounds. Make a checkpoint commit when they pass.

### 5. Failed upgrade

1. Read the output of the failed test.
2. If the correction is small and mechanical, apply it and test again. An example is `ruff check --fix`.
3. Do not change a test assertion, remove a test, or relax a check to get a pass.
4. If the correction is not small, run the rollback command.
5. For a Python package, add an upper bound that excludes the failed version. If you do not, each new install takes that version.
6. Run the tests after you add an upper bound. Make a checkpoint commit when they pass.
7. Record the dependency, the failed test, and the cause for the summary.

### 6. Deliver

1. If `git diff --quiet <start commit> HEAD` gives exit status 0, no change exists. Then run `git reset --hard <start commit>`, go back to the start branch, delete the work branch that you created, and go to step 8.
2. Add one entry for each upgrade and each new upper bound to `CHANGELOG.md`, below `## [Unreleased]` and `### Changed`. Make a checkpoint commit.
3. Run the tests. Then run the [End-to-end test](REFERENCE.md#end-to-end-test) if the machine permits it.
4. If a test fails, obey [Failure in the last tests](REFERENCE.md#failure-in-the-last-tests).
5. Make sure that `git status --porcelain --untracked-files=no` prints nothing. Record the tested commit (`git rev-parse HEAD`).
6. Run `git reset --soft <start commit>`, then `git commit -m "(chore) upgraded dependencies"`. List each upgrade and each new upper bound in the body of the message.
7. Run `git diff --quiet <tested commit> HEAD`. Exit status 0 proves that the commit contains the tested tree.
8. Give the summary to the user. Use the [Summary template](REFERENCE.md#summary-template).
9. Do not push.
