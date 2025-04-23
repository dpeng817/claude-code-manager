import os
from typing import Any, Dict, List, Optional

import yaml


class ConfigManager:
    """Manages configuration for Claude Code Manager."""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            config_dir: Custom configuration directory path. If None, uses ~/.claude_code
        """
        if config_dir is None:
            self.config_dir = os.path.expanduser("~/.claude_code")
        else:
            self.config_dir = os.path.expanduser(config_dir)

        self.config_file = os.path.join(self.config_dir, "config.yaml")
        self.environments_dir = os.path.join(self.config_dir, "environments")
        self.instances_dir = os.path.join(self.config_dir, "instances")
        self.templates_dir = os.path.join(self.config_dir, "templates")

        # Ensure directories exist
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.environments_dir, exist_ok=True)
        os.makedirs(self.instances_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)

        # Initialize configuration
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                return yaml.safe_load(f) or {}
        else:
            default_config = {"default_work_dir": os.path.expanduser("~/claude_code_work"), "environments": {}}
            self._save_config(default_config)
            return default_config

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        with open(self.config_file, "w") as f:
            yaml.dump(config, f)

    def save(self) -> None:
        """Save current configuration."""
        self._save_config(self.config)

    def get_environment_config(self, env_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific environment.

        Args:
            env_name: Name of the environment

        Returns:
            Environment configuration dictionary or None if not found
        """
        env_file = os.path.join(self.environments_dir, f"{env_name}.yaml")
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                return yaml.safe_load(f)
        return None

    def save_environment_config(self, env_name: str, config: Dict[str, Any]) -> None:
        """
        Save configuration for a specific environment.

        Args:
            env_name: Name of the environment
            config: Environment configuration dictionary
        """
        env_file = os.path.join(self.environments_dir, f"{env_name}.yaml")

        # Use safe_dump to preserve formatting
        with open(env_file, "w") as f:
            yaml.safe_dump(config, f, default_flow_style=False)

        # Update main config with environment reference
        self.config.setdefault("environments", {})
        print("Current environments:", self.config["environments"])
        try:
            self.config["environments"][env_name] = {}
        except Exception as e:
            print("THAT DIDN'T WORK", e)
        self.config["environments"][env_name] = {"description": config.get("description", ""), "config_file": env_file}
        self.save()

    def delete_environment_config(self, env_name: str) -> bool:
        """
        Delete configuration for a specific environment.

        Args:
            env_name: Name of the environment

        Returns:
            True if deleted, False if not found
        """
        env_file = os.path.join(self.environments_dir, f"{env_name}.yaml")
        if os.path.exists(env_file):
            os.remove(env_file)

            # Remove from main config
            if env_name in self.config.get("environments", {}):
                del self.config["environments"][env_name]
                self.save()
            return True
        return False

    def list_environments(self) -> Dict[str, Dict[str, str]]:
        """
        List all configured environments.

        Returns:
            Dictionary of environment names and their descriptions
        """
        return self.config.get("environments", {})

    def get_instance_file(self, instance_id: str) -> str:
        """
        Get the path to an instance file.

        Args:
            instance_id: Instance identifier

        Returns:
            Path to the instance file
        """
        return os.path.join(self.instances_dir, f"{instance_id}.yaml")

    def save_instance(self, instance_id: str, instance_data: Dict[str, Any]) -> None:
        """
        Save instance data.

        Args:
            instance_id: Instance identifier
            instance_data: Instance data dictionary
        """
        instance_file = self.get_instance_file(instance_id)
        with open(instance_file, "w") as f:
            yaml.dump(instance_data, f)

    def get_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """
        Get instance data.

        Args:
            instance_id: Instance identifier

        Returns:
            Instance data dictionary or None if not found
        """
        instance_file = self.get_instance_file(instance_id)
        if os.path.exists(instance_file):
            with open(instance_file, "r") as f:
                return yaml.safe_load(f)
        return None

    def delete_instance(self, instance_id: str) -> bool:
        """
        Delete instance data.

        Args:
            instance_id: Instance identifier

        Returns:
            True if deleted, False if not found
        """
        instance_file = self.get_instance_file(instance_id)
        if os.path.exists(instance_file):
            os.remove(instance_file)
            return True
        return False

    def list_instances(self, env_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all instances, optionally filtered by environment type.

        Args:
            env_name: Optional environment name to filter by

        Returns:
            List of instance data dictionaries
        """
        instances = []
        for filename in os.listdir(self.instances_dir):
            if filename.endswith(".yaml"):
                instance_file = os.path.join(self.instances_dir, filename)
                with open(instance_file, "r") as f:
                    instance_data = yaml.safe_load(f)
                    if env_name is None or instance_data.get("environment") == env_name:
                        instances.append(instance_data)
        return instances

    def save_claude_md_template(self, env_name: str, content: str) -> str:
        """
        Save claude.md template content to a file.

        Args:
            env_name: Name of the environment
            content: Content for claude.md

        Returns:
            Path to the saved template file
        """
        template_path = os.path.join(self.templates_dir, f"{env_name}.md")
        with open(template_path, "w") as f:
            f.write(content)
        return template_path

    def get_claude_md_template(self, env_name: str) -> Optional[str]:
        """
        Get claude.md template content for an environment.

        Args:
            env_name: Name of the environment

        Returns:
            Template content or None if not found
        """
        template_path = os.path.join(self.templates_dir, f"{env_name}.md")
        if os.path.exists(template_path):
            with open(template_path, "r") as f:
                return f.read()
        return None
