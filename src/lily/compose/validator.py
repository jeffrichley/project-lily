"""Composition validation for Petal workflows."""

from lily.petal.models import Petal


class CompositionValidator:
    """Validates composed Petal workflows."""

    def __init__(self) -> None:
        """Initialize the composition validator."""
        # Lazy import to avoid circular dependencies
        from lily.petal.validator import PetalValidator

        self.petal_validator = PetalValidator()

    def validate_composition(self, petal: Petal, cfg: dict) -> tuple[bool, list[str]]:
        """Validate the composition of Petal workflow with config."""
        errors = []

        # Validate the Petal workflow itself
        is_valid, petal_errors = self.petal_validator.validate(petal)
        if not is_valid:
            errors.extend(petal_errors)

        # Validate configuration structure
        config_errors = self._validate_config(cfg)
        errors.extend(config_errors)

        # Validate merged configuration
        merged_errors = self._validate_merged_config(petal, cfg)
        errors.extend(merged_errors)

        return len(errors) == 0, errors

    def _validate_config(self, cfg: dict) -> list[str]:
        """Validate configuration structure."""
        errors = []

        try:
            # Validate environment variables if present
            if "env" in cfg and cfg["env"] is not None:
                env = cfg["env"]
                if not isinstance(env, dict):
                    errors.append("Environment variables must be a dictionary")

            # Validate parameters if present
            if "params" in cfg and cfg["params"] is not None:
                params = cfg["params"]
                if not isinstance(params, dict):
                    errors.append("Parameters must be a dictionary")

            # Validate variables if present
            if "vars" in cfg and cfg["vars"] is not None:
                vars_config = cfg["vars"]
                if not isinstance(vars_config, dict):
                    errors.append("Variables must be a dictionary")

        except Exception as e:
            errors.append(f"Error validating config: {e}")

        return errors

    def _validate_merged_config(self, petal: Petal, cfg: dict) -> list[str]:
        """Validate the merged configuration."""
        errors = []

        try:
            # Check for environment variable conflicts
            if "env" in cfg and cfg["env"] is not None:
                config_env = cfg["env"]
                if isinstance(config_env, dict):
                    for env_name, env_value in config_env.items():
                        if env_name in petal.env:
                            # Check if there's a value conflict
                            petal_env_value = petal.env[env_name]
                            if petal_env_value != env_value:
                                errors.append(
                                    f"Environment variable conflict for '{env_name}': "
                                    f"Petal has '{petal_env_value}', config has '{env_value}'"
                                )

            # Check for variable conflicts
            if "vars" in cfg and cfg["vars"] is not None:
                config_vars = cfg["vars"]
                if isinstance(config_vars, dict):
                    for var_name, var_value in config_vars.items():
                        if var_name in petal.vars:
                            # Check if there's a value conflict
                            petal_var_value = petal.vars[var_name]
                            if petal_var_value != var_value:
                                errors.append(
                                    f"Variable conflict for '{var_name}': "
                                    f"Petal has '{petal_var_value}', config has '{var_value}'"
                                )

        except Exception as e:
            errors.append(f"Error validating merged config: {e}")

        return errors
