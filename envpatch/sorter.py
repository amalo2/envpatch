"""Sort .env file keys alphabetically or by custom group order."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SortResult:
    sorted_env: Dict[str, str]
    original_order: List[str]
    sorted_order: List[str]
    groups_applied: bool = False

    @property
    def changed(self) -> bool:
        return self.original_order != self.sorted_order

    def to_summary(self) -> str:
        if not self.changed:
            return "Keys already in sorted order."
        return (
            f"Sorted {len(self.sorted_order)} keys"
            + (" using group order." if self.groups_applied else " alphabetically.")
        )


def sort_env(
    env: Dict[str, str],
    groups: Optional[List[List[str]]] = None,
) -> SortResult:
    """Sort env keys. If groups provided, keys are ordered by group then alphabetically."""
    original_order = list(env.keys())

    if groups:
        group_index: Dict[str, int] = {}
        for priority, group in enumerate(groups):
            for key in group:
                group_index[key] = priority
        ungrouped_priority = len(groups)

        def group_key(k: str):
            return (group_index.get(k, ungrouped_priority), k)

        sorted_keys = sorted(env.keys(), key=group_key)
        groups_applied = True
    else:
        sorted_keys = sorted(env.keys())
        groups_applied = False

    sorted_env = {k: env[k] for k in sorted_keys}

    return SortResult(
        sorted_env=sorted_env,
        original_order=original_order,
        sorted_order=sorted_keys,
        groups_applied=groups_applied,
    )
