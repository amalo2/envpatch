# Type Checking

The `typecheck` command inspects the values in a `.env` file and attempts to detect their semantic types.

## Supported Types

| Type      | Example                                  |
|-----------|------------------------------------------|
| `bool`    | `true`, `false`, `yes`, `no`, `1`, `0`   |
| `int`     | `42`, `-7`                               |
| `float`   | `3.14`, `-0.5`                           |
| `url`     | `https://example.com`                    |
| `email`   | `admin@example.com`                      |
| `uuid`    | `550e8400-e29b-41d4-a716-446655440000`   |
| `path`    | `/usr/local/bin`, `./config/settings`    |
| `json`    | `{"key": "value"}`, `[1, 2, 3]`         |

Values that do not match any pattern are reported as **untyped**.

## Usage

```bash
envpatch typecheck .env
```

### Options

| Flag                | Description                          |
|---------------------|--------------------------------------|
| `--show-untyped`    | Print a list of untyped keys         |
| `--fail-on-untyped` | Exit with code 1 if untyped keys exist |
| `--format`          | Output format: `text` (default) or `json` |

## Example Output

```
Typed keys   : 2
Untyped keys : 1
  PORT = '8080'  [int]
  DEBUG = 'true'  [bool]
Untyped:
  APP_NAME
```

## Programmatic Use

```python
from envpatch.typecheck import typecheck_env

result = typecheck_env({"PORT": "8080", "NAME": "myapp"})
print(result.to_summary())
```

### Accessing Individual Results

Each key in the result can be inspected individually:

```python
from envpatch.typecheck import typecheck_env

result = typecheck_env({"PORT": "8080", "DEBUG": "true", "APP_NAME": "myapp"})

for key, info in result.items():
    print(f"{key}: {info.detected_type or 'untyped'}")

# Output:
# PORT: int
# DEBUG: bool
# APP_NAME: untyped
```
