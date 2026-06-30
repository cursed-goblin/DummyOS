# OmniOS AI — Architecture

OmniOS AI is **not** a from-scratch kernel. It is a platform layered on top of a
standard Linux base (Debian, Ubuntu, Fedora Silverblue, or Arch). The Linux
kernel gives us drivers, GPU support, filesystems, networking, security modules,
and container support for free.

## Layers

1. **Linux Kernel** — base kernel 6.x, drivers, GPU, filesystems, containers.
2. **OS Services** — D-Bus, portals, package manager, updates, audio (PipeWire),
   display (Wayland), security (Polkit, AppArmor/SELinux).
3. **App Runtime Layer** — three runtimes behind one interface:
   - Linux: Flatpak / AppImage / native packages
   - Windows: Wine/Proton (DXVK, VKD3D, Winetricks), KVM/QEMU VM fallback
   - Android: Waydroid / LXC containers
4. **AI Agent Control Layer** — intent parsing, command routing, a permission
   model, a pluggable local LLM runtime, a tool executor, and memory.
5. **Desktop UI** — launcher, app switcher, settings, and the agent surface.

## Code map

| Path | Responsibility |
|------|----------------|
| `omni/cli.py` | `omni` command-line entry point |
| `omni/config.py` | Config + state directory (`~/.omni`) |
| `omni/registry.py` | Unified cross-platform app registry |
| `omni/runtimes/` | `linux`, `windows`, `android` runtimes + `manager` |
| `omni/system/controls.py` | Brightness, volume, file search helpers |
| `omni/agent/permissions.py` | Permission levels 0–5 |
| `omni/agent/tools.py` | Tool definitions the model can call |
| `omni/agent/backends.py` | `ModelBackend` interface + implementations |
| `omni/agent/agent.py` | Intent parsing + tool execution loop |
| `omni/daemon/server.py` | `omnid` localhost HTTP control API |

## Permission model

| Level | Capability |
|-------|------------|
| 0 | Chat only |
| 1 | Read system info |
| 2 | Open apps and files |
| 3 | Modify user files (with confirmation) |
| 4 | Run shell commands (with confirmation) |
| 5 | Admin commands (always require password) |

The model never executes commands directly. It emits tool calls, the executor
checks the required permission, asks for confirmation when needed, and only then
runs the action.

## Dry-run safety

Every runtime checks whether the underlying tool (`flatpak`, `wine`, `waydroid`,
`wpctl`, `brightnessctl`, ...) is installed. When it is not, the action runs in
**dry-run** mode and returns what *would* have been executed. This keeps the
scaffold testable on any machine and CI.
