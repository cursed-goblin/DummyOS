"""Basic OS controls: brightness, volume, and file search.

Each control shells out to a standard Linux tool when present and otherwise
returns a safe dry-run result.
"""
from __future__ import annotations

import shlex
import shutil
import subprocess
from pathlib import Path
from typing import List

from ..runtimes.base import RunResult


class SystemControls:
    def _run(self, command: str) -> RunResult:
        tool = shlex.split(command)[0]
        if shutil.which(tool) is None:
            return RunResult(True, f"[dry-run] would run: {command}", dry_run=True)
        proc = subprocess.run(shlex.split(command), capture_output=True, text=True)
        ok = proc.returncode == 0
        return RunResult(ok, proc.stderr.strip() or "ok", returncode=proc.returncode)

    def set_brightness(self, percent: int) -> RunResult:
        if not 0 <= percent <= 100:
            return RunResult(False, "Brightness must be between 0 and 100")
        return self._run(f"brightnessctl set {percent}%")

    def set_volume(self, percent: int) -> RunResult:
        if not 0 <= percent <= 100:
            return RunResult(False, "Volume must be between 0 and 100")
        return self._run(
            f"wpctl set-volume @DEFAULT_AUDIO_SINK@ {percent}%"
        )

    def search_files(self, query: str, root: str = ".", limit: int = 50) -> List[str]:
        matches: List[str] = []
        base = Path(root).expanduser()
        for path in base.rglob("*"):
            if query.lower() in path.name.lower():
                matches.append(str(path))
                if len(matches) >= limit:
                    break
        return matches
