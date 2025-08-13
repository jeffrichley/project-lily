"""Expression language parser for Petal DSL if: conditions."""

import ast
import re
from collections.abc import Callable


class ExpressionError(Exception):
    """Custom exception for expression parsing errors."""

    pass


class ExpressionParser:
    """Parser for Petal DSL conditional expressions."""

    # Supported operators
    OPERATORS = {
        "&&": "and",
        "||": "or",
        "!": "not",
        "==": "==",
        "!=": "!=",
        "<": "<",
        "<=": "<=",
        ">": ">",
        ">=": ">=",
        "in": "in",
    }

    # Supported identifier namespaces
    NAMESPACES = {"params", "vars", "outputs", "env"}

    def __init__(self) -> None:
        """Initialize the expression parser."""
        self._compiled_expressions: dict[str, ast.Expression] = {}

    def parse(self, expression: str) -> ast.Expression:
        """Parse an expression string into an AST."""
        if not expression or not expression.strip():
            raise ExpressionError("Expression cannot be empty")

        # Normalize whitespace
        expression = " ".join(expression.split())

        # Check if already compiled
        if expression in self._compiled_expressions:
            return self._compiled_expressions[expression]

        try:
            # Convert Petal operators to Python operators
            python_expr = self._convert_operators(expression)

            # Parse with Python AST
            tree = ast.parse(python_expr, mode="eval")

            # Validate the AST
            self._validate_ast(tree)

            # Cache the compiled expression
            self._compiled_expressions[expression] = tree

            return tree

        except SyntaxError as e:
            raise ExpressionError(f"Syntax error in expression: {e}") from e
        except Exception as e:
            raise ExpressionError(f"Failed to parse expression: {e}") from e

    def _convert_operators(self, expression: str) -> str:
        """Convert Petal operators to Python operators."""
        # Replace Petal operators with Python equivalents
        for petal_op, python_op in self.OPERATORS.items():
            # Use word boundaries to avoid partial matches
            if petal_op in ["&&", "||"]:
                expression = re.sub(
                    rf"\b{re.escape(petal_op)}\b", python_op, expression
                )
            else:
                expression = expression.replace(petal_op, python_op)

        return expression

    def _validate_ast(self, tree: ast.Expression) -> None:
        """Validate that the AST only contains allowed operations."""
        for node in ast.walk(tree):
            self._validate_node(node)

    def _validate_node(self, node: ast.AST) -> None:
        """Validate a single AST node."""
        if self._is_allowed_literal(node) or self._is_allowed_context(node):
            return

        validator = self._get_node_validator(node)
        if validator:
            validator(node)
        else:
            raise ExpressionError(f"Unsupported operation: {type(node).__name__}")

    def _get_node_validator(self, node: ast.AST) -> Callable[[ast.AST], None] | None:
        """Get the appropriate validator for a node type."""
        # Type ignore needed because mypy can't verify that the method signatures
        # match the expected callable type for the dict values, but we know
        # they all take the same signature: (self, node: ast.AST) -> None
        validators: dict[type[ast.AST], Callable[[ast.AST], None]] = {
            ast.Name: self._validate_identifier,  # type: ignore[dict-item]
            ast.Attribute: self._validate_attribute,  # type: ignore[dict-item]
            ast.Subscript: self._validate_subscript,  # type: ignore[dict-item]
            ast.Compare: self._validate_compare,  # type: ignore[dict-item]
            ast.BoolOp: self._validate_bool_op,  # type: ignore[dict-item]
            ast.UnaryOp: self._validate_unary_op,  # type: ignore[dict-item]
            ast.BinOp: self._validate_bin_op,  # type: ignore[dict-item]
        }

        if isinstance(node, ast.Call):
            raise ExpressionError("Function calls are not allowed in expressions")

        return validators.get(type(node))

    def _is_allowed_literal(self, node: ast.AST) -> bool:
        """Check if node is an allowed literal type."""
        return isinstance(node, ast.Constant | ast.List | ast.Dict | ast.Tuple)

    def _is_allowed_context(self, node: ast.AST) -> bool:
        """Check if node is an allowed context type."""
        return isinstance(
            node,
            ast.Expression
            | ast.Load
            | ast.Eq
            | ast.NotEq
            | ast.Lt
            | ast.LtE
            | ast.Gt
            | ast.GtE
            | ast.In
            | ast.NotIn
            | ast.And
            | ast.Or
            | ast.Not,
        )

    def _validate_identifier(self, node: ast.Name) -> None:
        """Validate identifier names."""
        # Check if it's a namespace reference
        if "." in node.id:
            namespace = node.id.split(".")[0]
            if namespace not in self.NAMESPACES:
                raise ExpressionError(f"Invalid namespace: {namespace}")
        # Simple identifiers are allowed (for local variables)

    def _validate_attribute(self, node: ast.Attribute) -> None:
        """Validate attribute access."""
        if isinstance(node.value, ast.Name):
            if node.value.id not in self.NAMESPACES:
                raise ExpressionError(f"Invalid namespace: {node.value.id}")
        else:
            # Allow chained attribute access on valid namespaces
            self._validate_ast(ast.Expression(body=node.value))

    def _validate_subscript(self, node: ast.Subscript) -> None:
        """Validate subscript operations."""
        # Allow dictionary/list access on valid namespaces
        self._validate_ast(ast.Expression(body=node.value))
        self._validate_ast(ast.Expression(body=node.slice))

    def _validate_compare(self, node: ast.Compare) -> None:
        """Validate comparison operations."""
        # Validate left operand
        self._validate_ast(ast.Expression(body=node.left))

        # Validate comparators and operators
        for op, comparator in zip(node.ops, node.comparators, strict=False):
            if not isinstance(
                op,
                ast.Eq
                | ast.NotEq
                | ast.Lt
                | ast.LtE
                | ast.Gt
                | ast.GtE
                | ast.In
                | ast.NotIn,
            ):
                raise ExpressionError(
                    f"Unsupported comparison operator: {type(op).__name__}"
                )
            self._validate_ast(ast.Expression(body=comparator))

    def _validate_bool_op(self, node: ast.BoolOp) -> None:
        """Validate boolean operations."""
        if not isinstance(node.op, ast.And | ast.Or):
            raise ExpressionError(
                f"Unsupported boolean operator: {type(node.op).__name__}"
            )

        for value in node.values:
            self._validate_ast(ast.Expression(body=value))

    def _validate_unary_op(self, node: ast.UnaryOp) -> None:
        """Validate unary operations."""
        if not isinstance(node.op, ast.Not):
            raise ExpressionError(
                f"Unsupported unary operator: {type(node.op).__name__}"
            )

        self._validate_ast(ast.Expression(body=node.operand))

    def _validate_bin_op(self, node: ast.BinOp) -> None:
        """Validate binary operations."""
        # Only allow basic arithmetic and string operations
        allowed_ops = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow)
        if not isinstance(node.op, allowed_ops):
            raise ExpressionError(
                f"Unsupported binary operator: {type(node.op).__name__}"
            )

        self._validate_ast(ast.Expression(body=node.left))
        self._validate_ast(ast.Expression(body=node.right))


