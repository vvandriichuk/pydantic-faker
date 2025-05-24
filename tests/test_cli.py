import json
from pathlib import Path
from unittest import mock

import pytest
from typer.testing import CliRunner

from pydantic_faker.cli import app

runner = CliRunner()


def test_generate_stdout_uses_faker():
    """Tests that the generate command uses Faker for known field names."""
    result = runner.invoke(app, ["generate", "test_models:SimpleUser"])
    assert result.exit_code == 0
    assert "Successfully loaded model: SimpleUser" in result.stdout
    try:
        data_list = json.loads(
            result.stdout.split("🎉 Generation complete!")[0]
            .split("🔍 Successfully loaded model: SimpleUser")[-1]
            .strip(),
        )
        data = data_list[0]
        assert isinstance(data, dict)
        assert "id" in data
        if data["email"] is not None:
            assert isinstance(data["email"], str)
            assert "@" in data["email"]
        assert len(data["name"].split()) >= 2
        assert data["name"] != f"random_string_{data['id']}"
    except (json.JSONDecodeError, IndexError, KeyError) as e:
        pytest.fail(f"Output processing error or unexpected data: {e}\nOutput: {result.stdout}")


def test_generate_to_file(tmp_path: Path):
    """Tests the generate command writing to an output file."""
    output_file = tmp_path / "output.json"
    result = runner.invoke(app, ["generate", "test_models:SimpleUser", "--output-file", str(output_file)])

    assert result.exit_code == 0
    assert f"Data successfully saved to: {output_file}" in result.stdout
    assert output_file.exists()
    with output_file.open("r", encoding="utf-8") as f:
        data_list = json.load(f)
    assert isinstance(data_list, list)
    assert len(data_list) == 1
    data = data_list[0]
    assert "id" in data
    if data["email"] is not None:
        assert isinstance(data["email"], str)
        assert "@" in data["email"]


def test_generate_with_seed_is_deterministic():
    """Tests that using the same seed produces the same output."""
    seed = 123
    result1 = runner.invoke(app, ["generate", "test_models:ComplexOrder", "--seed", str(seed)])
    assert result1.exit_code == 0

    result2 = runner.invoke(app, ["generate", "test_models:ComplexOrder", "--seed", str(seed)])
    assert result2.exit_code == 0

    assert result1.stdout == result2.stdout, "Output with the same seed should be identical"

    result3 = runner.invoke(app, ["generate", "test_models:ComplexOrder", "--seed", "456"])
    assert result3.exit_code == 0
    assert result1.stdout != result3.stdout, "Output with different seeds should differ"


def test_generate_with_locale():
    """Tests the --faker-locale option."""
    locale = "ru_RU"
    result = runner.invoke(app, ["generate", "test_models:SimpleUser", "--faker-locale", locale])
    assert result.exit_code == 0
    assert f"Using Faker locale: {locale}" in result.stdout
    assert "Successfully loaded model: SimpleUser" in result.stdout
    try:
        data_list = json.loads(
            result.stdout.split("🎉 Generation complete!")[0]
            .split(f"🌍 Using Faker locale: {locale}")[-1]
            .split("🔍 Successfully loaded model: SimpleUser")[-1]
            .strip(),
        )
        assert len(data_list) > 0
    except (json.JSONDecodeError, IndexError) as e:
        pytest.fail(f"Locale output processing error: {e}\nOutput: {result.stdout}")


@mock.patch("pydantic_faker.cli.run_server")
def test_serve_command_calls_run_server(mock_run_server):
    """Tests that the 'serve' command calls the run_server function with correct defaults."""
    model_arg = "test_models:SimpleUser"
    result = runner.invoke(app, ["serve", model_arg])

    assert result.exit_code == 0

    mock_run_server.assert_called_once_with(
        model_path_str=model_arg,
        count=10,
        faker_locale=None,
        seed=None,
        host="127.0.0.1",
        port=8000,
    )


@mock.patch("pydantic_faker.cli.run_server")
def test_serve_command_with_options(mock_run_server):
    """Tests the 'serve' command with custom options."""
    model_arg = "test_models:ComplexOrder"
    custom_port = 8088
    custom_count = 7
    custom_locale = "fr_FR"
    custom_seed = 777

    result = runner.invoke(
        app,
        [
            "serve",
            model_arg,
            "--port",
            str(custom_port),
            "--count",
            str(custom_count),
            "--faker-locale",
            custom_locale,
            "--seed",
            str(custom_seed),
        ],
    )

    assert result.exit_code == 0
    mock_run_server.assert_called_once_with(
        model_path_str=model_arg,
        count=custom_count,
        faker_locale=custom_locale,
        seed=custom_seed,
        host="127.0.0.1",
        port=custom_port,
    )
