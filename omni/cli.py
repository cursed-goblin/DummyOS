"""The `omni` command-line interface."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .config import load_config, save_config
from .registry import App, AppRegistry
from .runtimes.manager import RuntimeManager
from .agent.agent import Agent
from .agent.backends import get_backend
from .agent.permissions import PermissionManager


def _cli_confirm(message: str) -> bool:
    try:
        return input(f"{message} [y/N] ").strip().lower() in ("y", "yes")
    except EOFError:
        return False


def _build_agent() -> Agent:
    config = load_config()
    perm = PermissionManager(config.get("permission_level", 2))
    model_name = config.get("active_model", "echo")
    model_cfg = config.get("models", {}).get(model_name, {"backend": "echo"})
    backend = get_backend(model_cfg.get("backend", "echo"))
    if model_cfg.get("model_path"):
        try:
            backend.load_model(model_cfg["model_path"], model_cfg.get("context_length", 4096))
        except Exception as exc:  # noqa: BLE001 - report and continue with echo
            print(f"warning: could not load model {model_name}: {exc}", file=sys.stderr)
    return Agent(permissions=perm, backend=backend, confirm=_cli_confirm)


def cmd_app(args: argparse.Namespace) -> int:
    reg = AppRegistry()
    if args.app_cmd == "add":
        reg.add(App(name=args.name, platform=args.platform, command=args.command))
        print(f"Added {args.name} ({args.platform})")
    elif args.app_cmd == "remove":
        print("Removed" if reg.remove(args.name) else "Not found")
    elif args.app_cmd == "list":
        apps = reg.list()
        if not apps:
            print("No apps registered. Try `omni app add ...`")
        for a in apps:
            print(f"{a.name:20} {a.platform:8} {a.command}")
    return 0


def cmd_launch(args: argparse.Namespace) -> int:
    reg = AppRegistry()
    app = reg.get(args.name)
    if app is None:
        print(f"App {args.name!r} not found", file=sys.stderr)
        return 1
    result = RuntimeManager().launch(app)
    print(result.message)
    return 0 if result.success else 1


def cmd_agent(args: argparse.Namespace) -> int:
    agent = _build_agent()
    if args.agent_cmd == "chat":
        message = " ".join(args.message)
        response = agent.chat(message)
        print(response.text)
    return 0


def cmd_model(args: argparse.Namespace) -> int:
    config = load_config()
    models = config.setdefault("models", {})
    if args.model_cmd == "list":
        active = config.get("active_model")
        for name, cfg in models.items():
            marker = "*" if name == active else " "
            print(f"{marker} {name:24} backend={cfg.get('backend')}")
    elif args.model_cmd == "use":
        if args.name not in models:
            print(f"Unknown model {args.name!r}", file=sys.stderr)
            return 1
        config["active_model"] = args.name
        save_config(config)
        print(f"Active model set to {args.name}")
    return 0


def cmd_daemon(args: argparse.Namespace) -> int:
    from .daemon.server import build_server

    server = build_server(args.host, args.port)
    print(f"omnid listening on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="omni", description="OmniOS AI control CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    app = sub.add_parser("app", help="Manage the app registry")
    app_sub = app.add_subparsers(dest="app_cmd", required=True)
    add = app_sub.add_parser("add", help="Register an app")
    add.add_argument("name")
    add.add_argument("--platform", required=True, choices=["linux", "windows", "android"])
    add.add_argument("--command", required=True)
    rm = app_sub.add_parser("remove", help="Remove an app")
    rm.add_argument("name")
    app_sub.add_parser("list", help="List apps")
    app.set_defaults(func=cmd_app)

    launch = sub.add_parser("launch", help="Launch a registered app")
    launch.add_argument("name")
    launch.set_defaults(func=cmd_launch)

    agent = sub.add_parser("agent", help="Talk to the AI agent")
    agent_sub = agent.add_subparsers(dest="agent_cmd", required=True)
    chat = agent_sub.add_parser("chat", help="Send a message to the agent")
    chat.add_argument("message", nargs="+")
    agent.set_defaults(func=cmd_agent)

    model = sub.add_parser("model", help="Manage local models")
    model_sub = model.add_subparsers(dest="model_cmd", required=True)
    model_sub.add_parser("list", help="List configured models")
    use = model_sub.add_parser("use", help="Set the active model")
    use.add_argument("name")
    model.set_defaults(func=cmd_model)

    daemon = sub.add_parser("daemon", help="Run the local control daemon (omnid)")
    daemon.add_argument("--host", default="127.0.0.1")
    daemon.add_argument("--port", type=int, default=8765)
    daemon.set_defaults(func=cmd_daemon)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
