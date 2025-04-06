"""
Environment management for Claude Code Manager.
Handles environment creation, configuration, and scaffolding.
"""

import os
import shutil
import uuid
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import git

from .config import ConfigManager


class EnvironmentManager:
    """Manages Claude Code environments."""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize the environment manager.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager or ConfigManager()
    
    def create_environment_config(self, env_name: str, config: Dict[str, Any], claude_md_content: Optional[str] = None) -> None:
        """
        Create a new environment configuration.
        
        Args:
            env_name: Name of the environment
            config: Environment configuration
            claude_md_content: Optional content for claude.md
        """
        # Ensure required fields are present with proper types
        if "repositories" not in config or not isinstance(config["repositories"], list):
            config["repositories"] = []
            
        if "scaffold_commands" not in config or not isinstance(config["scaffold_commands"], list):
            config["scaffold_commands"] = []
        
        # Add creation timestamp
        config["created_at"] = datetime.now().isoformat()
        
        # Save claude.md content to a separate file if provided
        if claude_md_content:
            self.config_manager.save_claude_md_template(env_name, claude_md_content)
        
        # Save to config
        self.config_manager.save_environment_config(env_name, config)
    
    def scaffold_environment(self, env_name: str, work_dir: Optional[str] = None) -> Optional[str]:
        """
        Scaffold a new environment instance.
        
        Args:
            env_name: Name of the environment
            work_dir: Working directory for the environment
            
        Returns:
            Path to the scaffolded environment or None if failed
        """
        # Load environment config
        env_config = self.config_manager.get_environment_config(env_name)
        if env_config is None:
            return None
        
        # Create a unique ID for this instance
        instance_id = str(uuid.uuid4())
        
        # Determine work directory
        if work_dir is None:
            default_work_dir = self.config_manager.config.get(
                "default_work_dir", 
                os.path.expanduser("~/claude_code_work")
            )
            instance_dir = os.path.join(default_work_dir, f"{env_name}_{instance_id[:8]}")
        else:
            instance_dir = os.path.expanduser(work_dir)
        
        # Create directory
        os.makedirs(instance_dir, exist_ok=True)
        
        # Clone repositories
        for repo_config in env_config.get("repositories", []):
            repo_url = repo_config.get("url")
            repo_path = repo_config.get("path", "")
            repo_branch = repo_config.get("branch")
            
            if repo_url:
                target_path = os.path.join(instance_dir, repo_path)
                self._clone_repository(repo_url, target_path, repo_branch)
        
        # Create claude.md from template
        claude_md_content = self.config_manager.get_claude_md_template(env_name)
        if claude_md_content:
            claude_md_path = os.path.join(instance_dir, "claude.md")
            with open(claude_md_path, 'w') as f:
                f.write(claude_md_content)
        
        # Run scaffold commands
        for command_config in env_config.get("scaffold_commands", []):
            command = command_config.get("command", "")
            if command:
                # Replace placeholders
                command = command.replace("${WORK_DIR}", instance_dir)
                
                # Run command
                try:
                    subprocess.run(command, shell=True, check=True, cwd=instance_dir)
                except subprocess.CalledProcessError as e:
                    print(f"Error running scaffold command: {e}")
        
        # Save instance info
        instance_info = {
            "id": instance_id,
            "environment": env_name,
            "path": instance_dir,
            "created_at": datetime.now().isoformat()
        }
        self.config_manager.save_instance(instance_id, instance_info)
        
        return instance_dir
    
    def _clone_repository(self, repo_url: str, target_path: str, branch: Optional[str] = None) -> bool:
        """
        Clone a Git repository.
        
        Args:
            repo_url: Repository URL
            target_path: Target path
            branch: Branch to checkout
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create parent directory if needed
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            # Clone repository
            clone_args = ['--depth', '1']  # Shallow clone for speed
            if branch:
                clone_args.extend(['--branch', branch])
            
            git.Repo.clone_from(repo_url, target_path, multi_options=clone_args)
            return True
        except Exception as e:
            print(f"Error cloning repository {repo_url}: {e}")
            return False
    
    def delete_environment(self, env_name: str) -> bool:
        """
        Delete an environment configuration.
        
        Args:
            env_name: Name of the environment
            
        Returns:
            True if deleted, False if not found
        """
        return self.config_manager.delete_environment_config(env_name)
    
    def delete_instance(self, instance_id: str, remove_files: bool = True) -> bool:
        """
        Delete an environment instance.
        
        Args:
            instance_id: Instance identifier
            remove_files: Whether to remove the instance files
            
        Returns:
            True if deleted, False if not found
        """
        instance_data = self.config_manager.get_instance(instance_id)
        if instance_data is None:
            return False
        
        # Remove instance directory
        if remove_files and "path" in instance_data:
            instance_path = instance_data["path"]
            if os.path.exists(instance_path):
                try:
                    shutil.rmtree(instance_path)
                except Exception as e:
                    print(f"Error removing instance directory: {e}")
        
        # Remove instance data
        return self.config_manager.delete_instance(instance_id)
    
    def list_environments(self) -> Dict[str, Dict[str, str]]:
        """
        List all configured environments.
        
        Returns:
            Dictionary of environment names and their descriptions
        """
        return self.config_manager.list_environments()
    
    def list_instances(self, env_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all instances, optionally filtered by environment type.
        
        Args:
            env_name: Optional environment name to filter by
            
        Returns:
            List of instance data dictionaries
        """
        return self.config_manager.list_instances(env_name)
    
    def get_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """
        Get instance data.
        
        Args:
            instance_id: Instance identifier
            
        Returns:
            Instance data dictionary or None if not found
        """
        return self.config_manager.get_instance(instance_id)