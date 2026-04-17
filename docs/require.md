# `envpatch require`

Verify that a set of required keys are present in an `.env` file.
Useful in CI pipelines to catch missing configuration before deployment.

## Usage

```bash
envpatch require .env -k DB_HOST -k DB_PORT -k APP_SECRET
```

## Options

| Flag | Description |
|------|-------------|
| `-k / --key` | Required key name. Repeatable. |
| `--strict` | Exit with code 1 if any key is missing. |

## Example output

```
Required : 3
Present  : 2
Missing  : 1
Missing keys:
  - APP_SECRET
```

## Strict mode

Without `--strict`, the command always exits `0` and is informational only.
With `--strict`, a non-zero exit code is returned when one or more keys are
missing — suitable for use in shell scripts and CI steps:

```bash
envpatch require .env -k DB_HOST --strict || exit 1
```

## Python API

```python
from envpatch.requirer import require_keys

result = require_keys(open(".env").read(), ["DB_HOST", "APP_SECRET"])
if not result.is_satisfied:
    print(result.to_summary())
```
