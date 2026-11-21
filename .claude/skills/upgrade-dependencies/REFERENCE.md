# Reference

## Where to look

| Dependency | File | Rule |
|---|---|---|
| Build requirements | `pyproject.toml`, `build-system.requires` | Change the version after `>=`. |
| Runtime packages | `pyproject.toml`, `project.dependencies` | Change the version after `>=`. |
| Lint and test packages | `pyproject.toml`, `project.optional-dependencies` | Change the version after `>=`. |
| GitHub Actions | `.github/workflows/ci.yml`, each `uses: owner/repo@ref` | Change each occurrence. Keep the form of the ref: `v7` stays a major tag. |
| Python | `requires-python` in `pyproject.toml`, `python-version` in `ci.yml` | See [Python version](#python-version). |

- Remove an upper bound (`<X`) only when the user approved a target above it.
- CI installs `ansible-lint` without a version. Report it as "no version declared". Do not add a version.
- `required_collections` in `src/molecule_lima/driver.py` is empty. If it declares a collection later, handle its version as a floor. Change the same value in `tests/test_driver.py`.

## How to find versions

**Python package:** read the release list on PyPI.

```bash
curl -s https://pypi.org/pypi/<name>/json | python3 -c "
import json, re, sys
data = json.load(sys.stdin)
print('latest:', data['info']['version'], '| requires Python', data['info']['requires_python'])
versions = [v for v, files in data['releases'].items() if files and not all(f['yanked'] for f in files)]
print(*sorted(versions, key=lambda v: [int(n) for n in re.findall(r'\d+', v)]))"
```

- Ignore a version that is not a final release, for example `2.0.0rc1` or `1.5.dev0`.
- If the lookup fails, try again. If it fails again, report the dependency as not examined.

**GitHub Action:** read the tags of the repository.

```bash
git ls-remote --tags --refs https://github.com/<owner>/<repo>
```

- Use only a ref that the output contains. Do not make a ref name from a version number.
- If the repository has no ref of the same form as the current ref, do not change the ref. Report it.

## Version rules

| Case | Major change |
|---|---|
| Default | The first number changes: `1.20.2` to `2.4.1`. |
| Version `0.x` | The first non-zero number changes: `0.17.6` to `0.18.0`. |
| `ansible-core` | The second number changes: `2.22.0` to `2.23.0`. Each such release removes deprecated features. |
| Calendar version (`molecule`) | The year changes: `26.11.0` to `27.1.0`. A new month is an automatic upgrade. |
| Version above a declared upper bound | Always needs approval. A previous run added the bound for a reason. |
| GitHub Action | The major tag changes: `v7` to `v8`. |

## Python version

- Do not change `requires-python` or the CI `python-version` in an automatic upgrade.
- CI tests the lowest Python version that `requires-python` permits. Keep the two values equal.
- PyPI shows the Python requirement of each release (`requires_python`).
- If a target excludes the `requires-python` floor, the upgrade needs a higher Python floor.
- Propose such an upgrade as a major upgrade, also when the version change is small. Tell the user about the Python change.

## Tests

Make a new virtual environment for each test run. An old environment keeps old versions. Run all the commands of this block in one shell call, because a new shell call does not keep the activated environment.

```bash
python3 -m venv <temporary directory>/venv
source <temporary directory>/venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[lint,test]" ansible-lint build
pip check
ruff check src/ tests/
mypy src/
ansible-lint
pytest tests/ -v
python -m build --outdir <temporary directory>/dist
python -m zipfile -l <temporary directory>/dist/*.whl
```

- Each command must give exit status 0.
- The build output must not contain a deprecation warning.
- The wheel list must contain `molecule_lima/playbooks/create.yml`.
- Use the Python version of CI (`python-version` in `ci.yml`) if the machine has it. If not, give the version that you used in the summary.
- `pip` installs the latest version that the declaration permits. If a new floor is lower than that version, add `"<name>==<floor>"` to the `pip install` command to test the floor.
- For an action, run `git ls-remote --exit-code https://github.com/<owner>/<repo> refs/tags/<ref>`. Exit status 0 proves that the ref exists.

## Work branch

- Run `git symbolic-ref --short refs/remotes/origin/HEAD`. It prints `origin/<name>`. The default branch is `<name>`.
- If the command fails, the default branch is `main`.
- Create the work branch with `git switch -c deps/upgrade-<YYYY-MM-DD>`.
- If that branch exists, add a number: `deps/upgrade-<YYYY-MM-DD>-2`.
- If the start branch is not the default branch, stay on it. Do not delete it in section 6.

## Baseline failures

A test can fail before you change a file. A new install always takes the latest permitted versions, so a new release can break the project.

1. Run `pip list` in the test environment. Compare the versions with the floors in `pyproject.toml`.
2. Find the release that causes the failure.
3. If it is a major version, ask the user. Do not ask again about it in section 4.
4. Do section 5 of `SKILL.md` for this release: correct the project, or add an upper bound.
5. Continue with the other upgrades after the tests pass.
6. If no declared dependency causes the failure, stop and tell the user.

## Failure in the last tests

In section 6 of `SKILL.md`, each change is in a checkpoint commit. The rollback command has no effect there.

1. Read the output. Find the upgrade that causes the failure.
2. Set the declaration of that upgrade back to its value in the start commit. `git show <start commit>:<file>` shows that value.
3. Do not use `git revert`. It conflicts when two checkpoints changed adjacent lines.
4. Remove the corrections that you made for that upgrade. Remove its entry from `CHANGELOG.md`.
5. For a Python package, add an upper bound that excludes the failed version.
6. Commit these changes with `git commit -am`. Then do section 6 again from step 1. In step 2, add only the entries that `CHANGELOG.md` does not contain.
7. If you cannot find the cause, stop and tell the user. Do not make the final commit.

## End-to-end test

- The unit tests use mocks. `ansible-lint` examines the playbooks but does not run them.
- Only the scenario in `e2e/` runs the playbooks on a real Lima VM. `e2e/README.md` gives the requirements and the commands.
- Run it if the machine has the requirements. Use the virtual environment of the last test run.
- Do not install Lima or QEMU on a machine of the user without approval.
- If you cannot run it, continue. State in the summary that no test ran the playbooks.
- If it fails, obey [Failure in the last tests](#failure-in-the-last-tests).

## Summary template

```markdown
## Dependency upgrade summary

### Upgraded
| Dependency | From | To | Type |
|---|---|---|---|
| pytest | 9.0.0 | 9.2.0 | automatic |
| mypy | 1.20.2 | 2.4.1 | major, approved |

### Not upgraded
| Dependency | Current | Available | Reason |
|---|---|---|---|
| molecule | 26.11.0 | 27.1.0 | Declined. Upper bound `<27` added. |
| ruff | 0.17.6 | 0.18.2 | Failed and rolled back: `ruff check` reported 14 new errors. Upper bound `<0.18` added. |
| python (CI) | 3.13 | - | Not changed automatically. |
| ansible-lint | - | - | No version declared. |

### Tests
- Unit and lint tests: passed with Python 3.13.x.
- End-to-end test: passed, failed, or not run with the reason.
- Not tested locally: the GitHub Actions upgrades. CI tests them after the push.

### Commit
- `<hash>` `(chore) upgraded dependencies` on branch `<branch>`. Not pushed.
```
