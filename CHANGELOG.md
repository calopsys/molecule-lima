# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
