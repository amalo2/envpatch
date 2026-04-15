"""Apply a DiffResult (or a target env dict) to a base env dict.

The patcher intentionally does NOT overwrite existing keys unless
``overwrite=True`` is passed — this is the core safety guarantee of envpatch.
"""

from typing import Dict, Optional
from envpatch.differ import DiffResult, diff_envs


def apply_patch(
    base: Dict[str, str],
    patch: Dict[str, str],
    overwrite: bool = False,
    remove_missing: bool = False,
) -> Dict[str, str]:
    """Merge *patch* into *base* and return the resulting env dict.

    Args:
        base: The existing env mapping (will not be mutated).
        patch: The desired / incoming env mapping.
        overwrite: When True, modified keys in *patch* replace those in *base*.
                   When False (default), existing keys are left untouched.
        remove_missing: When True, keys present in *base* but absent from *patch*
                        are removed from the result.

    Returns:
        A new dict representing the patched environment.
    """
    result = dict(base)
    diff = diff_envs(base, patch)

    for change in diff.added:
        result[change.key] = change.new_value  # type: ignore[assignment]

    if overwrite:
        for change in diff.modified:
            result[change.key] = change.new_value  # type: ignore[assignment]

    if remove_missing:
        for change in diff.removed:
            result.pop(change.key, None)

    return result


def apply_patch_from_diff(
    base: Dict[str, str],
    diff: DiffResult,
    overwrite: bool = False,
    remove_missing: bool = False,
) -> Dict[str, str]:
    """Apply a pre-computed :class:`DiffResult` to *base*.

    Useful when you already hold a diff object and want to avoid recomputing it.
    """
    result = dict(base)

    for change in diff.added:
        result[change.key] = change.new_value  # type: ignore[assignment]

    if overwrite:
        for change in diff.modified:
            result[change.key] = change.new_value  # type: ignore[assignment]

    if remove_missing:
        for change in diff.removed:
            result.pop(change.key, None)

    return result


def serialize_env(env: Dict[str, str]) -> str:
    """Serialize an env dict back to .env file format.

    Values containing spaces or special characters are double-quoted.
    """
    lines = []
    for key in sorted(env):
        value = env[key]
        needs_quoting = any(ch in value for ch in (" ", "\t", "#", "'", '"', "="))
        if needs_quoting:
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")
