# Publishing Guide for NguyenPanda Config

This document outlines the steps to build and publish `nguyenpanda-config` to PyPI (Production) and TestPyPI (Staging).

## Prerequisites

Ensure you have the build and upload tools installed. Since we use `uv`, you can install them as dev dependencies or use `uvx` (tool execution).

```bash
# Install twine locally
uv add --dev twine build
```

## 1. Build the Package

Before uploading, clear previous builds and generate new distribution archives (`.tar.gz` and `.whl`).

```bash
# Clean previous builds (Linux/Mac)
rm -rf dist/

# Build using the standard build module
uv run python -m build
```

You should now see a `dist/` folder containing the artifacts.

## 2. Publish to TestPyPI (Staging)

It is highly recommended to upload to TestPyPI first to ensure everything renders correctly.

### 1. **Upload:**

```bash
uv run twine upload --repository testpypi dist/*
```

* **Username:** `__token__`
* **Password:** Your TestPyPI API Token (starts with `pypi-`)

### 2. **Verify Installation:**

Try installing the package in a fresh environment to ensure dependencies and imports work.

```bash
# Create a temporary virtualenv
uv venv test_env
source test_env/bin/activate

# Install from TestPyPI
uv pip install --index-url [https://test.pypi.org/simple/](https://test.pypi.org/simple/) --extra-index-url [https://pypi.org/simple/](https://pypi.org/simple/) nguyenpanda-config
```

## 3. Publish to PyPI (Production)

Once the test release is verified:

### 1. **Upload:**

```bash
uv run twine upload dist/*
```

* **Username:** `__token__`
* **Password:** Your real PyPI API Token (starts with `pypi-`)

### 2. **Verification:**

Wait a few minutes, then check the page at [https://pypi.org/project/nguyenpanda-config/](https://www.google.com/search?q=https://pypi.org/project/nguyenpanda-config/).

## Versioning Workflow

Remember to bump the version number in `pyproject.toml` (or your version source) before running the build command.

1. Update version in `pyproject.toml`.
2. Commit changes: `git commit -m "Bump version to x.y.z"`.
3. Create a git tag: `git tag vx.y.z`.
4. Run the build and upload steps above.
