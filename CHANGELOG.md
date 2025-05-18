# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - v0.2.0 (In Development)

### Added
- **Faker Integration**: Integrated the [Faker](https://faker.readthedocs.io/) library to generate more realistic data for common field names (e.g., `name`, `email`, `address`).
- **Locale Support**: Added `--faker-locale` CLI option to specify the locale for Faker, enabling localized data generation.
- **Seedable Generation**: Added `--seed` CLI option to provide a seed for random number generators (Python's `random` and `Faker`), ensuring reproducible data generation.
- Enhanced generation for `uuid.UUID` and `datetime` types to use Faker providers for better seed determinism.
- Default string generation (when not matching a specific Faker provider by field name) now uses `Faker.sentence()` for more meaningful random strings.

### Changed
- Updated core data generation logic to incorporate Faker.
- Modified `_generate_value_for_type` to accept and use a `Faker` instance.
- Refactored `generate_fake_data_for_model` to handle Faker instance creation based on `locale` and `seed` options.

### Fixed
- Improved determinism of generated `uuid.UUID` and `datetime` values when a seed is provided by using Faker's relevant providers.

## [0.1.0] - 2025-05-18

### Added
- Initial release of `pydantic-faker`.
- CLI command `generate` to produce fake data from Pydantic models.
- Dynamic loading of Pydantic models via string path (e.g., `module:ClassName`).
- Support for basic Python types: `int`, `str`, `float`, `bool`.
- Support for common Python data types: `uuid.UUID`, `datetime.datetime`, `datetime.date`, `datetime.time`.
- Handling of Pydantic/typing generics: `Optional[T]`, `List[T]`, `Dict[str, T]`.
- Recursive generation for nested Pydantic models.
- Output of generated data to JSON format, either to standard output (stdout) or to a specified file.
- Basic error handling for invalid model paths or non-Pydantic models.
- CLI structure built with Typer.
- Project setup with `pyproject.toml` and `hatchling` as the build backend.
- Initial test suite using `pytest`.
- Code linting and formatting настроено с `Ruff`, type checking с `Mypy` и `Pyright`.
