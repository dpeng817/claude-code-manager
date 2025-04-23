# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- Build: `pip install -e .` (run in the virtual environment at project root)
- Format: `ruff format .` (formats code according to style guidelines)
- Lint: `ruff check .` (lints code for errors and style issues)
- Test: No tests configured yet
- Run: `ccm <command>` (see README.md for available commands)

## Code Style Guidelines
- **Imports**: Group standard lib, then third-party, then local imports with a blank line between
- **Types**: Use type hints consistently (`typing` module) for all function parameters and returns
- **Formatting**: 4-space indentation, 120 char line length max
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Documentation**: Docstrings for all functions/classes using """triple quotes"""
- **Error Handling**: Use try/except blocks with specific exceptions, log errors appropriately
- **Functions**: Keep functions small and focused on a single responsibility
- **CLI Design**: Follow click patterns with descriptive help text and consistent command structure

Remember this is a CLI tool for managing Claude Code environments with a focus on clean architecture and good UX.