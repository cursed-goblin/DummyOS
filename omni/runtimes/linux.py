"""Linux app runtime (Flatpak / AppImage / native)."""
from __future__ import annotations

from .base import RunResult, Runtime


class LinuxRuntime(Runtime):
    platform = "linux"
    # Most registered Linux apps use flatpak; native commands run regardless.
    required_tool = None

    def launch(self, command: str) -> RunResult:
        return self._execute(command)
