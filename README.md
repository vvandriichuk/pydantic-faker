# Pydantic Faker 🚀

**pydantic-faker** is a CLI tool designed to rapidly generate fake data based on your Pydantic models. Perfect for quickly populating databases for testing, creating mock API responses, or any scenario where you need structured fake data matching your Pydantic schemas.

[![PyPI version](https://badge.fury.io/py/pydantic-faker.svg)](https://badge.fury.io/py/pydantic-faker)
[![Python Version](https://img.shields.io/pypi/pyversions/pydantic-faker.svg)](https://pypi.org/project/pydantic-faker/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

* **CLI First**: Easy-to-use command-line interface.
* **Pydantic Powered**: Leverages your existing Pydantic models as the source of truth.
* **Dynamic Model Loading**: Load models transparently from your project's modules.
* **Fake Data Generation (`generate` command)**:
  * Supports common Python types and nested Pydantic structures.
  * Integrates with [Faker](https://faker.readthedocs.io/) for realistic data.
  * `--faker-locale` for localized data.
  * `--seed` for reproducible output.
  * Outputs to JSON (stdout or file).
  * Supports Pydantic `Field` constraints (e.g., `min_length`, `gt`, `max_items`).
* **Mock API Server (`serve` command)**:
  * Instantly serve generated Pydantic model data via a local HTTP API.
  * Powered by FastAPI and Uvicorn.
  * Auto-generated OpenAPI (Swagger UI) and ReDoc documentation.
  * Configurable host, port, data count, locale, and seed.

## Installation

```bash
pip install pydantic-faker
```

## Quick Start

### Define your Pydantic models (e.g., my_models.py):

```python
# my_models.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict # Use from typing for < Python 3.9
from uuid import UUID
from datetime import datetime, date, time

class SimpleUser(BaseModel):
    id: int
    name: str = Field(min_length=5)
    is_active: bool
    uuid: UUID
    created_at: datetime
    birth_date: date
    wakeup_time: time
    email: Optional[str] = None # Faker will generate an email if field name is "email"
    rating: Optional[float] = Field(default=None, ge=0, le=5)
    # Pydantic v2: list и dict можно использовать напрямую без typing
    tags: list[str] = Field(default_factory=list, min_length=1, max_length=3)
    metadata: Optional[dict[str, int]] = None
```

### Generate Fake Data (using generate command):

To generate one instance of SimpleUser and print to console, respecting constraints and using Faker for name and email:

```bash
pydantic-faker generate my_models:SimpleUser
```

To generate 5 instances, save to a file, use Russian locale, and a specific seed:

```bash
pydantic-faker generate my_models:SimpleUser --count 5 --output-file users.json --faker-locale ru_RU --seed 123
```

Expected output in users.json will contain 5 SimpleUser objects with Russian names/emails (if applicable Faker providers exist for ru_RU) and data respecting min_length=5 for name and 0 <= rating <= 5.

### Serve Fake Data as a Mock API (using serve command):

To serve 10 instances of SimpleUser on the default port (8000):

```bash
pydantic-faker serve my_models:SimpleUser --count 10
```

You will see output like:

```
🚀 Mock API for 'SimpleUser' available at:
   GET http://127.0.0.1:8000/simpleusers
   GET http://127.0.0.1:8000/simpleusers/<id_or_index>
📚 OpenAPI docs at: http://127.0.0.1:8000/docs
📄 ReDoc at: http://127.0.0.1:8000/redoc
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Open http://127.0.0.1:8000/docs in your browser to interact with the API.

To use a different port and a seed for the served data:

```bash
pydantic-faker serve my_models:SimpleUser --port 8001 --seed 42
```

## Usage

pydantic-faker provides two main commands: `generate` and `serve`.

### generate command

Generates fake data based on a Pydantic model and outputs it as JSON.

```bash
pydantic-faker generate [OPTIONS] MODEL_PATH
```

Arguments:
- `MODEL_PATH`: Required. The Python import path to your Pydantic model (e.g., 'my_module:MyModelClass').

Options:
- `-c, --count INTEGER`: Number of instances to generate. (Default: 1)
- `-o, --output-file PATH`: File path to save JSON data. (Default: prints to stdout)
- `-l, --faker-locale TEXT`: Locale for Faker (e.g., 'en_US', 'ru_RU').
- `-s, --seed INTEGER`: Seed for random number generators.
- `--install-completion`: Install shell completion.
- `--show-completion`: Show shell completion script.
- `--help`: Show this help message and exit.

### serve command

Generates fake data and serves it via a local HTTP mock API.

```bash
pydantic-faker serve [OPTIONS] MODEL_PATH
```

Arguments:
- `MODEL_PATH`: Required. The Python import path to your Pydantic model.

Options:
- `-c, --count INTEGER`: Number of fake instances to generate for the API. (Default: 10)
- `-l, --faker-locale TEXT`: Locale for Faker.
- `-s, --seed INTEGER`: Seed for random number generators.
- `--host TEXT`: Host to bind the server to. (Default: "127.0.0.1")
- `--port INTEGER`: Port to run the server on. (Default: 8000)
- `--help`: Show this help message and exit.

## How it Works (v0.3.0)

pydantic-faker uses the following process:

1. **Dynamic Model Loading**: Parses the MODEL_PATH to dynamically import your Pydantic BaseModel class.
2. **Faker Initialization**: Initializes a Faker instance, configured with the specified `--faker-locale` and `--seed` if provided. Python's random module is also seeded.
3. **Data Generation Loop**: For the specified `--count`:
   - Iterates through the model_fields of your Pydantic model.
   - **Faker by Field Name**: Checks if the field name matches a predefined list of common names (e.g., "email", "name", "address"). If so, uses the corresponding Faker provider.
   - **Type-Based Generation**: If no match by field name, it generates data based on the field's type annotation:
     - **Basic & Special Types**: int, float, str, bool, uuid.UUID, datetime.datetime, date, time are generated using random or Faker methods.
     - **Collections**: List[T] and Dict[str, T] are populated with a random number of items (respecting constraints).
     - **Optional & Nested**: Optional[T] fields have a chance to be None. Nested Pydantic models are generated recursively.
   - **Constraint Application**: Pydantic Field constraints (gt, le, min_length, max_length, multiple_of, etc.) are applied to the generated values. For strings from Faker, an attempt is made to fit them within length constraints.
4. **Output/Serving**:
   - `generate` command: The list of generated data dictionaries is serialized to JSON and printed to stdout or saved to a file.
   - `serve` command: The generated data is stored in memory. A FastAPI application is created with GET endpoints for the data (/{resource_name} and /{resource_name}/{id_or_index}). Uvicorn is used to run this application, providing a local mock API with Swagger UI and ReDoc documentation.

## Future Roadmap (Planned Features)

With v0.3.0 released, here's what's next:

### v0.4.0: Advanced Types & Server Enhancements
- Improved handling for more complex Pydantic/Python types like Union (beyond Optional), Literal, and Enum.
- Ability to use examples provided in pydantic.Field(examples=[...]) as a source for generated data.
- Basic query parameter filtering for the serve command (e.g., GET /mymodel?is_active=true).
- (Optional) Basic POST/PUT/DELETE mock endpoints for the serve command (in-memory changes).

### v0.5.0: LLM Integration (Experimental)
- An optional, experimental feature to use Large Language Models (e.g., via OpenAI API) for generating highly creative or context-specific textual data for certain fields, configurable via prompts.

### Beyond:
- Configuration files for more complex generation rules.
- Plugin system for custom data providers.
