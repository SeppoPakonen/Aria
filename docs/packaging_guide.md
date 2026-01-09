# Aria Packaging and Distribution Guide

This document outlines how to package Aria for local development and distribution.

## Project Structure

Aria is structured as a Python-based CLI application:

- `src/`: Contains the core logic and the main entry point (`aria.py`).
- `docs/`: Manuals, runbooks, and planning documents.
- `tests/`: Unit and integration tests.
- `selenium_hybrid_scripts/`: Utility scripts for launching browsers in debug mode.
- `requirements.txt`: List of Python dependencies.

## Local Installation (Development)

To run Aria from source:

1.  **Clone the repository.**
2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up the Gemini API Key:**
    ```bash
    export GEMINI_API_KEY="your-api-key" # On Windows: set GEMINI_API_KEY=your-api-key
    ```
5.  **Run the CLI:**
    ```bash
    python src/aria.py --help
    ```

## Packaging for Distribution

### Current Method: Source Distribution
Currently, Aria is distributed as source code. To "package" it, you can create a compressed archive of the project directory:

```bash
# Example using zip on Windows/Linux
zip -r aria-v0.1.0.zip . -x "*.git*" "*__pycache__*" "*venv*"
```

### Future Method: Python Package (PEP 517/518)
In the future, we will transition to using a `pyproject.toml` file to allow standard installation via `pip`:

```bash
pip install .
```

This will automatically handle dependencies and create an `aria` executable in your path.

## Versioning Strategy

Aria uses [Semantic Versioning (SemVer)](https://semver.org/): `MAJOR.MINOR.PATCH`.

- **MAJOR**: Incompatible API changes.
- **MINOR**: Add functionality in a backwards compatible manner.
- **PATCH**: Backwards compatible bug fixes.

The current version is tracked in `src/aria.py` via the `VERSION` constant.

## Release Checklist

Before releasing a new version:

1.  **Update Version**: Update `VERSION` in `src/aria.py`.
2.  **Run Tests**: Ensure all tests pass (`pytest`).
3.  **Update Documentation**: Ensure `README.md` and runbooks reflect the latest changes.
4.  **Tag Release**: Create a Git tag (e.g., `git tag v0.1.0`).
5.  **Build Package**: Create the distribution archive.
6.  **Publish**: Upload to the distribution channel (e.g., GitHub Releases).
