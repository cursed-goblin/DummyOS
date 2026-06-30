"""Tools the model can call. The model never runs commands directly."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from ..registry import AppRegistry
from ..runtimes.manager import RuntimeManager
from ..system.controls import SystemControls


@dataclass
class ToolResult:
    success: bool
    message: str


@dataclass
class Tool:
    name: str
    description: str
    handler: Callable[..., ToolResult]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def names(self) -> List[str]:
        return sorted(self._tools)

    def specs(self) -> List[Dict[str, str]]:
        return [
            {"name": t.name, "description": t.description}
            for t in self._tools.values()
        ]


def default_tools(
    registry: AppRegistry,
    runtimes: RuntimeManager,
    controls: SystemControls,
) -> ToolRegistry:
    tools = ToolRegistry()

    def open_app(name: str) -> ToolResult:
        app = registry.get(name)
        if app is None:
            return ToolResult(False, f"App {name!r} is not registered")
        res = runtimes.launch(app)
        return ToolResult(res.success, res.message)

    def search_files(query: str, root: str = ".") -> ToolResult:
        hits = controls.search_files(query, root=root)
        return ToolResult(True, "\n".join(hits) if hits else "No matches")

    def set_brightness(value: int) -> ToolResult:
        r = controls.set_brightness(int(value))
        return ToolResult(r.success, r.message)

    def set_volume(value: int) -> ToolResult:
        r = controls.set_volume(int(value))
        return ToolResult(r.success, r.message)

    tools.register(Tool("open_app", "Open an installed app", open_app))
    tools.register(Tool("search_files", "Search files in a directory", search_files))
    tools.register(Tool("set_brightness", "Set screen brightness (0-100)", set_brightness))
    tools.register(Tool("set_volume", "Set audio volume (0-100)", set_volume))
    return tools
