# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2025-05-21

### Added
- **Mock API Server (`serve` command)**: Implemented the `pydantic-faker serve` command.
    - Uses FastAPI and Uvicorn to run a local HTTP server.
    - Serves fake data generated from the specified Pydantic model.
    - Provides `GET /{resource_name}` endpoint to retrieve all generated instances.
    - Provides `GET /{resource_name}/{item_id_or_index}` endpoint to retrieve a single instance by ID (if `id` or `uuid` field exists) or by index.
    - Automatically generates OpenAPI (Swagger UI at `/docs`) and ReDoc (at `/redoc`) documentation for the mock API.
    - Supports `--host`, `--port`, `--count`, `--faker-locale`, and `--seed` options for server configuration and data generation.

### Changed
- Added `fastapi` and `uvicorn[standard]` as project dependencies.
- Created `src/pydantic_faker/server.py` module to encapsulate server logic.
- CLI in `src/pydantic_faker/cli.py` updated to call `run_server` function.
- Refined data generation loop in `run_server` to ensure consistent use of seeded Faker instances when `--count` > 1.

## [0.2.0] - 2025-05-21

### Added
- **Faker Integration**: Integrated the [Faker](https://faker.readthedocs.io/) library to generate more realistic data for common field names (e.g., `name`, `email`, `address`, `company`, etc.).
- **Locale Support**: Added `--faker-locale` CLI option to specify the locale for Faker, enabling localized data generation.
- **Seedable Generation**: Added `--seed` CLI option to provide a seed for Python's `random` module and the `Faker` instance, ensuring reproducible and deterministic data generation.
- **Pydantic Field Constraints Support**:
    - Numbers (`int`, `float`): Implemented support for `gt`, `ge`, `lt`, `le`, and `multiple_of` constraints.
    - Strings (`str`): Implemented support for `min_length` and `max_length` constraints, including for Faker-generated strings.
    - Lists (`list`): Implemented support for `min_items` and `max_items` (via Pydantic's `min_length` and `max_length` on `Field` for collections).
    - Dictionaries (`dict`): Implemented support for `min_items` and `max_items` for the number of key-value pairs.
- Enhanced generation for `uuid.UUID`, `datetime.datetime`, `datetime.date`, and `datetime.time` types to use Faker providers, improving seed determinism.
- Default string generation (when not matching a specific Faker provider by field name) now uses `Faker.sentence()` for more meaningful random strings, respecting length constraints.

### Changed
- **Core Logic Refactor**:
    - `generate_fake_data_for_model` now orchestrates Faker instance creation based on `locale` and `seed` and handles field name to Faker provider mapping.
    - `_generate_value_for_type` now accepts a `Faker` instance and `FieldInfo` to apply type-specific generation and constraints.
- Improved logic for determining and applying numerical, string, and collection size constraints.
- Test suite (`tests/test_core.py`) significantly expanded to cover Faker integration, locale, seed, and various Pydantic field constraints.

### Fixed
- Ensured deterministic output for all relevant types when a `--seed` is provided.
- Corrected issues with parsing `FieldInfo` metadata to accurately retrieve constraint values for Pydantic v2.
- Resolved `ModuleNotFoundError` for `email-validator` by adding `pydantic[email]` to project dependencies.
- Addressed various linting and static analysis issues.

## [0.1.0] - 2025-05-18

### Added
- Initial release of `pydantic-faker`.
- CLI command `generate` to produce fake data from Pydantic models.
- Dynamic loading of Pydantic models via string path.
- Support for basic Python types: `int`, `str`, `float`, `bool`.
- Support for common Python data types: `uuid.UUID`, `datetime.datetime`, `datetime.date`, `datetime.time`.
- Handling of Pydantic/typing generics: `Optional[T]`, `List[T]`, `Dict[str, T]`.
- Recursive generation for nested Pydantic models.
- Output of generated data to JSON format (stdout or file).
- Basic error handling.
- CLI structure built with Typer.
- Project setup with `pyproject.toml` and `hatchling`.
- Initial test suite with `pytest`.
- Code linting/formatting with `Ruff`, type checking with `Mypy`/`Pyright`.
