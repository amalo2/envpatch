# envpatch inject

Inject variables from a `.env` file into the current process environment.

## Usage

```bash
envpatch inject .env [OPTIONS]
```

## Options

| Option | Description |
|---|---|
| `--overwrite` | Overwrite variables that already exist in the environment |
| `--prefix PREFIX` | Prepend `PREFIX` to every injected key |
| `--format [text\|export\|json]` | Output format (default: `text`) |

## Examples

### Basic injection (text summary)

```bash
envpatch inject .env
# Injected 3 key(s), skipped 0 key(s) (already set).
#   Injected: DB_HOST, DB_PORT, APP_KEY
```

### Shell-compatible export statements

Use `--format export` to emit `export KEY=value` lines that can be sourced
directly in your shell:

```bash
eval $(envpatch inject .env --format export)
```

### JSON output

```bash
envpatch inject .env --format json
```

```json
{
  "injected": ["DB_HOST", "DB_PORT"],
  "skipped": ["APP_KEY"],
  "injected_count": 2,
  "skipped_count": 1
}
```

### Namespace isolation with a prefix

Avoid key collisions by prefixing all injected variables:

```bash
envpatch inject .env --prefix MYAPP_
```

This injects `MYAPP_DB_HOST`, `MYAPP_DB_PORT`, etc., leaving any existing
`DB_HOST` untouched.

## Notes

- Without `--overwrite`, keys already present in the environment are **skipped**.
- The `inject` command operates on a copy of the environment for reporting;
  use the `export` format and `eval` to actually modify your shell session.
