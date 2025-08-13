"""Pytest configuration and plugins for Lily CLI."""

import inspect
import json
import os

import pytest

# Cache to track file modification times and processed functions
_file_cache: dict[str, tuple[float, set]] = {}

# Cache file path - stored in pytest cache directory
_cache_file = None


def _get_cache_file() -> str:
    """Get the cache file path, creating it if needed."""
    global _cache_file
    if _cache_file is None:
        # Use pytest's cache directory for consistency
        cache_dir = os.path.join(os.getcwd(), ".pytest_cache")
        os.makedirs(cache_dir, exist_ok=True)
        _cache_file = os.path.join(cache_dir, "auto_fix_cache.json")
    return _cache_file


def _load_cache() -> None:
    """Load cache from disk if it exists."""
    global _file_cache
    cache_file = _get_cache_file()

    if os.path.exists(cache_file):
        try:
            with open(cache_file) as f:
                data = json.load(f)
                # Convert lists back to sets for O(1) lookups
                _file_cache = {
                    file_path: (mtime, set(funcs))
                    for file_path, (mtime, funcs) in data.items()
                }
        except (json.JSONDecodeError, OSError):
            # If cache is corrupted, start fresh
            _file_cache = {}


def _save_cache() -> None:
    """Save cache to disk."""
    cache_file = _get_cache_file()

    try:
        # Convert sets to lists for JSON serialization
        data = {
            file_path: (mtime, list(funcs))
            for file_path, (mtime, funcs) in _file_cache.items()
        }

        with open(cache_file, "w") as f:
            json.dump(data, f)
    except OSError:
        # If we can't save, just continue without caching
        pass


def pytest_configure(config: pytest.Config) -> None:
    """Load cache when pytest starts."""
    _load_cache()


def pytest_runtest_setup(item: pytest.Item) -> None:
    """Enforce that all test functions have at least one marker, proper AAA structure, and return type.

    This plugin runs right before each test executes and fails individual tests
    that don't have markers, proper Arrange-Act-Assert structure, or correct return type.
    This provides "test failed" messages for better developer experience.
    """
    try:
        # Skip non-function items (like classes, modules)
        if not hasattr(item, "function") or not getattr(item, "function", None):  # type: ignore[misc]
            return

        # Check if the test function has any markers
        markers = list(item.iter_markers())

        if not markers:
            pytest.fail(
                f"Test '{item.name}' must have at least one marker. "
                f"Add a marker like @pytest.mark.unit, @pytest.mark.integration, etc. "
                f"See pytest.ini for valid markers."
            )

        # Check for proper AAA structure
        source_lines = inspect.getsource(item.function).split("\n")
        _check_aaa_structure(item, source_lines)

        # Check for proper return type and auto-fix if needed
        _check_and_fix_return_type(item, source_lines)

    except Exception:
        # If there's any error, just skip the check to avoid breaking tests
        pass


def _check_aaa_structure(item: pytest.Item, source_lines: list[str]) -> None:
    """Check that test function has proper Arrange-Act-Assert structure."""
    arrange_found = False
    act_found = False
    assert_found = False

    for source_line in source_lines:
        line = source_line.strip()

        # Only check comment lines
        if not line.startswith("#"):
            continue

        # Check if any of the AAA words are in this comment line
        if "Arrange" in line:
            arrange_found = True
            if not _has_descriptive_comment(line):
                pytest.fail(
                    f"Test '{item.name}' has 'Arrange' but missing descriptive comment. "
                    f"Use format: '# Arrange - description of what is being set up'"
                )

        if "Act" in line:
            act_found = True
            if not _has_descriptive_comment(line):
                pytest.fail(
                    f"Test '{item.name}' has 'Act' but missing descriptive comment. "
                    f"Use format: '# Act - description of what action is being performed'"
                )

        if "Assert" in line:
            assert_found = True
            if not _has_descriptive_comment(line):
                pytest.fail(
                    f"Test '{item.name}' has 'Assert' but missing descriptive comment. "
                    f"Use format: '# Assert - description of what is being verified'"
                )

    _check_missing_sections(item, arrange_found, act_found, assert_found)


