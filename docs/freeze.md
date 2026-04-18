# envpatch freeze

The `freeze` command annotates `.env` keys with a marker comment to indicate they should not be changed.

## Usage

```bash
envpatch freeze .env
envpatch freeze .env --key DB_HOST --key SECRET_KEY
envpatch freeze .env --output .env.frozen
envpatch freeze .env --marker "# locked"
```

## Options

| Option | Description |
|--------|-------------|
| `--key / -k` | Key(s) to freeze. Repeatable. Defaults to all keys. |
| `--marker` | Comment appended to frozen lines. Default: `# frozen` |
| `--output / -o` | Write output to a file instead of stdout. |

## Example

Input `.env`:
```
DB_HOST=localhost
SECRET_KEY=abc123
DEBUG=true
```

After `envpatch freeze .env --key DB_HOST`:
```
DB_HOST=localhost  # frozen
SECRET_KEY=abc123
DEBUG=true
```

## Notes

- The freeze command is non-destructive: it only appends comments.
- Use `--output` to avoid modifying the original file.
- Frozen markers are informational; enforcement is up to your workflow.
