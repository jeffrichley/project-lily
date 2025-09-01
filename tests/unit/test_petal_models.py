"""Unit tests for Petal models."""


import pytest
from pydantic import ValidationError

from lily.petal.enums import IfErrorPolicy
from lily.petal.models import PetalFile, Retry, Step


@pytest.mark.unit
class TestRetry:
    """Test Retry model."""

    def test_creates_valid_retry_config(self) -> None:
        """Test that Retry can be created with valid parameters."""
        # Arrange - No setup needed

        # Act - Create retry config
        retry = Retry(max_attempts=3)

        # Assert - Verify default values are set correctly
        assert retry.max_attempts == 3
        assert retry.backoff_factor == 1.5
        assert retry.jitter is True
        assert retry.max_delay is None

    def test_creates_retry_with_all_parameters(self) -> None:
        """Test that Retry can be created with all parameters."""
        # Arrange - No setup needed

        # Act - Create retry config with all parameters
        retry = Retry(max_attempts=5, backoff_factor=2.0, jitter=False, max_delay=60.0)

        # Assert - Verify all parameters are set correctly
        assert retry.max_attempts == 5
        assert retry.backoff_factor == 2.0
        assert retry.jitter is False
        assert retry.max_delay == 60.0

    def test_raises_on_invalid_max_attempts(self) -> None:
        """Test that Retry raises error for invalid max_attempts."""
        # Arrange - No setup needed

        # Act & Assert - Verify validation error is raised
        with pytest.raises(ValidationError, match="greater than 0"):
            Retry(max_attempts=0)

    def test_raises_on_invalid_backoff_factor(self) -> None:
        """Test that Retry raises error for invalid backoff_factor."""
        # Arrange - No setup needed

        # Act & Assert - Verify validation error is raised
        with pytest.raises(ValidationError, match="greater than 0"):
            Retry(max_attempts=1, backoff_factor=0)

    def test_raises_on_invalid_max_delay(self) -> None:
        """Test that Retry raises error for invalid max_delay."""
        # Arrange - No setup needed

        # Act & Assert - Verify validation error is raised
        with pytest.raises(ValidationError, match="greater than 0"):
            Retry(max_attempts=1, max_delay=0)


@pytest.mark.unit
class TestStep:
    """Test Step model."""

    def test_creates_valid_step(self) -> None:
        """Test that Step can be created with valid parameters."""
        # Arrange - No setup needed

        # Act - Create step with valid parameters
        step_data = {
            "id": "test-step",
            "uses": "shell.run",
            "reads": ["cmd"],
            "writes": ["output"],
            "with": {"cmd": "echo hello"},
        }
        step = Step.model_validate(step_data)

        # Assert - Verify all fields are set correctly
        assert step.id == "test-step"
        assert step.uses == "shell.run"
        assert step.reads == ["cmd"]
        assert step.writes == ["output"]
        assert step.with_ == {"cmd": "echo hello"}
        assert step.when is None
        assert step.if_error == IfErrorPolicy.FAIL
        assert step.retry is None

    def test_creates_step_with_all_parameters(self) -> None:
        """Test that Step can be created with all parameters."""
        # Arrange - Create retry config
        retry = Retry(max_attempts=3)

        # Act - Create step with all parameters
        step_data = {
            "id": "complex-step",
            "uses": "llm.generate",
            "reads": ["prompt", "context"],
            "writes": ["response"],
            "with": {"model": "gpt-4", "prompt": "{{ prompt }}"},
            "when": "{{ context|length > 0 }}",
            "if_error": IfErrorPolicy.RETRY,
            "retry": retry,
        }
        step = Step.model_validate(step_data)

        # Assert - Verify all fields are set correctly
        assert step.id == "complex-step"
        assert step.uses == "llm.generate"
        assert step.reads == ["prompt", "context"]
        assert step.writes == ["response"]
        assert step.with_ == {"model": "gpt-4", "prompt": "{{ prompt }}"}
        assert step.when == "{{ context|length > 0 }}"
        assert step.if_error == IfErrorPolicy.RETRY
        assert step.retry == retry

    def test_raises_on_empty_id(self) -> None:
        """Test that Step raises error for empty ID."""
        # Arrange - No setup needed

        # Act & Assert - Verify validation error is raised
        with pytest.raises(ValidationError, match="cannot be empty"):
            Step(id="", uses="test")

    def test_raises_on_whitespace_id(self) -> None:
        """Test that Step raises error for whitespace-only ID."""
        # Arrange - No setup needed

        # Act & Assert - Verify validation error is raised
        with pytest.raises(ValidationError, match="cannot be empty"):
            Step(id="   ", uses="test")

    def test_raises_on_id_with_spaces(self) -> None:
        """Test that Step raises error for ID with spaces."""
        # Arrange - No setup needed

        # Act & Assert - Verify validation error is raised
        with pytest.raises(ValidationError, match="cannot contain spaces"):
            Step(id="test step", uses="test")

    def test_raises_on_empty_uses(self) -> None:
        """Test that Step raises error for empty tool name."""
        # Arrange - No setup needed

        # Act & Assert - Verify validation error is raised
        with pytest.raises(ValidationError, match="cannot be empty"):
            Step(id="test", uses="")

    def test_raises_on_whitespace_uses(self) -> None:
        """Test that Step raises error for whitespace-only tool name."""
        # Arrange - No setup needed

        # Act & Assert - Verify validation error is raised
        with pytest.raises(ValidationError, match="cannot be empty"):
            Step(id="test", uses="   ")

    def test_strips_whitespace_from_id_and_uses(self) -> None:
        """Test that Step strips whitespace from ID and uses."""
        # Arrange - No setup needed

        # Act - Create step with whitespace in ID and uses
        step = Step(id="  test-id  ", uses="  test.tool  ")

        # Assert - Verify whitespace is stripped
        assert step.id == "test-id"
        assert step.uses == "test.tool"

    def test_uses_alias_for_with_field(self) -> None:
        """Test that Step uses 'with' alias for with_ field."""
        # Arrange - No setup needed

        # Act - Create step with with_ parameter
        step_data = {"id": "test", "uses": "test.tool", "with": {"param": "value"}}
        step = Step.model_validate(step_data)

        # Assert - Verify with_ field is set correctly
        assert step.with_ == {"param": "value"}


