from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envpatch.parser import parse_env_string
from envpatch.merger import merge_envs


@dataclass
class CloneResult:
    env: Dict[str, str]
    copied_count: int
    overwritten_count: int
    skipped_count: int
    remapped: Dict[str, str] = field(default_factory=dict)

    def to_summary(self) -> str:
        lines = [
            f"Copied:      {self.copied_count}",
            f"Overwritten: {self.overwritten_count}",
            f"Skipped:     {self.skipped_count}",
        ]
        if self.remapped:
            lines.append("Remapped keys:")
            for old, new in self.remapped.items():
                lines.append(f"  {old} -> {new}")
        return "\n".join(lines)


def clone_env(
    source: str,
    target: str,
    keys: Optional[List[str]] = None,
    remap: Optional[Dict[str, str]] = None,
    overwrite: bool = False,
) -> CloneResult:
    """Clone selected keys from source env into target env.

    Args:
        source: raw .env string to copy from
        target: raw .env string to copy into
        keys: if provided, only these keys are cloned
        remap: mapping of {source_key: target_key} renames during clone
        overwrite: whether to overwrite existing keys in target
    """
    src = parse_env_string(source)
    tgt = parse_env_string(target)
    remap = remap or {}

    subset = {k: v for k, v in src.items() if keys is None or k in keys}

    remapped: Dict[str, str] = {}
    patch: Dict[str, str] = {}
    for k, v in subset.items():
        dest_key = remap.get(k, k)
        if k != dest_key:
            remapped[k] = dest_key
        patch[dest_key] = v

    copied = 0
    overwritten = 0
    skipped = 0
    result_env = dict(tgt)

    for dest_key, val in patch.items():
        if dest_key in tgt:
            if overwrite:
                result_env[dest_key] = val
                overwritten += 1
            else:
                skipped += 1
        else:
            result_env[dest_key] = val
            copied += 1

    return CloneResult(
        env=result_env,
        copied_count=copied,
        overwritten_count=overwritten,
        skipped_count=skipped,
        remapped=remapped,
    )
