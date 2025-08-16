"""Python evaluation tool for Petal workflow system."""

from typing import Any, TypedDict

from lily.petal.executor.tools import ToolContext
from lily.petal.executor.types import StepResultDict
from lily.petal.models_strict import PythonEvalStepConfig


class PythonEvalSuccess(TypedDict):
    """Successful Python evaluation result."""

    result: Any
    expression: str


class PythonEvalError(TypedDict):
    """Failed Python evaluation result."""

    error: str
    expression: str


PythonEvalResult = PythonEvalSuccess | PythonEvalError


class PythonEvalTool:
    """Tool for evaluating Python expressions safely."""

    @property
    def name(self) -> str:
        """Get the tool name."""
        return "python.eval"

    @property
    def step_config_class(self) -> type[PythonEvalStepConfig]:
        """Get the step config class for this tool."""
        return PythonEvalStepConfig

    def get_description(self) -> str:
        """Get a description of what this tool does."""
        return "Tool for evaluating Python expressions safely."

    def validate(self, step: PythonEvalStepConfig) -> bool:
        """Validate that the step configuration is correct for this tool."""
        return step.uses == self.name

    def execute(
        self, context: ToolContext, step: PythonEvalStepConfig
    ) -> StepResultDict:
        """Execute Python evaluation step."""
        # Extract step configuration
        expression = step.expression
        globals_dict = step.globals

        # Create safe evaluation environment with workflow state
        safe_globals = {
            "__builtins__": {
                name: getattr(__builtins__, name)
                for name in [
                    "abs",
                    "all",
                    "any",
                    "bin",
                    "bool",
                    "chr",
                    "dict",
                    "dir",
                    "divmod",
                    "enumerate",
                    "filter",
                    "float",
                    "format",
                    "frozenset",
                    "getattr",
                    "hasattr",
                    "hash",
                    "hex",
                    "id",
                    "int",
                    "isinstance",
                    "issubclass",
                    "iter",
                    "len",
                    "list",
                    "map",
                    "max",
                    "min",
                    "next",
                    "oct",
                    "ord",
                    "pow",
                    "print",
                    "range",
                    "repr",
                    "reversed",
                    "round",
                    "set",
                    "slice",
                    "sorted",
                    "str",
                    "sum",
                    "tuple",
                    "type",
                    "vars",
                    "zip",
                ]
                if hasattr(__builtins__, name)
            }
        }
        safe_globals.update(globals_dict or {})

        # Add workflow state to globals for context access
        safe_globals.update(context.state.state)

        try:
            # Evaluate expression safely
            result = eval(expression, safe_globals, {})
            return {
                "result": result,
                "expression": expression,
            }
        except Exception as e:
            return {
                "error": str(e),
                "expression": expression,
            }
