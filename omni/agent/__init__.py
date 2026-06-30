"""The OmniOS AI agent: permissions, tools, model backends, and the agent loop."""
from .permissions import Permission, PermissionManager
from .backends import ModelBackend, EchoBackend, LlamaCppBackend, get_backend
from .tools import ToolRegistry, ToolResult, default_tools
from .agent import Agent

__all__ = [
    "Permission",
    "PermissionManager",
    "ModelBackend",
    "EchoBackend",
    "LlamaCppBackend",
    "get_backend",
    "ToolRegistry",
    "ToolResult",
    "default_tools",
    "Agent",
]
