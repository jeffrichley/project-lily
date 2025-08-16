"""Core Petal workflow executor."""

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import ruamel.yaml
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from lily.petal.enums import StepStatus
from lily.petal.executor.state import WorkflowState
from lily.petal.executor.tools import ToolContext
from lily.petal.executor.types import StepResultDict
from lily.petal.models_strict import PetalFile, StepConfig
from lily.petal.tool_registry import tool_registry


class PetalExecutor:
    """Executes Petal workflow files."""

    def __init__(self) -> None:
        """Initialize the executor."""
        self.logger = structlog.get_logger()

    def load_petal_file(self, file_path: Path) -> PetalFile:
        """Load and parse a Petal workflow file."""
        with open(file_path) as f:
            yaml_content = f.read()

        # Parse YAML
        yaml = ruamel.yaml.YAML(typ="safe")
        data = yaml.load(yaml_content)

        # Convert to Pydantic model
        petal_file = PetalFile.model_validate(data)
        self.logger.info("Loaded Petal file", path=str(file_path), name=petal_file.name)
        return petal_file

    def execute(
        self,
        petal_file: PetalFile,
        run_dir: Path | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Execute a Petal workflow."""
        # Generate run ID
        run_id = f"run_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"

        # Set up run directory
        run_dir = Path.cwd() / "runs" / run_id if run_dir is None else run_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        # Initialize workflow state
        state = WorkflowState(
            run_id=run_id,
            run_dir=run_dir,
            params=petal_file.params,
            env=petal_file.env,
        )

        self.logger.info(
            "Starting workflow execution",
            name=petal_file.name,
            run_id=run_id,
            run_dir=str(run_dir),
            dry_run=dry_run,
        )

        if dry_run:
            return self._dry_run(petal_file, state)

        # Execute steps
        for step in petal_file.steps:
            try:
                self._execute_step(step, state)
            except Exception as e:
                self.logger.error(
                    "Step execution failed",
                    step_id=step.id,
                    error=str(e),
                    if_error=step.if_error,
                )

                # Handle error based on policy
                if step.if_error == "fail":
                    raise
                elif step.if_error == "skip":
                    self.logger.info("Skipping step due to error", step_id=step.id)
                    state.set_step_status(step.id, StepStatus.SKIPPED)
                elif step.if_error == "retry":
                    # TODO: Implement retry logic
                    self.logger.warning(
                        "Retry policy not yet implemented", step_id=step.id
                    )
                    raise
                else:
                    # Default to fail
                    raise

        result = {
            "run_id": run_id,
            "status": "completed",
            "run_dir": str(run_dir),
            "state": state.state,
            "step_results": state.step_results,
        }

        self.logger.info("Workflow execution completed", run_id=run_id)
        return result

    def _execute_step(self, step: StepConfig, state: WorkflowState) -> None:
        """Execute a single step."""
        self.logger.info("Executing step", step_id=step.id, uses=step.uses)

        # Set step status to running
        state.set_step_status(step.id, StepStatus.RUNNING)

        # Get tool using the proper registry
        tool = tool_registry.get_tool(step.uses)
        if not tool:
            raise ValueError(f"Tool not found: {step.uses}")

        # Create tool context
        context = ToolContext(
            state=state,
            run_dir=str(state.run_dir),
            env=state.env,
        )

        # Execute tool
        def _execute() -> StepResultDict:
            return tool.execute(context, step)

        # Execute with retry if configured
        if step.retry:
            result = self._execute_with_retry(step, state, _execute)
        else:
            result = _execute()

        # Update state with results
        state.update_from_tool_result(step.id, result)
        state.set_step_status(step.id, StepStatus.COMPLETED)

        self.logger.info(
            "Step completed",
            step_id=step.id,
            result_keys=list(result.keys()),
        )

    def _execute_with_retry(
        self,
        step: StepConfig,
        state: WorkflowState,
        execute_func: Callable | None = None,
    ) -> StepResultDict:
        """Execute a step with retry logic."""
        if not step.retry:
            raise ValueError("No retry configuration provided")

        retry_config = step.retry

        @retry(
            stop=stop_after_attempt(retry_config.max_attempts),
            wait=wait_exponential(
                multiplier=retry_config.backoff_factor,
                max=retry_config.max_delay,
            ),
        )
        def _retry_execute() -> StepResultDict:
            if execute_func:
                return execute_func()
            else:
                # Re-execute the step
                self._execute_step(step, state)
                return state.step_results[step.id]

        return _retry_execute()

    def _dry_run(self, petal_file: PetalFile, state: WorkflowState) -> dict[str, Any]:
        """Perform a dry run of the workflow."""
        self.logger.info("Performing dry run", name=petal_file.name)

        dry_run_results = {
            "run_id": state.run_id,
            "status": "dry_run",
            "run_dir": str(state.run_dir),
            "steps": [],
        }

        for step in petal_file.steps:
            step_info = {
                "id": step.id,
                "uses": step.uses,
                "reads": step.reads,
                "writes": step.writes,
                "when": step.when,
                "if_error": step.if_error,
                "retry": step.retry.model_dump() if step.retry else None,
                "with": step.with_,
            }
            dry_run_results["steps"].append(step_info)

        self.logger.info("Dry run completed", steps_count=len(petal_file.steps))
        return dry_run_results
