"""Configuration and state directory management for OmniOS AI."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

OMNI_HOME = Path(os.environ.get("OMNI_HOME", Path.home() / ".omni"))
CONFIG_PATH = OMNI_HOME / "config.json"
REGISTRY_PATH = OMNI_HOME / "apps.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "active_model": "echo",
    "permission_level": 2,
    "models": {
        "echo": {"backend": "echo"},
    },
}


def ensure_home() -> Path:
    OMNI_HOME.mkdir(parents=True, exist_ok=True)
    return OMNI_HOME


def load_config() -> Dict[str, Any]:
    ensure_home()
    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)
    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save_config(config: Dict[str, Any]) -> None:
    ensure_home()
    with CONFIG_PATH.open("w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)
