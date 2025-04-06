"""
Core functionality for Claude Code Manager.
Provides high-level operations for the CLI interface.
"""

import os
import time
import inquirer
from typing import Dict, List, Any, Optional, Tuple

from .config import ConfigManager
from .environment import EnvironmentManager
from .utils import (
    print_success, print_error, print_info, print_warning,
    print_table, display_environment_details, open_editor,
    with_spinner, format_time_ago
)


class ClaudeCodeManager:
    """
    Core manager for Claude Code environments.
    Provides high-level operations for the CLI interface.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the Claude Code Manager.
        
        Args:
            config_dir: Custom configuration directory path
        """
        self.config_manager = ConfigManager(config_dir)
        self.env_manager = EnvironmentManager(self.config_manager)
    
    def setup_environment(self, env_name: Optional[str] = None) -> bool:
        """
        Set up a new environment configuration interactively.
        
        Args:
            env_name: Optional environment name
            
        Returns:
            True if successful, False otherwise
        """
        # If environment name is not provided, ask for it
        if env_name is None:
            questions = [
                inquirer.Text(
                    'name',
                    message="What is the name of this environment?",
                    validate=lambda _, x: len(x) > 0
                )
            ]
            answers = inquirer.prompt(questions)
            if not answers:
                return False
            env_name = answers['name']
        
        # Check if environment already exists
        if self.config_manager.get_environment_config(env_name):
            print_warning(f"Environment '{env_name}' already exists. Overwrite?")
            questions = [
                inquirer.Confirm('overwrite', message="Overwrite?", default=False)
            ]
            answers = inquirer.prompt(questions)
            if not answers or not answers['overwrite']:
                return False
        
        # Get environment description
        questions = [
            inquirer.Text(
                'description',
                message="Provide a description for this environment:"
            )
        ]
        answers = inquirer.prompt(questions)
        if not answers:
            return False
        description = answers['description']
        
        # Initialize environment config
        env_config = {
            "name": env_name,
            "description": description,
            "repositories": [],
            "scaffold_commands": [],
            "claude_md": ""
        }
        
        # Configure repositories
        print_info("Configure repositories to clone:")
        while True:
            questions = [
                inquirer.Confirm('add_repo', message="Add a repository?", default=True)
            ]
            answers = inquirer.prompt(questions)
            if not answers or not answers['add_repo']:
                break
            
            questions = [
                inquirer.Text(
                    'url',
                    message="Repository URL:",
                    validate=lambda _, x: len(x) > 0
                ),
                inquirer.Text(
                    'path',
                    message="Local path (relative to work dir, leave empty for root):"
                ),
                inquirer.Text('branch', message="Branch (leave empty for default):")
            ]
            repo_answers = inquirer.prompt(questions)
            if not repo_answers:
                continue
            
            repo_config = {
                "url": repo_answers['url'],
                "path": repo_answers['path'] or ".",
                "branch": repo_answers['branch'] or None
            }
            env_config["repositories"].append(repo_config)
        
        # Configure scaffold commands
        print_info("Configure commands to run during scaffolding:")
        print_info("You can use ${WORK_DIR} as a placeholder for the work directory")
        while True:
            questions = [
                inquirer.Confirm(
                    'add_command', 
                    message="Add a scaffold command?", 
                    default=True
                )
            ]
            answers = inquirer.prompt(questions)
            if not answers or not answers['add_command']:
                break
            
            questions = [
                inquirer.Text(
                    'command',
                    message="Command:",
                    validate=lambda _, x: len(x) > 0
                )
            ]
            cmd_answers = inquirer.prompt(questions)
            if not cmd_answers:
                continue
            
            cmd_config = {
                "command": cmd_answers['command']
            }
            env_config["scaffold_commands"].append(cmd_config)
        
        # Configure claude.md content
        print_info("Configure claude.md content:")
        questions = [
            inquirer.Confirm(
                'edit_claude_md', 
                message="Edit claude.md content in an external editor?", 
                default=True
            )
        ]
        answers = inquirer.prompt(questions)
        
        claude_md_content = None
        if answers and answers.get('edit_claude_md', False):
            try:
                claude_md_content = open_editor("")
                if not claude_md_content:
                    print_info("No content provided for claude.md")
            except Exception as e:
                print_error(f"Error editing claude.md content: {e}")
        
        # Save environment configuration (claude.md is saved separately)
        print("ATTEMPTING TO SAVE ENVIRONMENT CONFIG")
        self.env_manager.create_environment_config(env_name, env_config, claude_md_content)
        print_success(f"Environment '{env_name}' configured successfully!")
        return True
    
    def scaffold_environment(self, env_name: str, work_dir: Optional[str] = None) -> bool:
        """
        Scaffold a new environment instance.
        
        Args:
            env_name: Name of the environment
            work_dir: Optional working directory
            
        Returns:
            True if successful, False otherwise
        """
        # Check if environment exists
        env_config = self.config_manager.get_environment_config(env_name)
        if not env_config:
            print_error(f"Environment '{env_name}' does not exist")
            return False
        
        # Scaffold environment
        print_info(f"Scaffolding environment '{env_name}'...")
        instance_dir = with_spinner(
            f"Scaffolding environment '{env_name}'...",
            self.env_manager.scaffold_environment,
            env_name,
            work_dir
        )
        
        if not instance_dir:
            print_error(f"Failed to scaffold environment '{env_name}'")
            return False
        
        print_success(f"Environment '{env_name}' scaffolded successfully at: {instance_dir}")
        return True
    
    def choose_environment(self, env_name: Optional[str] = None, instance_id: Optional[str] = None) -> bool:
        """
        Choose an environment instance to work with.
        
        Args:
            env_name: Optional environment name
            instance_id: Optional instance identifier
            
        Returns:
            True if successful, False otherwise
        """
        # If both env_name and instance_id are None, list all environments
        if env_name is None and instance_id is None:
            environments = self.env_manager.list_environments()
            if not environments:
                print_error("No environments configured")
                return False
            
            # Ask user to select an environment
            questions = [
                inquirer.List(
                    'env_name',
                    message="Select an environment:",
                    choices=[(f"{name} - {env['description']}", name) for name, env in environments.items()]
                )
            ]
            answers = inquirer.prompt(questions)
            if not answers:
                return False
            env_name = answers['env_name']
        
        # If instance_id is None but env_name is provided, list instances for that environment
        if instance_id is None:
            instances = self.env_manager.list_instances(env_name)
            if not instances:
                print_error(f"No instances found for environment '{env_name}'")
                return False
            
            # Format instances for display
            formatted_instances = []
            for instance in instances:
                created_at = format_time_ago(instance.get('created_at', ''))
                choice_text = f"{instance.get('id', '')[:8]} - {instance.get('path', '')} ({created_at})"
                formatted_instances.append((choice_text, instance.get('id', '')))
            
            # Ask user to select an instance
            questions = [
                inquirer.List(
                    'instance_id',
                    message="Select an instance:",
                    choices=formatted_instances
                )
            ]
            answers = inquirer.prompt(questions)
            if not answers:
                return False
            instance_id = answers['instance_id']
        
        # Get instance data
        instance = self.env_manager.get_instance(instance_id)
        if not instance:
            print_error(f"Instance not found: {instance_id}")
            return False
        
        print_success(f"Selected instance: {instance.get('path', '')}")
        
        # Ask user what to do with the instance
        questions = [
            inquirer.List(
                'action',
                message="What would you like to do?",
                choices=[
                    ("Open in terminal", "terminal"),
                    ("Open in editor", "editor"),
                    ("Show details", "details"),
                    ("Delete instance", "delete"),
                    ("Nothing", "nothing")
                ]
            )
        ]
        answers = inquirer.prompt(questions)
        if not answers:
            return False
        
        action = answers['action']
        instance_path = instance.get('path', '')
        
        if action == 'terminal':
            # Open a terminal in the instance directory
            os.system(f"cd {instance_path} && $SHELL")
            return True
        elif action == 'editor':
            # Open in preferred editor
            editor = os.environ.get("EDITOR", "code")  # Default to VS Code
            os.system(f"{editor} {instance_path}")
            return True
        elif action == 'details':
            # Show instance details
            print_info(f"Instance ID: {instance.get('id', '')}")
            print_info(f"Environment: {instance.get('environment', '')}")
            print_info(f"Path: {instance.get('path', '')}")
            print_info(f"Created: {instance.get('created_at', '')}")
            return True
        elif action == 'delete':
            # Confirm deletion
            questions = [
                inquirer.Confirm(
                    'confirm',
                    message="Are you sure you want to delete this instance?",
                    default=False
                )
            ]
            answers = inquirer.prompt(questions)
            if answers and answers['confirm']:
                success = self.env_manager.delete_instance(instance_id)
                if success:
                    print_success("Instance deleted successfully")
                else:
                    print_error("Failed to delete instance")
                return success
            return False
        
        return True
    
    def delete_environment_instance(self, instance_id: Optional[str] = None, env_name: Optional[str] = None) -> bool:
        """
        Delete an environment instance.
        
        Args:
            instance_id: Optional instance identifier
            env_name: Optional environment name to filter instances
            
        Returns:
            True if deleted, False otherwise
        """
        # If instance_id is None, list instances to select from
        if instance_id is None:
            instances = self.env_manager.list_instances(env_name)
            if not instances:
                print_error("No instances found")
                return False
            
            # Format instances for display
            formatted_instances = []
            for instance in instances:
                env = instance.get('environment', '')
                created_at = format_time_ago(instance.get('created_at', ''))
                choice_text = f"{instance.get('id', '')[:8]} - {env} - {instance.get('path', '')} ({created_at})"
                formatted_instances.append((choice_text, instance.get('id', '')))
            
            # Ask user to select an instance
            questions = [
                inquirer.List(
                    'instance_id',
                    message="Select an instance to delete:",
                    choices=formatted_instances
                )
            ]
            answers = inquirer.prompt(questions)
            if not answers:
                return False
            instance_id = answers['instance_id']
        
        # Get instance data
        instance = self.env_manager.get_instance(instance_id)
        if not instance:
            print_error(f"Instance not found: {instance_id}")
            return False
        
        # Confirm deletion
        questions = [
            inquirer.Confirm(
                'confirm',
                message=f"Are you sure you want to delete instance {instance_id[:8]} at {instance.get('path', '')}?",
                default=False
            )
        ]
        answers = inquirer.prompt(questions)
        if not answers or not answers['confirm']:
            return False
        
        # Delete instance
        success = self.env_manager.delete_instance(instance_id)
        if success:
            print_success("Instance deleted successfully")
        else:
            print_error("Failed to delete instance")
        
        return success
    
    def list_env_types(self) -> bool:
        """
        List all configured environments.
        
        Returns:
            True if environments exist, False otherwise
        """
        environments = self.env_manager.list_environments()
        if not environments:
            print_info("No environments configured")
            return False
        
        # Format data for table
        env_data = []
        for name, env in environments.items():
            env_data.append({
                "name": name,
                "description": env.get("description", ""),
            })
        
        # Print table
        columns = [
            {"key": "name", "header": "Name", "style": "bold"},
            {"key": "description", "header": "Description"}
        ]
        print_table("Configured Environments", env_data, columns)
        return True
    
    def list_instances(self, env_name: Optional[str] = None) -> bool:
        """
        List all environment instances.
        
        Args:
            env_name: Optional environment name to filter instances
            
        Returns:
            True if instances exist, False otherwise
        """
        instances = self.env_manager.list_instances(env_name)
        if not instances:
            if env_name:
                print_info(f"No instances found for environment '{env_name}'")
            else:
                print_info("No instances found")
            return False
        
        # Format data for table
        instance_data = []
        for instance in instances:
            instance_data.append({
                "id": instance.get("id", "")[:8],  # Show first 8 chars of UUID
                "environment": instance.get("environment", ""),
                "path": instance.get("path", ""),
                "created_at": format_time_ago(instance.get("created_at", ""))
            })
        
        # Print table
        columns = [
            {"key": "id", "header": "ID", "style": "bold"},
            {"key": "environment", "header": "Environment"},
            {"key": "path", "header": "Path"},
            {"key": "created_at", "header": "Created", "style": "italic"}
        ]
        print_table("Environment Instances", instance_data, columns)
        return True