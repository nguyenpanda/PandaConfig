# PandaConfig

**PandaConfig** is a dynamic configuration engine designed to transform static configuration files into executable code. Unlike traditional loaders, it supports variable resolution, function execution, and file inheritance directly within your configs.

**Now supporting both YAML and JSON**, with an extensible architecture ready for future formats (like TOML, XML, or INI).

## Key Features

* **Multi-Format Support**: Works seamlessly with **YAML** (`.yaml`, `.yml`) and **JSON** (`.json`) out of the box.
* **Dynamic Variables**: Define values once and interpolate them anywhere (`url: "http://$host:$port"`).
* **Function Execution**: Run Python logic directly inside your config (`secret: "$(get_env API_KEY)"`).
* **File Inheritance**: Keep configs DRY (Don't Repeat Yourself) using the `extends` keyword.
* **Extensible Architecture**: Easily register custom functions or add support for new file formats without modifying the core library.

## Installation

Install via pip or uv:

```bash
# Using pip
pip install nguyenpanda-config

# Using uv
uv add nguyenpanda-config
```

## Quick Start

### 1. Define Your Configuration

PandaConfig works identically across different formats. Choose the one you prefer.

**Option A: YAML (`config.yaml`)**

```yaml
extends: "./base.yaml"

server:
  host: "localhost"
  port: 8080
  url: "http://$server.host:$server.port/api"     # Variable interpolation ($var)

logs:
  path: "$(path ./logs)/$(now).log"                # Function execution ($(func arg))
```

**Option B: JSON (`config.json`)**

```json
{
  "extends": "./base.json",
  "server": {
    "host": "localhost",
    "port": 8080,
    "url": "http://$server.host:$server.port/api"
  },
  "logs": {
    "path": "$(path ./logs)/$(now).log"
  }
}
```

### 2. Load it in Python

The `PandaConfig` class automatically detects the file type and parses it accordingly.

```python
from PandaConfig import PandaConfig

# Works for YAML
agent_yaml = PandaConfig("config.yaml")
print(agent_yaml.config['server']['url']) 
# Output: http://localhost:8080/api

# Works for JSON
agent_json = PandaConfig("config.json")
print(agent_json.config['server']['url'])
```

## Advanced Usage

### Custom Functions

You can extend the logic available inside your configuration files by registering Python functions.

```python
import os
from PandaConfig import PandaConfig

# 1. Initialize
agent = PandaConfig("config.yaml")

# 2. Register a custom function
@agent.registration("env", 1)  # Name='env', Expected Args=1
def get_env_var(key):
    return os.getenv(key, "UNKNOWN")

# 3. Use it in YAML/JSON: 
# db_password: "$(env DB_PASS)"
```

### Adding New File Formats (Future-Proofing)

PandaConfig is designed to be agnostic to the file format. You can register new parsers (e.g., TOML) dynamically.

```python
import tomllib
from PandaConfig import ConfigLoader

# Register a parser for .toml files
ConfigLoader.register_parser('.toml', lambda path: tomllib.load(open(path, "rb")))

# Now you can load TOML files!
agent = PandaConfig("settings.toml")
```

## Built-in Functions

PandaConfig comes with a suite of utility functions ready to use:

| Function | Args | Description |
| --- | --- | --- |
| `path` | 1 | Convert string to a system-safe `Path` object |
| `abspath` | 1 | Get the absolute path of a file/folder |
| `glob` | 2 | `(dir pattern)` List matching files |
| `rglob` | 2 | Recursive glob listing |
| `find_ancestor` | 2 | `(path target)` Find parent dir containing a target file |
| `now` | 0 | Get current timestamp |
| `list` | 1 | Wrap an item in a list `[item]` |
| `not` | 1 | Boolean negation |

## Advanced Usage

### Registering Custom File Types

You can extend PandaConfig to support other file formats (like TOML, JSON, or XML) by registering a custom parser.

Here is an example of how to register a **TOML** parser:

```python
from PandaConfig import PandaConfig
import toml
from pathlib import Path
from typing import Any

# 1. Define your parsing logic
def parse_toml(file_path: Path) -> dict[str, Any]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return toml.load(f) or {}
    except toml.TomlDecodeError as e:
        raise ValueError(f'Invalid TOML in {file_path}: {e}')

# 2. Register the parser for the .toml extension
PandaConfig.register_parser('.toml', lambda path: parse_toml(path))

# 3. Use PandaConfig with a .toml file
agent = PandaConfig("./pyproject.toml")
print(agent.yaml())
```

## Development & Testing

We use `uv` for dependency management and `pytest` for testing. The test suite is dynamic and automatically picks up new test cases added to the `data/cases` directory.

```bash
# Run all tests (YAML, JSON, etc.)
uv run pytest
```

---

## Author

* **Email:** [hatuongnguyen@0107gmail.com](hatuongnguyen@0107gmail.com)
* **GitHub:** [nguyenpanda](https://github.com/nguyenpanda)
* **Website:** [nguyenpanda.com](https://www.google.com/search?q=https://nguyenpanda.com)

If you find this project useful, please consider giving it a ⭐ on GitHub!

## License

This project is licensed under the **MIT License**.

You are free to use, modify, and distribute this software, provided that the original copyright notice and permission notice are included in all copies or substantial portions of the software.

See the [LICENSE](https://www.google.com/search?q=LICENSE) file for more details.
