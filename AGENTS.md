# Agent Protocol: Yeti-Dabble

This document defines the mandatory protocol for all development activities within the `yeti-dabble` codebase. Following this protocol ensures codebase consistency, type safety, and reliability.

## Workflow Requirements

After any code change, you **must** perform the following steps before considering the task complete:

1.  **Type Checking**: Run `mypy` to ensure static type safety.
2.  **Linting and Formatting**: Run `ruff` to enforce coding standards and ensure consistent formatting.
3.  **Testing**: Run the project's test suite to verify changes and ensure no regressions.

## Command Reference

When performing these checks, use the following commands:

-   **Mypy**: `uv run mypy .`
-   **Linting/Formatting**: `uv run ruff check . --fix` and `uv run ruff format .`
-   **Tests**: `uv run pytest`

*Failure to run these tools after modifications is a violation of the development workflow.*
