"""
CLI interface for Claude Code Manager.
Provides command-line commands for interacting with Claude Code environments.
"""

import os
import sys
import click
from typing import Optional

from .core import ClaudeCodeManager
from .utils import print_success, print_error, print_info, print_warning


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option()
def cli():
    """
    Claude Code Manager - A tool for managing Claude Code environments.
    
    This tool helps you define, scaffold, and manage temporary working
    environments for Claude Code projects.
    """
    pass


@cli.command('setup')
@click.argument('env_name', required=False)
def setup(env_name: Optional[str] = None):
    """
    Configure a new environment type.
    
    ENV_NAME is an optional name for the environment.
    """
    manager = ClaudeCodeManager()
    manager.setup_environment(env_name)


@cli.command('scaffold')
@click.argument('env_name', required=True)
@click.option('--dir', '-d', help='Working directory for the environment')
def scaffold(env_name: str, dir: Optional[str] = None):
    """
    Create a new environment instance.
    
    ENV_NAME is the name of the environment to scaffold.
    """
    manager = ClaudeCodeManager()
    manager.scaffold_environment(env_name, dir)


@cli.command('choose')
@click.argument('env_name', required=False)
@click.option('--instance', '-i', help='Instance ID to select')
def choose(env_name: Optional[str] = None, instance: Optional[str] = None):
    """
    Select an environment instance to work with.
    
    ENV_NAME is an optional environment name to filter instances.
    """
    manager = ClaudeCodeManager()
    manager.choose_environment(env_name, instance)


@cli.command('del')
@click.argument('instance_id', required=False)
@click.option('--env', '-e', help='Environment name to filter instances')
def delete(instance_id: Optional[str] = None, env: Optional[str] = None):
    """
    Remove environment instances.
    
    INSTANCE_ID is an optional instance ID to delete.
    If not provided, a selection menu will be shown.
    """
    manager = ClaudeCodeManager()
    manager.delete_environment_instance(instance_id, env)


@cli.command('list')
@click.argument('env_name', required=False)
def list_instances(env_name: Optional[str] = None):
    """
    Show existing environment instances.
    
    ENV_NAME is an optional environment name to filter instances.
    """
    manager = ClaudeCodeManager()
    manager.list_instances(env_name)


@cli.command('envs')
def list_environments():
    """
    List all configured environment types.
    """
    manager = ClaudeCodeManager()
    manager.list_env_types()


def main():
    """
    Main entry point for the CLI.
    """
    try:
        cli()
    except KeyboardInterrupt:
        print_info("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()