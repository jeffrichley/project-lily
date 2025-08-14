"""Configuration merging logic for Petal workflows."""

from lily.petal.models import Petal


class ConfigurationMerger:
    """Merges configuration with Petal workflows."""

    def merge_config_to_petal(self, petal: Petal, cfg: dict) -> Petal:
        """Merge configuration into Petal workflow.

        Args:
            petal: Petal workflow to merge into
            cfg: Configuration dictionary to merge from

        Returns:
            Merged Petal workflow
        """
        # Merge environment variables
        if "env" in cfg and cfg["env"] is not None:
            petal.env.update(cfg["env"])

        # Merge parameters (update parameter defaults, not replace Param objects)
        if "params" in cfg and cfg["params"] is not None:
            config_params = cfg["params"]

            for key, value in config_params.items():
                if key in petal.params:
                    # Update the default value of the existing Param object
                    petal.params[key].default = value
                else:
                    # Create a new Param object if it doesn't exist
                    from lily.petal.models import Param

                    # Determine the appropriate type based on the value
                    if isinstance(value, bool):
                        param_type = "bool"
                    elif isinstance(value, int):
                        param_type = "int"
                    elif isinstance(value, float):
                        param_type = "float"
                    else:
                        param_type = "str"

                    petal.params[key] = Param(
                        type=param_type,
                        required=False,
                        default=value,
                        help=f"Override from config: {key}",
                    )

        # Merge variables
        if "vars" in cfg and cfg["vars"] is not None:
            petal.vars.update(cfg["vars"])

        # Apply database configuration
        if "db" in cfg and cfg["db"] is not None:
            petal.env.update(cfg["db"])

        # Apply profile configuration
        if "profiles" in cfg and cfg["profiles"] is not None:
            profile_config = cfg["profiles"]
            if isinstance(profile_config, dict):
                petal.env.update(profile_config.get("env", {}))

                # Merge profile parameters
                profile_params = profile_config.get("params", {})
                for key, value in profile_params.items():
                    if key in petal.params:
                        # Update existing parameter
                        petal.params[key].default = value
                    else:
                        # Create new parameter
                        from lily.petal.models import Param

                        if isinstance(value, bool):
                            param_type = "bool"
                        elif isinstance(value, int):
                            param_type = "int"
                        elif isinstance(value, float):
                            param_type = "float"
                        else:
                            param_type = "str"

                        petal.params[key] = Param(
                            type=param_type,
                            required=False,
                            default=value,
                            help=f"From profile config: {key}",
                        )

        # Apply workflow configuration
        if "workflows" in cfg and cfg["workflows"] is not None:
            workflow_config = cfg["workflows"]
            if isinstance(workflow_config, dict):
                petal.env.update(workflow_config.get("env", {}))
                petal.vars.update(workflow_config.get("vars", {}))

                # Merge workflow parameters
                workflow_params = workflow_config.get("params", {})
                for key, value in workflow_params.items():
                    if key in petal.params:
                        # Update existing parameter
                        petal.params[key].default = value
                    else:
                        # Create new parameter
                        from lily.petal.models import Param

                        if isinstance(value, bool):
                            param_type = "bool"
                        elif isinstance(value, int):
                            param_type = "int"
                        elif isinstance(value, float):
                            param_type = "float"
                        else:
                            param_type = "str"

                        petal.params[key] = Param(
                            type=param_type,
                            required=False,
                            default=value,
                            help=f"From workflow config: {key}",
                        )

        # Apply adapter configuration
        if "adapters" in cfg and cfg["adapters"] is not None:
            adapter_config = cfg["adapters"]
            if isinstance(adapter_config, dict):
                petal.env.update(adapter_config.get("env", {}))

                # Merge adapter parameters
                adapter_params = adapter_config.get("params", {})
                for key, value in adapter_params.items():
                    if key in petal.params:
                        # Update existing parameter
                        petal.params[key].default = value
                    else:
                        # Create new parameter
                        from lily.petal.models import Param

                        if isinstance(value, bool):
                            param_type = "bool"
                        elif isinstance(value, int):
                            param_type = "int"
                        elif isinstance(value, float):
                            param_type = "float"
                        else:
                            param_type = "str"

                        petal.params[key] = Param(
                            type=param_type,
                            required=False,
                            default=value,
                            help=f"From adapter config: {key}",
                        )

        return petal

    def merge_petal_to_config(self, cfg: dict, petal: Petal) -> dict:
        """Merge Petal workflow configuration into config dictionary."""
        # Create a copy of the config
        merged_config = cfg.copy()

        # Merge Petal environment variables
        if "env" not in merged_config:
            merged_config["env"] = {}
        merged_config["env"].update(petal.env)

        # Merge Petal parameters
        if "params" not in merged_config:
            merged_config["params"] = {}
        merged_config["params"].update(petal.params)

        # Merge Petal variables
        if "vars" not in merged_config:
            merged_config["vars"] = {}
        merged_config["vars"].update(petal.vars)

        return merged_config

    def validate_merged_config(self, petal: Petal, cfg: dict) -> bool:
        """Validate that the merged configuration is valid."""
        try:
            # Check that required parameters are present
            for param_name, param_def in petal.params.items():
                if param_def.required:
                    if param_name not in petal.params:
                        return False

            # Check that environment variables are properly set
            for env_name, env_value in petal.env.items():
                if env_value is None:
                    return False

            return True
        except Exception:
            return False
