"""Permission model for the AI agent (levels 0-5)."""
from __future__ import annotations

from enum import IntEnum


class Permission(IntEnum):
    CHAT_ONLY = 0
    READ_SYSTEM = 1
    OPEN_APPS_FILES = 2
    MODIFY_FILES_CONFIRM = 3
    RUN_SHELL_CONFIRM = 4
    ADMIN = 5


#: Each tool declares the minimum permission level it needs.
TOOL_REQUIREMENTS = {
    "open_app": Permission.OPEN_APPS_FILES,
    "list_files": Permission.READ_SYSTEM,
    "search_files": Permission.READ_SYSTEM,
    "move_file": Permission.MODIFY_FILES_CONFIRM,
    "change_setting": Permission.OPEN_APPS_FILES,
    "set_brightness": Permission.OPEN_APPS_FILES,
    "set_volume": Permission.OPEN_APPS_FILES,
    "run_shell_command": Permission.RUN_SHELL_CONFIRM,
}

#: Tools that always require explicit user confirmation before running.
CONFIRM_TOOLS = {"move_file", "run_shell_command", "change_setting"}


class PermissionManager:
    def __init__(self, level: int = Permission.OPEN_APPS_FILES) -> None:
        self.level = Permission(level)

    def allows(self, tool_name: str) -> bool:
        required = TOOL_REQUIREMENTS.get(tool_name, Permission.ADMIN)
        return self.level >= required

    def needs_confirmation(self, tool_name: str) -> bool:
        return tool_name in CONFIRM_TOOLS
