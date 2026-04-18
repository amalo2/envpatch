# envpatch alias

The `alias` command creates new keys that mirror the values of existing keys in a `.env` file.
This is useful when migrating key names while keeping backward compatibility.

## Usage

```bash
envpatch alias .env --map DATABASE_URL:DB_URL
```

Multiple mappings can be specified:

```bash
envpatch alias .env --map DATABASE_URL:DB_URL --map PORT:APP_PORT
```

## Options

| Option | Description |
|---|---|
| `--map SOURCE:ALIAS` | Key alias mapping. Repeatable. |
| `--overwrite` | Overwrite alias key if it already exists. |
| `--output FILE` | Write result to a file instead of stdout. |
| `--summary` | Print aliased/skipped counts to stderr. |

## Example

Input `.env`:
```
DATABASE_URL=postgres://localhost/mydb
PORT=8080
```

Command:
```bash
envpatch alias .env --map DATABASE_URL:DB_URL --map PORT:APP_PORT
```

Output:
```
DATABASE_URL=postgres://localhost/mydb
PORT=8080
DB_URL=postgres://localhost/mydb
APP_PORT=8080
```

## Notes

- The original source key is always preserved.
- If the alias key already exists, it is skipped unless `--overwrite` is set.
- If the source key does not exist, it is silently skipped and counted in the skipped total.
