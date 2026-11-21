# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Claude skill `upgrade-dependencies` that gives the procedure to upgrade and test the dependencies
- End-to-end Molecule scenario for a real Lima VM in `e2e/`

### Changed
- Raised the minimum `molecule` version from 6.0.0 to 26.11.0
- Raised the minimum `ansible-core` version from 2.12.0 to 2.22.0
- Raised the minimum `pyyaml` version from 5.1 to 6.0.4
- Raised the minimum `jinja2` version from 2.11.3 to 3.1.6
- Raised the minimum `ruff` version from 0.9.0 to 0.17.6
- Raised the minimum `mypy` version from 1.0.0 to 2.4.1
- Raised the minimum `pytest` version from 9.0.0 to 9.2.0
- Raised the minimum `setuptools` build requirement from 61.0 to 84.2.1
- Removed `wheel` from the build requirements
- Changed the `license` field in pyproject.toml to the SPDX form `"MIT"`
- Removed the `community.general` collection requirement, because the playbooks do not use it
- Upgraded `actions/checkout` from v6 to v7 in the CI workflow
- Upgraded `actions/setup-python` from v6 to v7 in the CI workflow

### Fixed
- Included the Ansible playbooks in the built wheel, so a non-editable install can create instances

## [1.0.1] - 2026-03-07

### Added
- Comprehensive unit test suite for the Lima driver
- GitHub Actions CI workflow with lint and test jobs
- AGENTS.md with developer guidelines and coding conventions

### Changed
- Updated pyproject.toml with optional lint and test dependencies

### Fixed
- Added type ignore for Driver.__init__ config parameter

## [1.0.0] - 2026-03-06

### Added
- Initial release of molecule-lima
- Molecule driver for Lima VM provisioning
- Ansible playbooks for instance lifecycle management:
  - create.yml - Main create playbook
  - create_instance.yml - Instance creation and configuration
  - validate_instance.yml - Instance validation
  - prepare.yml - Instance preparation
  - destroy.yml - Instance destruction
- README with installation and usage documentation
- Package metadata (pyproject.toml, .gitignore)
