"""Unit tests for Petal enums."""

import pytest

from lily.petal.enums import IfErrorPolicy, StepStatus


@pytest.mark.unit
class TestIfErrorPolicy:
    """Test IfErrorPolicy enum."""

    def test_enum_values_are_correct(self) -> None:
        """Test that enum has the expected values."""
        # Arrange - No setup needed for enum value testing

        # Act - Access enum values

        # Assert - Verify enum values match expected strings
        assert IfErrorPolicy.FAIL.value == "fail"
        assert IfErrorPolicy.SKIP.value == "skip"
        assert IfErrorPolicy.RETRY.value == "retry"

    def test_enum_membership(self) -> None:
        """Test that enum values are valid members."""
        # Arrange - No setup needed for enum membership testing

        # Act - Check membership of enum values

        # Assert - Verify valid values are members and invalid values are not
        assert "fail" in IfErrorPolicy
        assert "skip" in IfErrorPolicy
        assert "retry" in IfErrorPolicy
        assert "invalid" not in IfErrorPolicy

    def test_enum_iteration(self) -> None:
        """Test that enum can be iterated over."""
        # Arrange - No setup needed for enum iteration testing

        # Act - Convert enum to list
        values = list(IfErrorPolicy)

        # Assert - Verify all expected values are present
        assert len(values) == 3
        assert IfErrorPolicy.FAIL in values
        assert IfErrorPolicy.SKIP in values
        assert IfErrorPolicy.RETRY in values


@pytest.mark.unit
class TestStepStatus:
    """Test StepStatus enum."""

    def test_enum_values_are_correct(self) -> None:
        """Test that enum has the expected values."""
        # Arrange - No setup needed for enum value testing

        # Act - Access enum values

        # Assert - Verify enum values match expected strings
        assert StepStatus.PENDING.value == "pending"
        assert StepStatus.RUNNING.value == "running"
        assert StepStatus.COMPLETED.value == "completed"
        assert StepStatus.FAILED.value == "failed"
        assert StepStatus.SKIPPED.value == "skipped"
        assert StepStatus.RETRYING.value == "retrying"

    def test_enum_membership(self) -> None:
        """Test that enum values are valid members."""
        # Arrange - No setup needed for enum membership testing

        # Act - Check membership of enum values

        # Assert - Verify valid values are members and invalid values are not
        assert "pending" in StepStatus
        assert "running" in StepStatus
        assert "completed" in StepStatus
        assert "failed" in StepStatus
        assert "skipped" in StepStatus
        assert "retrying" in StepStatus
        assert "invalid" not in StepStatus

    def test_enum_iteration(self) -> None:
        """Test that enum can be iterated over."""
        # Arrange - No setup needed for enum iteration testing

        # Act - Convert enum to list
        values = list(StepStatus)

        # Assert - Verify all expected values are present
        assert len(values) == 6
        assert StepStatus.PENDING in values
        assert StepStatus.RUNNING in values
        assert StepStatus.COMPLETED in values
        assert StepStatus.FAILED in values
        assert StepStatus.SKIPPED in values
        assert StepStatus.RETRYING in values
