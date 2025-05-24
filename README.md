# Pydantic Faker 🚀

**pydantic-faker** is a CLI tool designed to rapidly generate fake data based on your Pydantic models. Perfect for quickly populating databases for testing, creating mock API responses, or any scenario where you need structured fake data matching your Pydantic schemas.

[![PyPI version](https://badge.fury.io/py/pydantic-faker.svg)](https://badge.fury.io/py/pydantic-faker)
[![Python Version](https://img.shields.io/pypi/pyversions/pydantic-faker.svg)](https://pypi.org/project/pydantic-faker/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Inspired by the need for a simple, CLI-first way to leverage Pydantic's schema definition power for data generation and mock API serving.

## Features

- **CLI First**: Easy-to-use command-line interface.
- **Pydantic Powered**: Leverages your existing Pydantic models as the source of truth.
- **Dynamic Model Loading**: Load models transparently from your project's modules.
- **Advanced Fake Data Generation (`generate` command)**:
  - Supports common Python types (`int`, `str`, `float`, `bool`, `UUID`, `datetime`, `date`, `time`).
  - Handles nested Pydantic structures, `List[T]`, `Dict[str, T]`, and `Optional[T]`.
  - **Advanced Type Support**: Generates data for `Union` (non-Optional), `Literal`, and `enum.Enum` types.
  - **Field Examples Usage**: Can utilize values from `Field(examples=[...])` with a configurable probability.
  - Integrates with [Faker](https://faker.readthedocs.io/) for realistic data for common field names.
  - `--faker-locale` for localized data.
  - `--seed` for reproducible output.
  - Outputs to JSON (stdout or file).
  - Supports Pydantic `Field` constraints (e.g., `min_length`, `gt`, `max_items`).
- **Enhanced Mock API Server (`serve` command)**:
  - Instantly serve generated Pydantic model data via a local HTTP API.
  - Powered by FastAPI and Uvicorn.
  - **CRUD Operations**: Supports `GET` (all & by ID/index), `POST` (create), `PUT` (update by ID/index), and `DELETE` (by ID/index) for in-memory data manipulation.
  - **Basic Filtering**: Allows simple query parameter filtering for `GET` requests on collections (e.g., `?field_name=value`).
  - Auto-generated OpenAPI (Swagger UI) and ReDoc documentation.
  - Configurable host, port, data count, locale, and seed.

## Installation

```bash
pip install pydantic-faker
```

## Quick Start

### Define your Pydantic models

Create a file with your Pydantic models (e.g., `my_models.py`):

```python
# my_models.py
import enum
from pydantic import BaseModel, Field, EmailStr, HttpUrl
# For Python 3.10+ you can use `int | str` instead of `Union[int, str]`
# and `list[str]` instead of `List[str]`
from typing import Optional, List, Dict, Union, Literal, Any
from uuid import UUID
from datetime import datetime, date, time

class UserStatus(enum.Enum):
    ACTIVE = "active"
    PENDING = "pending_approval"
    INACTIVE = "inactive"

class User(BaseModel):
    id: int = Field(gt=0)
    username: str = Field(min_length=3, max_length=20, examples=["john_doe", "jane_doe"])
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=18, le=100)
    role: Literal["guest", "user", "admin"] = Field(examples=["user"])
    status: UserStatus = Field(examples=[UserStatus.ACTIVE, UserStatus.PENDING])
    member_type: Union[Literal["free"], Literal["premium"], Literal["vip"]] = "free"
    last_login: Optional[datetime] = None
    # Pydantic v2: list и dict можно использовать напрямую без typing
    tags: list[str] = Field(default_factory=list, min_length=0, max_length=5)
    profile_data: Optional[Dict[str, Any]] = None
```

### Generate Fake Data (using `generate` command)

Generate one instance of User, utilizing examples and Faker where applicable:

```bash
pydantic-faker generate my_models:User
```

Output will be a JSON array with one User object. The username might be "john_doe", role might be "user", and status could be "active" due to the examples.

Generate 5 instances, save to a file, use German locale, and a specific seed:

```bash
pydantic-faker generate my_models:User --count 5 --output-file users.json --faker-locale de_DE --seed 42
```

### Serve Fake Data as a Mock API (using `serve` command)

Serve 10 instances of User on port 8001 with a seed:

```bash
pydantic-faker serve my_models:User --count 10 --port 8001 --seed 123
```

Output in terminal:

```
🚀 Starting mock API server for model at: my_models:User
   Serving 10 fake instance(s).
   🌱 Using random seed: 123
🚀 Mock API for 'User' available at:
   GET http://127.0.0.1:8001/users
   GET http://127.0.0.1:8001/users/<id_or_index>
   POST http://127.0.0.1:8001/users
   PUT http://127.0.0.1:8001/users/<id_or_index>
   DELETE http://127.0.0.1:8001/users/<id_or_index>
📚 OpenAPI docs at: http://127.0.0.1:8001/docs
📄 ReDoc at: http://127.0.0.1:8001/redoc
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
```

### Interact with the API

1. Open http://127.0.0.1:8001/docs in your browser.
2. Try GET http://127.0.0.1:8001/users?is_active=true (if is_active was a field) to test filtering.
3. Use curl or Postman to test POST, PUT, DELETE requests. For example, to create a new user:

```bash
curl -X POST "http://127.0.0.1:8001/users" \
-H "Content-Type: application/json" \
-d '{
      "id": 101,
      "username": "new_user_cli",
      "email": "new@example.com",
      "role": "guest",
      "status": "pending_approval",
      "is_active": false
    }'
# (Ensure payload matches all required fields of your User model)
```

## Usage

`pydantic-faker` provides two main commands: `generate` and `serve`.

### `generate` command

Generates fake data based on a Pydantic model and outputs it as JSON.

```bash
pydantic-faker generate [OPTIONS] MODEL_PATH
```

**Arguments:**
- `MODEL_PATH`: Path to your Pydantic model in format `module:ClassName`

**Options:**
- `--count, -c`: Number of instances to generate
- `--output-file, -o`: Output file path (optional, defaults to stdout)
- `--faker-locale, -l`: Faker locale for localized data
- `--seed, -s`: Random seed for reproducible output
- `--install-completion`, `--show-completion`, `--help`: Standard CLI options

### `serve` command

Generates fake data and serves it via a local HTTP mock API with CRUD capabilities.

```bash
pydantic-faker serve [OPTIONS] MODEL_PATH
```

**Arguments:**
- `MODEL_PATH`: Path to your Pydantic model in format `module:ClassName`

**Options:**
- `--count, -c`: Number of instances to generate and serve
- `--faker-locale, -l`: Faker locale for localized data
- `--seed, -s`: Random seed for reproducible output
- `--host`: Host address (default: 127.0.0.1)
- `--port`: Port number (default: 8000)
- `--help`: Show help message

## How it Works (v0.4.0)

`pydantic-faker` uses the following process:

1. **Dynamic Model Loading**: Parses `MODEL_PATH` to import your Pydantic BaseModel.

2. **Faker Initialization**: Initializes a Faker instance (respecting `--faker-locale` and `--seed`). Python's random is also seeded.

3. **Data Generation Loop**: For each of the `--count` instances:
   - Iterates through model fields.
   - **Field examples Priority**: If `Field(examples=[...])` is present and a random chance (default ~30%) occurs, a value is picked from the examples.
   - **Faker by Field Name**: If no example is used, checks if the field name matches a predefined list (e.g., "email", "name"). If so, uses the corresponding Faker provider.
   - **Type-Based Generation**: Otherwise, generates data based on the field's type:
     - **Advanced Types**: `Union[A, B]`, `Literal["a", "b"]`, and `enum.Enum` are handled by randomly selecting an appropriate option/value.
     - **Basic & Special Types**: `int`, `str`, `float`, `bool`, `uuid.UUID`, `datetime`, `date`, `time` are generated using random or Faker methods.
     - **Collections**: `List[T]` and `Dict[str, T]` are populated (respecting count constraints).
     - **Optional & Nested**: `Optional[T]` fields may be None. Nested Pydantic models are generated recursively.
   - **Constraint Application**: Pydantic Field constraints (`gt`, `min_length`, etc.) are applied.

4. **Output/Serving**:
   - **`generate` command**: Outputs JSON to stdout or a file.
   - **`serve` command**: Data is stored in-memory. A FastAPI app is created with GET (all, by ID/index, with basic filtering), POST, PUT, and DELETE endpoints. Uvicorn runs this app, providing a local mock API with Swagger UI/ReDoc.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Future Roadmap (Planned Features)

With v0.4.0 released, here's what's next:

### v0.5.0: LLM Integration (Experimental) & Further Enhancements

- An optional, experimental feature to use Large Language Models (e.g., via OpenAI API) for generating highly creative or context-specific textual data.
- More robust query parameter filtering for the `serve` command (e.g., numeric ranges, case-insensitivity for strings).
- Support for more Pydantic Field constraints if any were missed.
- Configuration files for more complex or reusable generation rules.

### Beyond:

- Plugin system for custom data providers.
- Deeper integration with Field metadata for fine-tuning generation.

## License

MIT License

Copyright (c) 2025 Viktor Andriichuk

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
