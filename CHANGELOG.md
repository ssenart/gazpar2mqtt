# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Development dependencies: pytest `^9.0.3` and pytest-asyncio `^1.4.0`.
- Development tooling: ruff (lint and format) and mypy replace flake8, isort, black and pylint. Ruff and mypy are updated to their latest stable versions, and the CI lint and test steps are inlined in the workflow.

### Security

- Locked `urllib3` to 2.8.0, `requests` to 2.34.2, `idna` to 3.20 and `Jinja2` to 3.1.6 to fix open Dependabot alerts.

## [0.2.6a1] - 2026-10-04

### Changed

- Upgraded the PyGazpar library to `1.4.0a3`. It brings pydantic as a new dependency.

### Fixed

[#36](https://github.com/ssenart/gazpar2mqtt/issues/36): Wait for the MQTT broker to accept the connection before publishing. A refused connection (e.g. missing or wrong `mqtt.username`/`mqtt.password`) now stops the application with a clear error instead of logging success and silently dropping all data. Also fixed a shutdown hang when the connection is still open.

## [0.2.5] - 2026-03-22

### Fixed

[#31](https://github.com/ssenart/gazpar2mqtt/issues/31): Replace deprecated `object_id` with `default_entity_id` in MQTT discovery payload to fix Home Assistant deprecation warning (will stop working in HA Core 2026.4).

## [0.2.4] - 2025-11-16

### Fixed

[#28](https://github.com/ssenart/gazpar2mqtt/issues/28): Console logging, Env variable substitution, documentation clarifications by [hb020](https://github.com/hb020)
* complete env vars inside Python
* better docker build statements
* improve readme
* small readme tweak

## [0.2.3] - 2025-11-05

### Fixed

[#24](https://github.com/ssenart/gazpar2mqtt/issues/24): [Docker] Error without MQTT credential (contributed by [Nicolas-Delahaie](https://github.com/Nicolas-Delahaie))

## [0.2.2] - 2025-07-22

### Changed

[#21](https://github.com/ssenart/gazpar2mqtt/issues/21): Upgrade PyGazpar library to version 1.3.1.

## [0.2.1] - 2025-02-15

### Changed

[#12](https://github.com/ssenart/gazpar2mqtt/issues/12): Upgrade PyGazpar library to version 1.3.0.

## [0.2.0] - 2025-01-26

### Added

[#2](https://github.com/ssenart/gazpar2mqtt/issues/2): Deploy gazpar2mqtt as an HA add-on.
    Warning: Breaking change on configuration file format.

## [0.1.4] - 2025-01-22

### Added

[#7](https://github.com/ssenart/gazpar2mqtt/issues/7): Run unit tests against a MQTT container.

## [0.1.3] - 2025-01-22

### Fixed

[#5](https://github.com/ssenart/gazpar2mqtt/issues/5): Dockerhub container version 0.1.2 fails to start due to errors in entrypoint.sh.

## [0.1.2] - 2025-01-21

### Added

[#4](https://github.com/ssenart/gazpar2mqtt/issues/4): Automate build, package, publish with Github Actions.

## [0.1.1] - 2024-12-09

### Fixed

[#1](https://github.com/ssenart/gazpar2mqtt/issues/1): Fatal error if GrDF returns no start index/end index/volume/energy data in the record.

## [0.1.0] - 2024-12-08

First version of the project.

[Unreleased]: https://github.com/ssenart/gazpar2mqtt/compare/0.2.6a1...HEAD
[0.2.6a1]: https://github.com/ssenart/gazpar2mqtt/compare/0.2.5...0.2.6a1
