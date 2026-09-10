# Contributing to MorseToolkit

Thank you for considering contributing to MorseToolkit! This document provides guidelines for contributing to the project.

## Development Setup

1. Fork and clone the repository:
	```bash
	git clone [https://github.com/your-username/MorseToolkit.git](https://github.com/your-username/MorseToolkit.git)
	cd MorseToolkit
	```

2. Set up a virtual environment and install dependencies:
	```bash
	python -m venv .venv
	source .venv/bin/activate  # On Windows: .venv\Scripts\activate
	pip install -e .[dev]
	```

## Running Tests and Linting

Before submitting a pull request, ensure all tests pass and code style guidelines are met.

- **Run tests:**
	```bash
	pytest
	```

- **Check code formatting and linting:**
	```bash
	ruff check .
	ruff format --check .
	```

- **Automatically format code:**
	```bash
	ruff format .
	```

## Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` A new feature
- `fix:` A bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, missing semi-colons, etc.)
- `refactor:` Code refactoring without changing functionality
- `test:` Adding or updating tests
- `chore:` Maintenance tasks, build processes, or dependency updates

**Example:**
```text
feat: add binary tree decoding support for morse signals
```

## Submitting Pull Requests
- Create a descriptive branch name (feat/tree-decoder or fix/signal-parsing).
- Make your changes and commit using Conventional Commits.
- Push your branch to GitHub and submit a Pull Request against the main branch.
- Ensure all GitHub Actions CI checks pass.
