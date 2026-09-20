from __future__ import annotations


def normalize_label(value: str) -> str:
    """Normalize a non-empty label to lowercase kebab-case."""
    stripped = value.strip()
    if not stripped:
        raise ValueError("label must not be empty")
    return stripped.lower().replace(" ", "-")
