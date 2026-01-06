# Development & Documentation

This documentation is built using [MkDocs](https://www.mkdocs.org/). Since this project uses `uv` for dependency management, you should run the documentation commands using `uv run`.

## Common Commands

* **Serve documentation locally**:

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

```text
mkdocs.yml    # The configuration file.
docs/
    index.md  # This homepage.
    ...       # Add your tutorials and API references here.
```
