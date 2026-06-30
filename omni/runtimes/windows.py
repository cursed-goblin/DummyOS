"""Windows app runtime.

Strategy: try Wine/Proton first. If the app is known to be incompatible, the
caller can request the KVM/QEMU VM fallback.
"""
from __future__ import annotations

from .base import RunResult, Runtime


class WindowsRuntime(Runtime):
    platform = "windows"
    required_tool = "wine"

    def launch(self, command: str) -> RunResult:
        result = self._execute(command)
        if not result.success and not result.dry_run:
            result.message += (
                "\nWine launch failed. Consider the VM fallback: "
                "`omni run-windows <app> --vm` (KVM/QEMU + SPICE/Looking Glass)."
            )
        return result

    def launch_in_vm(self, app_path: str) -> RunResult:
        """Hook for the KVM/QEMU fallback path.

        A full implementation boots a Windows guest and forwards the app via
        SPICE or Looking Glass. Here we describe the intended command.
        """
        return RunResult(
            success=True,
            dry_run=True,
            message=(
                "[dry-run] would boot Windows guest via QEMU/KVM and run "
                f"{app_path} with GPU acceleration where available."
            ),
        )
