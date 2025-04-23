import os
import subprocess
from collections.abc import Sequence
from typing import Optional

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("claude-code-manager")


def _subprocess(command: Sequence[str], cwd: str) -> str:
    """Call to `subprocess.check_output` with exception output exposed.

    This is used to provide additional context to the `mcp.tool`.

    Args:
        command: Sequence of command arguments.
        cwd: Current working directory.

    Returns:
        Decoded command output.
    """
    try:
        return subprocess.check_output(
            command,
            cwd=cwd,
            stderr=subprocess.STDOUT,
        ).decode("utf-8")
    except subprocess.CalledProcessError as e:
        raise Exception(e.output)

@mcp.tool()
async def list_environments():
    """
    List all configured environment types.
    """
    return _subprocess(["ccm", "envs"], cwd=os.getcwd())

@mcp.tool()
async def list_instances(env_name: Optional[str] = None):
    """
    Show existing environment instances.

    ENV_NAME is an optional environment name to filter instances.
    """
    return _subprocess(["ccm", "list", env_name], cwd=os.getcwd())

@mcp.tool()
async def delete(instance_id: Optional[str] = None, env: Optional[str] = None):
    """
    Delete an environment instance. Call this when you're done with the environment.

    INSTANCE_ID is the ID of the instance to delete.
    ENV is an optional environment name to filter instances.
    """
    return _subprocess(["ccm", "del", instance_id, "--env", env], cwd=os.getcwd())

@mcp.tool()
async def setup(env_name: Optional[str] = None):
    """
    Setup an environment. Call this when you're ready to start working on a new environment.
    """
    return _subprocess(["ccm", "setup", env_name], cwd=os.getcwd())

@mcp.tool()
async def scaffold(env_name: str, dir: Optional[str] = None):
    """
    Scaffold an environment. Call this when you need to create a new environment.
    """
    params = ["ccm", "scaffold", "--env-name", env_name]
    if dir:
        params.extend(["--dir", dir])
    return _subprocess(params, cwd=os.getcwd())

@mcp.tool()
async def choose(env_name: Optional[str] = None, instance: Optional[str] = None):
    """
    Choose an environment instance. Call this when you need to start working on an existing environment.
    """
    params = ["ccm", "choose"]
    if env_name:
        params.extend(["--env-name", env_name])
    if instance:
        params.extend(["--instance", instance])
    return _subprocess(params, cwd=os.getcwd())

@mcp.tool()
async def scaffold_help():
    """
    Show help for the scaffold command.
    """
    params = ["ccm", "scaffold", "-h"]
    return _subprocess(params, cwd=os.getcwd())

@mcp.tool()
async def choose_help():
    """
    Show help for the choose command.
    """
    params = ["ccm", "choose", "--help"]
    return _subprocess(params, cwd=os.getcwd())

@mcp.tool()
async def delete_help():
    """
    Show help for the delete command.
    """
    params = ["ccm", "del", "--help"]
    return _subprocess(params, cwd=os.getcwd())

@mcp.tool()
async def setup_help():
    """
    Show help for the setup command.
    """
    params = ["ccm", "setup", "--help"]
    return _subprocess(params, cwd=os.getcwd())

def main():
    """
    Main entry point for the MCP server.
    """
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()









