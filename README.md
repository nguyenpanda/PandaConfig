# PandaConfig

**PandaConfig** is a logic-driven configuration library that transforms static YAML into executable code. It supports variable resolution, Python function execution, and inheritance directly within your config files.

## Features

* **Variables**: Define once, reuse anywhere (`url: http://$host:$port`).
* **Functions**: Execute logic inside YAML (`files: $(glob ./data *.csv)`).
* **Inheritance**: Modularize configs with `extends`.
* **Custom Extensions**: Register your own Python functions.

## Installation

```bash
pip install nguyenpanda-config
```

## How to Use

### 1. The YAML Configuration

PandaConfig extends YAML with `extends`, `$variable`, and `$(function)` syntax.

```yaml
# prod.yaml
extends: "./base.yaml"  # Inherit settings

app_name: "PandaApp"
server:
  host: "localhost"
  port: 8080
  url: "http://$host:$port/api"  # Variable substitution

logging:
  # Function execution
  file: "$(find_ancestor . pyproject.toml)/logs/$(now).log"
```

### 2. Loading in Python

```python
from PandaConfig import PandaConfig

# Load and resolve
agent = PandaConfig("prod.yaml")
config = agent.config

print(config['server']['url']) 
# Output: http://localhost:8080/api
```

## Custom Functions

Inject your own logic using the `registration` decorator.

```python
import os
from PandaConfig import PandaConfig

agent = PandaConfig("config.yaml")

@agent.registration("get_env", 2) # Register function 'get_env' with 2 args
def get_env(key, default):
    return os.getenv(key, default)

# YAML Usage: 
# secret: "$(get_env API_KEY 12345)"
```

## Built-in Functions

| Function | Args | Description |
| --- | --- | --- |
| `path` | 1 | Convert string to `Path` object |
| `abspath` | 1 | Get absolute path |
| `glob` | 2 | `(dir, pattern)` List matching files |
| `rglob` | 2 | Recursive glob |
| `find_ancestor` | 2 | `(path, target)` Find parent dir containing target |
| `now` | 0 | Current timestamp |
| `strftime` | 2 | `(time_str, fmt)` Format timestamp |
| `list` | 1 | Wrap item in list `[item]` |
| `filter` | 2 | `(func, list)` Filter list items |
| `not` | 1 | Boolean negation |

## Running Tests

```bash
pytest tests/

```
