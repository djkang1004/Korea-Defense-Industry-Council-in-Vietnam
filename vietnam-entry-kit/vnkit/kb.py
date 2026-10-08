"""지식베이스(kb/*.yaml) 로더."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

KIT_ROOT = Path(__file__).resolve().parent.parent
KB_DIR = KIT_ROOT / "kb"


@lru_cache(maxsize=None)
def load(name: str) -> dict:
    path = KB_DIR / f"{name}.yaml"
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def entity_options() -> list[dict]:
    return load("entity_types")["options"]


def sectors() -> list[dict]:
    return load("sector_profiles")["sectors"]


def common_rules() -> list[dict]:
    return load("common_rules")["rules"]


def modules() -> list[dict]:
    return load("research_modules")["modules"]


def team() -> dict:
    return load("team")
