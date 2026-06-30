"""The agent loop: parse intent, plan tool calls, check permissions, execute.

The planner here is a small, deterministic intent parser so the scaffold works
without a real model loaded. When a real backend is configured it is used to
generate richer responses; tool routing still goes through the permission layer.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

from ..registry import AppRegistry
from ..runtimes.manager import RuntimeManager
from ..system.controls import SystemControls
from .backends import ModelBackend, EchoBackend
from .permissions import PermissionManager
from .tools import ToolRegistry, ToolResult, default_tools

# (tool_name, kwargs)
PlannedCall = Tuple[str, dict]


@dataclass
class AgentResponse:
    text: str
    actions: List[str] = field(default_factory=list)


class Agent:
    def __init__(
        self,
        registry: Optional[AppRegistry] = None,
        runtimes: Optional[RuntimeManager] = None,
        controls: Optional[SystemControls] = None,
        permissions: Optional[PermissionManager] = None,
        backend: Optional[ModelBackend] = None,
        confirm: Optional[Callable[[str], bool]] = None,
    ) -> None:
        self.registry = registry or AppRegistry()
        self.runtimes = runtimes or RuntimeManager()
        self.controls = controls or SystemControls()
        self.permissions = permissions or PermissionManager()
        self.backend = backend or EchoBackend()
        self.tools = default_tools(self.registry, self.runtimes, self.controls)
        # Default confirmation callback denies; CLI overrides with a prompt.
        self.confirm = confirm or (lambda _msg: False)

    # --- intent parsing -------------------------------------------------
    def plan(self, message: str) -> List[PlannedCall]:
        calls: List[PlannedCall] = []
        lowered = message.lower()

        m = re.search(r"brightness (?:to )?(\d{1,3})", lowered)
        if m:
            calls.append(("set_brightness", {"value": int(m.group(1))}))

        m = re.search(r"volume (?:to )?(\d{1,3})", lowered)
        if m:
            calls.append(("set_volume", {"value": int(m.group(1))}))

        for app in self.registry.list():
            if re.search(r"\bopen\b.*\b" + re.escape(app.name.lower()) + r"\b", lowered):
                calls.append(("open_app", {"name": app.name}))

        m = re.search(r"(?:search|find)(?: for)? (?:files? )?(?:named |called )?([\w.\-]+)", lowered)
        if m and "open" not in lowered:
            calls.append(("search_files", {"query": m.group(1)}))
        return calls

    # --- execution ------------------------------------------------------
    def run_tool(self, name: str, **kwargs) -> ToolResult:
        if not self.permissions.allows(name):
            return ToolResult(False, f"Permission denied for {name}")
        if self.permissions.needs_confirmation(name):
            if not self.confirm(f"Allow {name}({kwargs})?"):
                return ToolResult(False, f"User declined {name}")
        tool = self.tools.get(name)
        if tool is None:
            return ToolResult(False, f"Unknown tool {name}")
        return tool.handler(**kwargs)

    def chat(self, message: str) -> AgentResponse:
        calls = self.plan(message)
        actions: List[str] = []
        for name, kwargs in calls:
            result = self.run_tool(name, **kwargs)
            status = "ok" if result.success else "failed"
            actions.append(f"{name}({kwargs}) -> {status}: {result.message}")
        if calls:
            text = "Done. " + "; ".join(actions)
        else:
            text = self.backend.generate(message)
        return AgentResponse(text=text, actions=actions)
