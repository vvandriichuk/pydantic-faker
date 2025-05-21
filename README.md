# Pydantic Faker 🚀

**pydantic-faker** is a CLI tool designed to rapidly generate fake data based on your Pydantic models. Perfect for quickly populating databases for testing, creating mock API responses, or any scenario where you need structured fake data matching your Pydantic schemas.

[![PyPI version](https://badge.fury.io/py/pydantic-faker.svg)](https://badge.fury.io/py/pydantic-faker)
[![Python Version](https://img.shields.io/pypi/pyversions/pydantic-faker.svg)](https://pypi.org/project/pydantic-faker/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
<!-- Future: Add CI/CD, code coverage badges -->

Inspired by the need for a simple, CLI-first way to leverage Pydantic's schema definition power for data generation.

## Features

*   **CLI First**: Easy-to-use command-line interface.
*   **Pydantic Powered**: Leverages your existing Pydantic models as the source of truth for data structure.
*   **Dynamic Model Loading**: Load models transparently from your project's modules.
*   **Basic Type Generation**: Supports common Python types (`int`, `str`, `float`, `bool`, `UUID`, `datetime`, `date`, `time`).
*   **Nested Structures**: Handles nested Pydantic models, `List[T]`, `Dict[str, T]`, and `Optional[T]`.
*   **JSON Output**: Outputs generated data in JSON format, either to stdout or a file.
*   **Faker Integration**: Uses Faker library to generate more realistic data for common field names (e.g., name, email, address).
*   **Locale Support**: `--faker-locale` option to generate data in specific languages/regions.
*   **Seedable Generation**: `--seed` option for reproducible data generation.
*   *(Upcoming)* Constraint Support: Respect Pydantic `Field` constraints.
*   *(Upcoming)* Mock API Server: Instantly serve your generated data via a local HTTP server.

## Installation

```bash
pip install pydantic-faker
```

## Quick Start

Define your Pydantic models in a Python file (e.g., my_models.py in your project's root directory):

```python
# my_models.py
from pydantic import BaseModel
from typing import Optional, List, Dict # Use from typing for < Python 3.9
from uuid import UUID
from datetime import datetime, date, time

class SimpleUser(BaseModel):
    id: int
    name: str
    is_active: bool
    uuid: UUID
    created_at: datetime
    birth_date: date
    wakeup_time: time
    email: Optional[str] = None
    rating: Optional[float] = None

class NestedItem(BaseModel):
    item_id: str
    value: float
    tags: List[str]

class ComplexOrder(BaseModel):
    order_id: int
    user: SimpleUser
    items: List[NestedItem]
    metadata: Optional[Dict[str, int]] = None
```

Run pydantic-faker from your terminal (ensure you are in the same directory as my_models.py or that my_models.py is in your PYTHONPATH):

To generate one instance of SimpleUser and print to console:

```bash
pydantic-faker generate my_models:SimpleUser
```

To generate 5 instances of ComplexOrder and save to a file named orders.json:

```bash
pydantic-faker generate my_models:ComplexOrder --count 5 --output-file orders.json
```

To generate data using a specific locale and seed:

```bash
pydantic-faker generate my_models:SimpleUser --faker-locale ru_RU --seed 123
```

You should see output similar to this (values will be random):

```json
// Output for: pydantic-faker generate my_models:SimpleUser
[
  {
    "id": 123,
    "name": "Иван Петров",
    "is_active": true,
    "uuid": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "created_at": "2023-10-27T10:30:00+00:00",
    "birth_date": "2023-01-15",
    "wakeup_time": "08:00:00",
    "email": "ivan.petrov@example.ru",
    "rating": null
  }
]
```

## Usage

The primary command for generating data is `generate`.

```bash
pydantic-faker generate [OPTIONS] MODEL_PATH
```

### Arguments:

**MODEL_PATH**: Required. The Python import path to your Pydantic model, in the format 'your_module:YourModelClass' or 'your_package.sub_module:YourModelClass'. The specified module must be importable from your current working directory or be available on your PYTHONPATH.

### Options:

- `-c, --count INTEGER`: The number of fake data instances to generate for the specified model.
(Default: 1)

- `-o, --output-file PATH`: The file path where the generated JSON data should be saved. If this option is not provided, the JSON data will be printed to the standard output (stdout).

- `-l, --faker-locale TEXT`: Locale to use for Faker (e.g., 'en_US', 'ru_RU', 'ja_JP'). If not provided, Faker's default is used.

- `-s, --seed INTEGER`: Seed for the random number generator (for reproducible results).

- `--install-completion`: Install command-line completion for your current shell.

- `--show-completion`: Show the command-line completion script for your current shell.

- `--help`: Show this help message and exit.

(The `serve` command is planned for a future release and is currently hidden from general help.)

## How it Works (v0.2.0 Development)

For the current version in development (v0.2.0), pydantic-faker operates by:

1. **Dynamic Model Loading**: It takes the MODEL_PATH string, splits it into a module path and class name, and dynamically imports your Pydantic model class. It ensures that the loaded class is indeed a subclass of Pydantic's BaseModel.

2. **Field Inspection**: It iterates through the model_fields of your Pydantic model.

3. **Type-Based Data Generation**: For each field, it generates a random value based on its type annotation:

   - **Basic Types**:
     - `int`: A random integer.
     - `float`: A random float.
     - `str`: If the field name matches a common pattern (e.g., "name", "email", "address"), data is generated using the appropriate Faker provider. Otherwise, a random sentence is generated.
     - `bool`: Randomly True or False.

   - **Special Python Types**:
     - `uuid.UUID`: A Faker-generated Version 4 UUID (seedable), converted to a string.
     - `datetime.datetime`: A Faker-generated recent datetime object (UTC, timezone-aware, seedable), converted to an ISO 8601 string.
     - `datetime.date`: A recent date object, converted to an ISO 8601 string.
     - `datetime.time`: A random time object, converted to an ISO 8601 string.

   - **Generic Types**:
     - `Optional[T]` (or `T | None`): There's a 50% chance the value will be None. Otherwise, a value of type T is generated.
     - `List[T]`: A list containing 1 to 3 randomly generated items of type T.
     - `Dict[str, T]`: A dictionary with 1 to 3 keys (generic strings like "key_1") and randomly generated values of type T.

   - **Nested Pydantic Models**: If a field's type is another Pydantic BaseModel, pydantic-faker recursively calls its generation logic for that nested model.

   - `typing.Any`: A placeholder string like "any_value_placeholder" is generated.

   - **Other Unsupported Types**: A string indicating the unsupported type (e.g., "unsupported_type_<type_name>") is generated.

The generated data for each instance is collected into a Python dictionary. If multiple instances (--count > 1) are requested, a list of these dictionaries is created. Finally, this list is serialized to JSON and either printed to stdout or written to the specified output file.

Note: The current version includes Faker integration for common field names, but does not yet respect constraints defined in Pydantic Field objects. This feature is planned for the complete v0.2.0 release.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
   - Please ensure your commit messages are clear and descriptive.
4. Ensure Code Quality:
   - Run `ruff . --fix` for linting and formatting.
   - Run `mypy src/` for type checking.
   - Add tests for your new feature or bug fix.
   - Ensure all tests pass with `pytest`.
5. Push to the Branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

We use `ruff` for comprehensive linting and formatting, and `mypy` for static type checking. Adherence to these standards is expected for contributions.

## Future Roadmap (Planned Features)

We have exciting plans for pydantic-faker! Here's a glimpse of what's coming:

### v0.2.0: Smarter Faker & Basic Constraints (Partially Implemented)

* **Implemented:**
  * Integration with the [Faker](https://faker.readthedocs.io/) library for generating realistic data for common field names.
  * `--seed` option for reproducible random data generation.
  * `--faker-locale` option for localized data generation.
* **Planned for v0.2.0 Completion:**
  * Ability to respect basic Pydantic `Field` constraints (e.g., `min_length`, `max_length` for strings; `gt`, `lt`, `ge`, `le` for numbers; `min_items`, `max_items` for lists).
  * (Optional) More advanced type-to-Faker-provider mappings (beyond field names).

### v0.3.0: Hello, Server!

- Implementation of the `serve` command: `pydantic-faker serve my_module:MyModel` will generate data and instantly host it on a local HTTP server, providing mock API endpoints.

### v0.4.0: Advanced Types & Server Enhancements

- Improved handling for more complex Pydantic/Python types like Union (beyond Optional), Literal, and Enum.
- Ability to use examples provided in pydantic.Field(examples=[...]) as a source for generated data.
- Basic query parameter filtering for the `serve` command (e.g., GET /mymodel?is_active=true).

### v0.5.0: LLM Integration (Experimental)

- An optional, experimental feature to use Large Language Models (e.g., via OpenAI API) for generating highly creative or context-specific textual data for certain fields, configurable via prompts.

### Beyond:

- Configuration files for more complex generation rules.
- Plugin system for custom data providers.
- Deeper integration with Field metadata for fine-tuning generation.

Your feedback, feature requests, and contributions are highly encouraged to help prioritize and shape these future developments!

## License

Distributed under the MIT License. See LICENSE for more information.
