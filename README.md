# envpatch

> CLI tool to diff and apply `.env` file changes across environments without overwriting existing keys.

---

## Installation

```bash
pip install envpatch
```

Or with [pipx](https://pypa.github.io/pipx/):

```bash
pipx install envpatch
```

---

## Usage

**Diff two `.env` files:**

```bash
envpatch diff .env.example .env
```

**Apply new keys from a source file without overwriting existing values:**

```bash
envpatch apply .env.example .env
```

This will add any keys present in `.env.example` that are missing from `.env`, leaving your existing values untouched.

**Preview changes before applying:**

```bash
envpatch apply --dry-run .env.example .env
```

**Example output:**

```
+ NEW_FEATURE_FLAG=false   (added)
~ DATABASE_URL             (skipped, already set)
  SECRET_KEY               (skipped, already set)
```

---

## Why envpatch?

Keeping `.env` files in sync across team members and environments is error-prone. `envpatch` lets you safely propagate new configuration keys without risking accidental overwrites of secrets or environment-specific values.

---

## License

[MIT](LICENSE)