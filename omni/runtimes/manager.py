"""Routes apps to the correct runtime based on their platform."""
from __future__ import annotations

from typing import Dict

from ..registry import App
from .android import AndroidRuntime
from .base import RunResult, Runtime
from .linux import LinuxRuntime
from .windows import WindowsRuntime


class RuntimeManager:
    def __init__(self) -> None:
        self._runtimes: Dict[str, Runtime] = {
            "linux": LinuxRuntime(),
            "windows": WindowsRuntime(),
            "android": AndroidRuntime(),
        }

    def runtime_for(self, platform: str) -> Runtime:
        try:
            return self._runtimes[platform]
        except KeyError as exc:
            raise ValueError(f"No runtime for platform {platform!r}") from exc

    def launch(self, app: App) -> RunResult:
        return self.runtime_for(app.platform).launch(app.command)
