from dataclasses import dataclass, field
from typing import Dict, List
from envpatch.parser import parse_env_string


@dataclass
class TagResult:
    tagged: Dict[str, List[str]] = field(default_factory=dict)
    env: Dict[str, str] = field(default_factory=dict)

    @property
    def tag_count(self) -> int:
        return len(self.tagged)

    @property
    def untagged_count(self) -> int:
        return sum(1 for k in self.env if k not in self.tagged)

    def to_summary(self) -> str:
        lines = [f"Tagged: {self.tag_count} key(s), Untagged: {self.untagged_count} key(s)"]
        for key, tags in sorted(self.tagged.items()):
            lines.append(f"  {key}: {', '.join(tags)}")
        return "\n".join(lines)


def _infer_tags(key: str, value: str) -> List[str]:
    tags: List[str] = []
    lower = key.lower()
    if any(p in lower for p in ("secret", "password", "passwd", "token", "api_key", "private")):
        tags.append("sensitive")
    if any(p in lower for p in ("db", "database", "postgres", "mysql", "mongo")):
        tags.append("database")
    if any(p in lower for p in ("aws", "gcp", "azure", "cloud")):
        tags.append("cloud")
    if any(p in lower for p in ("url", "host", "port", "endpoint")):
        tags.append("network")
    if value == "":
        tags.append("empty")
    if not tags:
        tags.append("general")
    return tags


def tag_env(env_string: str, extra_tags: Dict[str, List[str]] = None) -> TagResult:
    env = parse_env_string(env_string)
    tagged: Dict[str, List[str]] = {}

    for key, value in env.items():
        inferred = _infer_tags(key, value)
        manual = (extra_tags or {}).get(key, [])
        merged = list(dict.fromkeys(inferred + manual))
        tagged[key] = merged

    return TagResult(tagged=tagged, env=env)


def filter_by_tag(result: TagResult, tag: str) -> Dict[str, str]:
    return {
        key: result.env[key]
        for key, tags in result.tagged.items()
        if tag in tags
    }
