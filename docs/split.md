# envpatch split

Split a `.env` file into multiple files based on key prefixes.

## Usage

```bash
envpatch split <env-file> --prefix <PREFIX> [--prefix <PREFIX> ...] [options]
```

## Options

| Flag | Description |
|------|-------------|
| `--prefix` | Key prefix to extract into its own file (repeatable) |
| `--output-dir` | Directory to write output files (default: `.`) |
| `--strip-prefix` | Remove the matched prefix from keys in the output file |
| `--no-unmatched` | Discard keys that don't match any prefix |
| `--dry-run` | Print summary without writing any files |

## Examples

### Split by `DB_` and `AWS_` prefixes

```bash
envpatch split .env --prefix DB_ --prefix AWS_ --output-dir ./split
```

Produces:
- `split/db.env` — all keys starting with `DB_`
- `split/aws.env` — all keys starting with `AWS_`
- `split/unmatched.env` — remaining keys

### Strip the prefix from output keys

```bash
envpatch split .env --prefix DB_ --strip-prefix --output-dir ./split
```

Input key `DB_HOST=localhost` becomes `HOST=localhost` in `db.env`.

### Dry run (no files written)

```bash
envpatch split .env --prefix DB_ --dry-run
```

Prints the split summary to stdout without touching the filesystem.

## Output

```
Segments: 2, Total keys: 6
  [DB_]: 2 key(s)
  [AWS_]: 2 key(s)
  [unmatched]: 2 key(s)
Written: ./split/db.env
Written: ./split/aws.env
Written: ./split/unmatched.env
```
