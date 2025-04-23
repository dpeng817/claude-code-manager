"""
CLI interface for Claude Code Manager.
Provides command-line commands for interacting with Claude Code environments.
"""

import sys
from typing import Optional

import click

from .core import ClaudeCodeManager
from .utils import print_error, print_info

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option()
def cli():
    """
    Claude Code Manager - A tool for managing Claude Code environments.

    This tool helps you define, scaffold, and manage temporary working
    environments for Claude Code projects.
    """
    pass


@cli.command("setup")
@click.option("--env-name", "-e", help="The name of the environment to configure")
def setup(env_name: Optional[str] = None):
    """
    Configure a new environment type.

    Parameters:
        --env-name: The name of the environment to configure.
    """
    manager = ClaudeCodeManager()
    manager.setup_environment(env_name)


@cli.command("scaffold")
@click.option("--env-name", "-e", help="The name of the environment to scaffold")
@click.option("--dir", "-d", help="Working directory for the environment")
def scaffold(env_name: str, dir: Optional[str] = None):
    """
    Create a new environment instance.

    Parameters:
        --env-name: The name of the environment to scaffold.
        --dir: The working directory for the environment.
    """
    manager = ClaudeCodeManager()
    manager.scaffold_environment(env_name, dir)


@cli.command("choose")
@click.option("--env-name", "-e", help="The name of the environment to filter instances")
@click.option("--instance", "-i", help="Instance ID to select")
def choose(env_name: Optional[str] = None, instance: Optional[str] = None):
    """
    Select an environment instance to work with.

    Parameters:
        --env-name: The name of the environment to filter instances.
        --instance: The instance ID to select.
    """
    manager = ClaudeCodeManager()
    manager.choose_environment(env_name, instance)


@cli.command("del")
@click.option("--instance-id", "-i", help="The instance ID to delete")
@click.option("--env", "-e", help="The environment name to filter instances")
def delete(instance_id: Optional[str] = None, env: Optional[str] = None):
    """
    Remove environment instances.

    Parameters:
        --instance-id: The instance ID to delete.
        --env: The environment name to filter instances.
    """
    manager = ClaudeCodeManager()
    manager.delete_environment_instance(instance_id, env)


@cli.command("list")
@click.option("--env-name", "-e", help="The environment name to filter instances")
def list_instances(env_name: Optional[str] = None):
    """
    Show existing environment instances.

    Parameters:
        --env-name: The environment name to filter instances.
    """
    manager = ClaudeCodeManager()
    manager.list_instances(env_name)


@cli.command("envs")
def list_environments():
    """
    List all configured environment types.
    """
    manager = ClaudeCodeManager()
    manager.list_env_types()

@cli.command("mcp")
def mcp():
    """
    Start the MCP server.
    """
    from .mcp.server import main
    main()


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


if __name__ == "__main__":
    main()
