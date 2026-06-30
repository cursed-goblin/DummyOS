"""Base runtime abstraction shared by every platform runtime."""
from __future__ import annotations

import shlex
import shutil
import subprocess
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RunResult:
    success: bool
    message: str
    dry_run: bool = False
    returncode: Optional[int] = None


class Runtime:
    """A platform runtime knows how to launch an app's command.

    Runtimes shell out to real tools when present; otherwise they fall back to a
    safe ``dry_run`` so the platform is testable on any machine.
    """

    platform: str = "base"
    #: Tool that must be on PATH for non-dry-run execution.
    required_tool: Optional[str] = None

    def available(self) -> bool:
        if self.required_tool is None:
            return True
        return shutil.which(self.required_tool) is not None

    def _execute(self, command: str) -> RunResult:
        if not self.available():
            return RunResult(
                success=True,
                message=f"[dry-run] would run: {command}",
                dry_run=True,
            )
        try:
            proc = subprocess.run(
                shlex.split(command),
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:  # pragma: no cover - defensive
            return RunResult(success=False, message=str(exc))
        ok = proc.returncode == 0
        msg = proc.stdout.strip() or proc.stderr.strip() or f"exit {proc.returncode}"
        return RunResult(success=ok, message=msg, returncode=proc.returncode)

    def launch(self, command: str) -> RunResult:
        raise NotImplementedError
