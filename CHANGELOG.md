# Changelog

## [0.1.0] - 2025-05-18

### Added
- Initial release of pydantic-faker.
- CLI command `generate` to produce fake data from Pydantic models.
- Support for basic Python types (int, str, float, bool).
- Support for `UUID`, `datetime`, `date`, `time`.
- Support for `Optional[T]`, `List[T]`, `Dict[str, T]`.
- Support for nested Pydantic models.
- Output to JSON (stdout or file).
- Dynamic loading of Pydantic models via string path.
