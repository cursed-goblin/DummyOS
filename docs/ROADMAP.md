# OmniOS AI — Roadmap

## MVP 1 — Linux-based OS image
Goal: a bootable Linux desktop.
- [ ] Base image (Debian Live Build / Fedora Kinoite / Arch ISO)
- [ ] Custom desktop session
- [ ] Custom app launcher
- [ ] Basic settings app
- Deliverables: bootable ISO, installer, desktop shell, package-manager wrapper

## MVP 2 — Unified app runtime
Goal: launch Linux, Windows, and Android apps.
- [x] App registry (`omni/registry.py`)
- [x] Unified launcher command (`omni launch`)
- [x] Linux runtime (Flatpak)
- [x] Windows runtime (Wine/Proton + VM fallback hook)
- [x] Android runtime (Waydroid)
- [ ] Install flows: `omni install linux|windows|android ...`

## MVP 3 — Local AI agent
Goal: AI can control basic OS actions.
- [x] Load a local model backend
- [x] Chat interface (`omni agent chat`)
- [x] Open apps, search files
- [x] Change brightness / volume
- [x] Run safe commands with confirmation

## MVP 4 — Model adaptation layer
Goal: users can switch models.
- [x] `ModelBackend` abstraction
- [ ] `omni model add /models/llama.gguf`
- [ ] `omni model add huggingface://mistralai/Mistral-7B-Instruct-v0.3`
- [x] `omni model use <name>`
- [x] `omni model list`
