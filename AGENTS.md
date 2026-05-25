# AGENTS.md

This repository contains a FreeSimpleGUI application to search tax court opinions.
The data is located on huggingface.com
Primary language: Python 3.13.

## Environment

- Use Python 3.13
- VSCode
- Dependency manager: uv
- OS target: Windows 11
- Formatting: ruff format
- Linting: ruff check
- Testing: pytest

## Coding conventions

- Prefer pathlib over os.path
- Use single quotes
- Explicitly specify encoding='utf-8'
- Avoid type hints unless already used in the file
- Prefer pandas for tabular data work
