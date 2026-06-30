"""Android app runtime (Waydroid / LXC container)."""
from __future__ import annotations

from .base import RunResult, Runtime


class AndroidRuntime(Runtime):
    platform = "android"
    required_tool = "waydroid"

    def launch(self, command: str) -> RunResult:
        return self._execute(command)

    def launch_package(self, package: str) -> RunResult:
        return self._execute(f"waydroid app launch {package}")
