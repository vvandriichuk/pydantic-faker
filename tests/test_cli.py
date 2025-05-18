import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from pydantic_faker.cli import app

runner = CliRunner()


def test_generate_stdout():
    """Tests the generate command piping to stdout."""
    result = runner.invoke(app, ["generate", "test_models:SimpleUser"])
    assert result.exit_code == 0
    assert "Successfully loaded model: SimpleUser" in result.stdout
    try:
        data = json.loads(
            result.stdout.split("🎉 Generation complete!")[0]
            .split("🔍 Successfully loaded model: SimpleUser")[-1]
            .strip(),
        )
        assert isinstance(data, list)
        assert len(data) == 1
        assert "id" in data[0]
        assert "name" in data[0]
    except json.JSONDecodeError:
        pytest.fail(f"Output is not valid JSON: {result.stdout}")


def test_generate_to_file(tmp_path: Path):
    """Tests the generate command writing to an output file."""
    output_file = tmp_path / "output.json"
    result = runner.invoke(app, ["generate", "test_models:SimpleUser", "--output-file", str(output_file)])

    assert result.exit_code == 0
    assert f"Data successfully saved to: {output_file}" in result.stdout
    assert output_file.exists()
    with open(output_file) as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) == 1
    assert "id" in data[0]


# TODO: Add test for serve command (when it is implemented)
# TODO: Add tests for various options of generate command (count, etc)
# TODO: Add tests for CLI script errors (invalid model path, etc)