class ExpressionEvaluator:
    """Evaluator for compiled Petal expressions."""

    def __init__(self) -> None:
        """Initialize the expression evaluator."""
        self.parser = ExpressionParser()

    def evaluate(
        self, expression: str, context: dict[str, str | int | float | bool | None]
    ) -> bool:
        """Evaluate an expression in the given context."""
        try:
            # Parse the expression
            tree = self.parser.parse(expression)

            # Create a safe evaluation environment
            eval_globals = {
                "__builtins__": {
                    "True": True,
                    "False": False,
                    "None": None,
                    "len": len,
                    "str": str,
                    "int": int,
                    "float": float,
                    "bool": bool,
                    "list": list,
                    "dict": dict,
                    "tuple": tuple,
                }
            }

            # Add context variables to globals
            # Type ignore needed because mypy can't verify that the context dict structure
            # is compatible with eval_globals, but this is safe at runtime since Python
            # dictionaries can be merged regardless of their content
            # The context dict contains str|int|float|bool|None values which are all
            # valid Python objects that can be safely added to the globals dict
            eval_globals.update(context)  # type: ignore[arg-type]

            # Evaluate the expression
            result = eval(compile(tree, "<string>", "eval"), eval_globals)

            # Ensure result is boolean
            return bool(result)

        except Exception as e:
            raise ExpressionError(f"Failed to evaluate expression: {e}") from e

    def validate(self, expression: str) -> tuple[bool, str | None]:
        """Validate an expression without evaluating it."""
        try:
            self.parser.parse(expression)
            return True, None
        except ExpressionError as e:
            return False, str(e)

    def get_identifiers(self, expression: str) -> set[str]:
        """Extract all identifiers from an expression."""
        try:
            tree = self.parser.parse(expression)
            identifiers = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    identifiers.add(node.id)
                elif isinstance(node, ast.Attribute) and isinstance(
                    node.value, ast.Name
                ):
                    # Handle attribute access like params.foo
                    identifiers.add(f"{node.value.id}.{node.attr}")

            return identifiers
        except ExpressionError:
            return set()

    def compile_expression(self, expression: str) -> ast.Expression:
        """Compile an expression for later evaluation."""
        return self.parser.parse(expression)
