"""Unified cross-platform app registry.

Apps from Linux, Windows, and Android are all treated as first-class apps and
stored in a single registry file (``~/.omni/apps.json``).
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .config import REGISTRY_PATH, ensure_home

VALID_PLATFORMS = ("linux", "windows", "android")


@dataclass
class App:
    name: str
    platform: str
    command: str

    def __post_init__(self) -> None:
        if self.platform not in VALID_PLATFORMS:
            raise ValueError(
                f"Unknown platform {self.platform!r}; expected one of {VALID_PLATFORMS}"
            )


class AppRegistry:
    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or REGISTRY_PATH
        self._apps: Dict[str, App] = {}
        self.load()

    def load(self) -> None:
        self._apps = {}
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            for entry in data.get("apps", []):
                app = App(**entry)
                self._apps[app.name.lower()] = app

    def save(self) -> None:
        ensure_home()
        data = {"apps": [asdict(a) for a in self._apps.values()]}
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    def add(self, app: App) -> App:
        self._apps[app.name.lower()] = app
        self.save()
        return app

    def remove(self, name: str) -> bool:
        existed = self._apps.pop(name.lower(), None) is not None
        if existed:
            self.save()
        return existed

    def get(self, name: str) -> Optional[App]:
        return self._apps.get(name.lower())

    def list(self) -> List[App]:
        return sorted(self._apps.values(), key=lambda a: a.name.lower())
