"""Comprehensive validator for Petal DSL workflows."""

import re

from lily.petal.models import Petal, StepBase
from lily.petal.parser import PetalParser


class PetalValidationError(Exception):
    """Custom exception for Petal validation errors."""

    pass


class PetalValidator:
    """Comprehensive validator for Petal workflows."""

    def __init__(self) -> None:
        """Initialize the Petal validator."""
        self.parser = PetalParser()

    def validate(self, petal: Petal) -> tuple[bool, list[str]]:
        """Perform comprehensive validation of a Petal workflow."""
        errors = []

        # Basic structure validation (already done by Pydantic)
        # Schema validation (already done by Pydantic)

        # DAG validation
        dag_errors = self._validate_dag(petal)
        errors.extend(dag_errors)

        # Input/Output validation
        io_errors = self._validate_inputs_outputs(petal)
        errors.extend(io_errors)

        # Type validation
        type_errors = self._validate_types(petal)
        errors.extend(type_errors)

        # Resource validation
        resource_errors = self._validate_resources(petal)
        errors.extend(resource_errors)

        # Cache validation
        cache_errors = self._validate_cache(petal)
        errors.extend(cache_errors)

        # Adapter validation
        adapter_errors = self._validate_adapters(petal)
        errors.extend(adapter_errors)

        return len(errors) == 0, errors

    def _validate_dag(self, petal: Petal) -> list[str]:
        """Validate DAG structure and dependencies."""
        errors = []

        # Build step lookup
        step_lookup = {step.id: step for step in petal.steps}

        # Check for missing dependencies
        missing_deps = [
            f"Step '{step.id}' depends on missing step '{needed_step}'"
            for step in petal.steps
            for needed_step in step.needs
            if needed_step not in step_lookup
        ]
        errors.extend(missing_deps)

        # Check for cycles
        cycle_errors = self._detect_cycles(petal.steps, step_lookup)
        errors.extend(cycle_errors)

        return errors

    def _detect_cycles(
        self, steps: list[StepBase], step_lookup: dict[str, StepBase]
    ) -> list[str]:
        """Detect cycles in the DAG using DFS."""
        errors = []
        visited = set()
        rec_stack = set()

        def dfs(step_id: str, path: list[str]) -> None:
            if step_id in rec_stack:
                cycle_path = path[path.index(step_id) :] + [step_id]
                errors.append(f"Cycle detected: {' -> '.join(cycle_path)}")
                return

            if step_id in visited:
                return

            visited.add(step_id)
            rec_stack.add(step_id)

            if step_id in step_lookup:
                step = step_lookup[step_id]
                for needed_step in step.needs:
                    dfs(needed_step, path + [step_id])

            rec_stack.remove(step_id)

        # Start DFS from each step
        for step in steps:
            if step.id not in visited:
                dfs(step.id, [])

        return errors

    def _validate_inputs_outputs(self, petal: Petal) -> list[str]:
        """Validate input/output declarations and dependencies."""
        errors = []

        # Build output producers map
        output_producers: dict[str, str] = {}
        for step in petal.steps:
            for output_name in step.outputs:
                if output_name in output_producers:
                    errors.append(
                        f"Output '{output_name}' is produced by multiple steps: {output_producers[output_name]} and {step.id}"
                    )
                else:
                    output_producers[output_name] = step.id

        # Check input dependencies
        for step in petal.steps:
            for input_name, input_decl in step.inputs.items():
                if input_decl.from_ and input_decl.from_.startswith("outputs."):
                    # Parse the 'from' expression to find dependencies
                    output_name = input_decl.from_.split(".", 1)[1]
                    if output_name not in output_producers:
                        errors.append(
                            f"Step '{step.id}' input '{input_name}' references undefined output '{output_name}'"
                        )
                    else:
                        producer_step = output_producers[output_name]
                        if producer_step not in step.needs:
                            errors.append(
                                f"Step '{step.id}' uses output '{output_name}' from '{producer_step}' but doesn't declare dependency"
                            )

        return errors

    def _validate_types(self, petal: Petal) -> list[str]:
        """Validate type declarations and consistency."""
        errors = []

        for step in petal.steps:
            # Validate input types
            for input_name, input_decl in step.inputs.items():
                if input_decl.type is None:
                    errors.append(
                        f"Step '{step.id}' input '{input_name}' must declare a type"
                    )

            # Validate output types
            for output_name, output_decl in step.outputs.items():
                if output_decl.type is None:
                    errors.append(
                        f"Step '{step.id}' output '{output_name}' must declare a type"
                    )

        return errors

    def _validate_resources(self, petal: Petal) -> list[str]:
        """Validate resource declarations."""
        errors = []

        for step in petal.steps:
            if step.resources:
                errors.extend(self._validate_step_resources(step))

        return errors

    def _validate_step_resources(self, step: StepBase) -> list[str]:
        """Validate resources for a single step."""
        errors: list[str] = []

        if step.resources is None:
            return errors

        if "cpu" in step.resources:
            errors.extend(self._validate_cpu_resource(step))

        if "mem" in step.resources:
            errors.extend(self._validate_memory_resource(step))

        if "gpu" in step.resources:
            errors.extend(self._validate_gpu_resource(step))

        if "network" in step.resources:
            errors.extend(self._validate_network_resource(step))

        return errors

    def _validate_cpu_resource(self, step: StepBase) -> list[str]:
        """Validate CPU resource specification."""
        errors: list[str] = []
        if step.resources is None:
            return errors

        cpu = step.resources["cpu"]

        if isinstance(cpu, str):
            if not cpu.replace(".", "").isdigit():
                errors.append(f"Step '{step.id}' CPU must be a number, got '{cpu}'")
        elif isinstance(cpu, bool):
            errors.append(f"Step '{step.id}' CPU must be a number, got boolean")

        return errors

    def _validate_memory_resource(self, step: StepBase) -> list[str]:
        """Validate memory resource specification."""
        errors: list[str] = []
        if step.resources is None:
            return errors

        mem = step.resources["mem"]

        if isinstance(mem, str):
            # Check for valid memory format (e.g., "1G", "512M", "2Gi")
            if not re.match(r"^\d+[KMGT]i?$", mem):
                errors.append(
                    f"Step '{step.id}' memory must be in format like '1G', '512M', got '{mem}'"
                )
        elif isinstance(mem, int | float | bool):
            errors.append(
                f"Step '{step.id}' memory must be a string, got {type(mem).__name__}"
            )

        return errors

    def _validate_gpu_resource(self, step: StepBase) -> list[str]:
        """Validate GPU resource specification."""
        errors: list[str] = []
        if step.resources is None:
            return errors

        gpu = step.resources["gpu"]

        if not isinstance(gpu, int) or gpu < 0:
            errors.append(
                f"Step '{step.id}' GPU must be a non-negative integer, got {gpu}"
            )

        return errors

    def _validate_network_resource(self, step: StepBase) -> list[str]:
        """Validate network resource specification."""
        errors: list[str] = []
        if step.resources is None:
            return errors

        network = step.resources["network"]

        if not isinstance(network, bool):
            errors.append(
                f"Step '{step.id}' network must be a boolean, got {type(network)}"
            )

        return errors

    def _validate_cache(self, petal: Petal) -> list[str]:
        """Validate cache configurations."""
        errors = []

        for step in petal.steps:
            if step.cache is not None:
                # Validate cache policy
                if "policy" in step.cache:
                    policy = step.cache["policy"]
                    valid_policies = {"auto", "never", "read-only", "write-only"}
                    if policy not in valid_policies:
                        errors.append(
                            f"Step '{step.id}' cache policy must be one of {valid_policies}, got '{policy}'"
                        )

                # Validate cache key if provided
                if "key" in step.cache:
                    # Key is already typed as string in CacheDict, so no validation needed
                    pass

        return errors

    def _validate_adapters(self, petal: Petal) -> list[str]:
        """Validate adapter configurations."""
        errors = []

        # Define valid adapters for each step type
        valid_adapters = {
            "shell": {"process", "docker"},
            "python": {"process", "docker", "python"},
            "llm": {"http"},
            "tool": {"process", "docker", "python", "http"},
            "human": set(),
            "foreach": set(),
            "include": set(),
        }

        for step in petal.steps:
            if not step.adapter:
                continue

            step_type = step.uses
            if step_type not in valid_adapters:
                continue

            allowed_adapters = valid_adapters[step_type]

            if step_type in ["human", "foreach", "include"]:
                if step.adapter is not None:
                    errors.append(
                        f"Step '{step.id}' {step_type} step cannot use adapters"
                    )
            elif step.adapter not in allowed_adapters:
                errors.append(
                    f"Step '{step.id}' {step_type} step can only use {list(allowed_adapters)} adapters, got '{step.adapter}'"
                )

        return errors

    def validate_file(self, file_path: str) -> tuple[bool, list[str]]:
        """Validate a Petal file."""
        try:
            petal = self.parser.parse_file(file_path)
            return self.validate(petal)
        except Exception as e:
            return False, [str(e)]

    def get_validation_summary(
        self, petal: Petal
    ) -> dict[str, bool | int | list[str] | dict[str, list[str]]]:
        """Get a summary of validation information."""
        is_valid, errors = self.validate(petal)

        # Build step dependency graph
        dependencies = {step.id: step.needs for step in petal.steps}

        # Count outputs
        output_count = sum(len(step.outputs) for step in petal.steps)

        # Count inputs
        input_count = sum(len(step.inputs) for step in petal.steps)

        # Count conditional steps
        conditional_count = sum(1 for step in petal.steps if step.if_)

        return {
            "is_valid": is_valid,
            "error_count": len(errors),
            "errors": errors,
            "step_count": len(petal.steps),
            "output_count": output_count,
            "input_count": input_count,
            "conditional_count": conditional_count,
            "dependencies": dependencies,
        }
