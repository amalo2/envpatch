"""Parser for .env files — handles reading and parsing key-value pairs."""

from typing import Dict, Optional
import re

ENV_LINE_RE = re.compile(
    r'^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)\s*$'
)
COMMENT_RE = re.compile(r'^\s*#')


def parse_env_string(content: str) -> Dict[str, str]:
    """Parse a .env file string into a dict of key-value pairs.

    - Strips inline comments only when the value is unquoted.
    - Preserves quoted values (single or double quotes) verbatim (without quotes).
    - Skips blank lines and comment lines.
    """
    result: Dict[str, str] = {}
    for line in content.splitlines():
        if not line.strip() or COMMENT_RE.match(line):
            continue
        match = ENV_LINE_RE.match(line)
        if not match:
            continue
        key = match.group('key')
        raw_value = match.group('value')
        result[key] = _parse_value(raw_value)
    return result


def parse_env_file(path: str) -> Dict[str, str]:
    """Read a .env file from *path* and return its parsed key-value pairs."""
    with open(path, 'r', encoding='utf-8') as fh:
        return parse_env_string(fh.read())


def _parse_value(raw: str) -> str:
    """Resolve the final string value from a raw .env value token."""
    raw = raw.strip()
    if not raw:
        return ''
    # Double-quoted value
    if raw.startswith('"') and raw.endswith('"') and len(raw) >= 2:
        return raw[1:-1]
    # Single-quoted value
    if raw.startswith("'") and raw.endswith("'") and len(raw) >= 2:
        return raw[1:-1]
    # Unquoted — strip trailing inline comment
    comment_pos = raw.find(' #')
    if comment_pos != -1:
        raw = raw[:comment_pos]
    return raw.strip()
