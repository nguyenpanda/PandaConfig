# Welcome to NguyenPanda Config

**NguyenPanda Config** is a dynamic YAML configuration engine supporting variable interpolation, function calls, and file inheritance.

## Key Features

* **Variable Interpolation:** Dynamically inject values into your configuration at runtime.
* **Function Calls:** Execute logic directly within your YAML structure.
* **File Inheritance:** Keep your configs DRY (Don't Repeat Yourself) by inheriting properties from base files.

## Installation

Install the package via pip or uv:

```bash
# Using pip
pip install nguyenpanda-config

# Using uv
uv add nguyenpanda-config

```

## Quick Start

```python
from PandaConfig import PandaConfig

# Load your dynamic configuration
panda_config = PandaConfig('./config.yaml')
config = panda_config.get()
ip = config['ip']
port = config['port']

```

## Development & Documentation

This documentation is built using [MkDocs](https://www.mkdocs.org/). Since this project uses `uv` for dependency management, you should run the documentation commands using `uv run`.

### Common Commands

```bash
uv run --group docs mkdocs serve

```

* **Build the site** (Static HTML):

```bash
uv run --group docs mkdocs build

```

* **Deploy to GitHub Pages**:

```bash
uv run --group docs mkdocs gh-deploy

```

## Project Layout

```
mkdocs.yml    # The configuration file.
docs/
    index.md  # This homepage.
    ...       # Add your tutorials and API references here.

```