def _check_missing_sections(
    item: pytest.Item, arrange_found: bool, act_found: bool, assert_found: bool
) -> None:
    """Check for missing AAA sections and fail with appropriate messages."""
    if not arrange_found:
        pytest.fail(
            f"Test '{item.name}' is missing 'Arrange' section. "
            f"Add '# Arrange - description' comment before test setup."
        )

    if not act_found:
        pytest.fail(
            f"Test '{item.name}' is missing 'Act' section. "
            f"Add '# Act - description' comment before test action."
        )

    if not assert_found:
        pytest.fail(
            f"Test '{item.name}' is missing 'Assert' section. "
            f"Add '# Assert - description' comment before test verification."
        )


def _check_and_fix_return_type(item: pytest.Item, source_lines: list[str]) -> None:
    """Check that test function has proper return type annotation and auto-fix if needed."""
    # Check cache first
    if _is_cached_and_valid(item):
        return

    # Look for the function definition line
    for i, line in enumerate(source_lines):
        line = line.strip()
        if line.startswith("def ") and item.name in line:
            # Check if it has a return type annotation
            if "->" not in line:
                # Auto-fix: add return type annotation
                _auto_fix_return_type(item, source_lines, i)
                return
            elif "-> None" not in line:
                pytest.fail(
                    f"Test '{item.name}' should return 'None', not '{line.split('->')[1].split(':')[0].strip()}'. "
                    f"Change to '-> None' in the function definition."
                )
            break


def _is_cached_and_valid(item: pytest.Item) -> bool:
    """Check if the file is cached and hasn't been modified since last check."""
    file_path = item.module.__file__
    if not file_path:
        return False

    try:
        current_mtime = os.path.getmtime(file_path)

        if file_path in _file_cache:
            cached_mtime, processed_functions = _file_cache[file_path]

            # If file hasn't been modified and function was already processed
            if current_mtime <= cached_mtime and item.name in processed_functions:
                return True

        # Cache miss - update cache
        if file_path not in _file_cache:
            _file_cache[file_path] = (current_mtime, set())

        _file_cache[file_path][1].add(item.name)
        return False

    except (OSError, AttributeError):
        # If we can't get file info, don't cache
        return False


def _auto_fix_return_type(
    item: pytest.Item, source_lines: list[str], func_line_index: int
) -> None:
    """Automatically add return type annotation to test function."""
    try:
        # Use a simpler approach: modify the specific line directly
        with open(item.module.__file__) as f:
            lines = f.readlines()

        # Find the function definition line
        for i, line in enumerate(lines):
            if (
                line.strip().startswith("def ")
                and item.name in line
                and "->" not in line
            ):
                # Add return type annotation to this line
                if line.rstrip().endswith(":"):
                    # Remove the colon, add return type, then add colon back
                    new_line = line.rstrip()[:-1] + " -> None:\n"
                else:
                    # Add return type before the colon
                    new_line = line.rstrip() + " -> None:\n"

                lines[i] = new_line

                # Write the modified file back
                with open(item.module.__file__, "w") as f:
                    f.writelines(lines)

                # Update cache with new modification time
                if item.module.__file__:
                    _file_cache[item.module.__file__] = (
                        os.path.getmtime(item.module.__file__),
                        {item.name},
                    )

                # Re-import the module to pick up changes
                import importlib

                importlib.reload(item.module)

                return

        # If we get here, we couldn't find the function to fix
        pytest.fail(
            f"Test '{item.name}' is missing return type annotation. "
            f"Add '-> None' to the function definition: 'def {item.name}() -> None:'"
        )

    except Exception:
        # If auto-fix fails, fall back to manual fix
        pytest.fail(
            f"Test '{item.name}' is missing return type annotation. "
            f"Add '-> None' to the function definition: 'def {item.name}() -> None:'"
        )


def _has_descriptive_comment(line: str) -> bool:
    """Check if a comment line has a descriptive dash and text."""
    # Remove the comment marker and check for dash and text
    comment_part = line.lstrip("#").strip()

    # Must have a dash followed by text
    return " - " in comment_part and len(comment_part.split(" - ")[1].strip()) > 0


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Save cache to disk."""
    _save_cache()
