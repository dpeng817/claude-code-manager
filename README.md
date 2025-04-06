# Claude Code Manager (ccm)

A CLI tool for managing temporary working environments for Claude Code. This tool allows you to define, scaffold, and manage different environments with specific configurations.

## Installation

```bash
pip install claude-code-manager
```

## Features

- Define named environment configurations
- Configure repositories to download for each environment
- Add customized claude.md files to environments
- Run arbitrary commands during the scaffolding process
- Interactive CLI with arrow key selection
- Clean architecture with modular components

## Usage

### Installation
- Install as an editable python package.
- 
### Available Commands

- `ccm setup`: Configure a new environment type
- `ccm scaffold <env-name>`: Create a new environment instance
- `ccm choose [env-name]`: Select an environment instance to work with
- `ccm del [env-name]`: Remove environment instances
- `ccm list [env-name]`: Show existing environment instances
- `ccm envs`: List all configured environment types

### Configuration

Configuration is stored in `~/.claude_code` by default.

### Example

```bash
# Create a new environment configuration
ccm setup

# Scaffold a new environment instance
ccm scaffold my-project

# List all available environments
ccm envs
```

## License

MIT