@pytest.mark.unit
class TestPetalFile:
    """Test PetalFile model."""

    def test_creates_valid_petal_file(self) -> None:
        """Test that PetalFile can be created with minimal parameters."""
        # Arrange - Create a step
        step = Step(id="test-step", uses="shell.run")

        # Act - Create petal file with minimal parameters
        petal_file = PetalFile(name="test-workflow", steps=[step])

        # Assert - Verify default values are set correctly
        assert petal_file.version == "0.1"
        assert petal_file.name == "test-workflow"
        assert petal_file.description is None
        assert petal_file.params == {}
        assert petal_file.defaults == {}
        assert petal_file.env == {}
        assert petal_file.secrets == []
        assert petal_file.macros == {}
        assert petal_file.imports == []
        assert petal_file.steps == [step]

    def test_creates_petal_file_with_all_parameters(self) -> None:
        """Test that PetalFile can be created with all parameters."""
        # Arrange - Create a step
        step = Step(id="test-step", uses="shell.run")

        # Act - Create petal file with all parameters
        petal_file = PetalFile(
            version="0.2",
            name="complex-workflow",
            description="A complex workflow",
            params={"input": "value"},
            defaults={"llm.model": "gpt-4"},
            env={"API_KEY": "$API_KEY"},
            secrets=["API_KEY", "SECRET_TOKEN"],
            macros={"notify": [{"slack.post": {"text": "{{ message }}"}}]},
            imports=[{"path": "./partials/foo.petal"}],
            steps=[step],
        )

        # Assert - Verify all parameters are set correctly
        assert petal_file.version == "0.2"
        assert petal_file.name == "complex-workflow"
        assert petal_file.description == "A complex workflow"
        assert petal_file.params == {"input": "value"}
        assert petal_file.defaults == {"llm.model": "gpt-4"}
        assert petal_file.env == {"API_KEY": "$API_KEY"}
        assert petal_file.secrets == ["API_KEY", "SECRET_TOKEN"]
        assert petal_file.macros == {
            "notify": [{"slack.post": {"text": "{{ message }}"}}]
        }
        assert petal_file.imports == [{"path": "./partials/foo.petal"}]
        assert petal_file.steps == [step]

    def test_raises_on_empty_version(self) -> None:
        """Test that PetalFile raises error for empty version."""
        # Arrange - Create a step
        step = Step(id="test", uses="test")

        # Act & Assert - Verify validation error is raised
        with pytest.raises(ValidationError, match="cannot be empty"):
            PetalFile(name="test", steps=[step], version="")

    def test_raises_on_empty_name(self) -> None:
        """Test that PetalFile raises error for empty name."""
        # Arrange - Create a step
        step = Step(id="test", uses="test")

        # Act & Assert - Verify validation error is raised
        with pytest.raises(ValidationError, match="cannot be empty"):
            PetalFile(name="", steps=[step])

    def test_raises_on_name_with_spaces(self) -> None:
        """Test that PetalFile raises error for name with spaces."""
        # Arrange - Create a step
        step = Step(id="test", uses="test")

        # Act & Assert - Verify validation error is raised
        with pytest.raises(ValidationError, match="cannot contain spaces"):
            PetalFile(name="test workflow", steps=[step])

    def test_raises_on_empty_steps(self) -> None:
        """Test that PetalFile raises error for empty steps list."""
        # Arrange - No setup needed

        # Act & Assert - Verify validation error is raised
        with pytest.raises(ValidationError, match="At least one step is required"):
            PetalFile(name="test", steps=[])

    def test_strips_whitespace_from_version_and_name(self) -> None:
        """Test that PetalFile strips whitespace from version and name."""
        # Arrange - Create a step
        step = Step(id="test", uses="test")

        # Act - Create petal file with whitespace in version and name
        petal_file = PetalFile(
            version="  0.2  ", name="  test-workflow  ", steps=[step]
        )

        # Assert - Verify whitespace is stripped
        assert petal_file.version == "0.2"
        assert petal_file.name == "test-workflow"

    def test_model_dump_returns_dict(self) -> None:
        """Test that model_dump returns a dictionary."""
        # Arrange - Create petal file
        step = Step(id="test", uses="test")
        petal_file = PetalFile(name="test", steps=[step])

        # Act - Call model_dump
        result = petal_file.model_dump()

        # Assert - Verify result is a dict with expected content
        assert isinstance(result, dict)
        assert result["name"] == "test"
        assert result["version"] == "0.1"
        assert len(result["steps"]) == 1

    def test_model_dump_json_returns_string(self) -> None:
        """Test that model_dump_json returns a JSON string."""
        # Arrange - Create petal file
        step = Step(id="test", uses="test")
        petal_file = PetalFile(name="test", steps=[step])

        # Act - Call model_dump_json
        result = petal_file.model_dump_json()

        # Assert - Verify result is a JSON string with expected content
        assert isinstance(result, str)
        assert '"name":"test"' in result
        assert '"version":"0.1"' in result
