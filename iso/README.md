# Building the OmniOS AI bootable ISO

This directory builds a bootable **live ISO** using [Debian live-build](https://wiki.debian.org/DebianLive). The image boots into a Wayland (sway) desktop with the OmniOS app runtimes and the `omni` CLI preinstalled.

## Through GitHub (recommended)

The ISO is built automatically by GitHub Actions:

- On every push to `main` that touches `iso/` or `omni/`
- Manually via the **Actions → Build ISO → Run workflow** button (`workflow_dispatch`)
- On every published GitHub Release (the ISO is attached to the release)

The built ISO is uploaded as the `omnios-ai-iso` workflow artifact and can be downloaded from the run summary page.

## Locally

```bash
sudo iso/build-iso.sh
# -> dist/omnios-ai-bookworm-amd64.iso
```

Requirements: a Debian/Ubuntu host (or container) with `sudo` and internet access. The script installs `live-build` for you.

## What's in the image

| Component | Package(s) |
|-----------|------------|
| Desktop | `sway`, `xwayland`, `foot`, `pipewire`, `wireplumber` |
| Networking | `network-manager` |
| Linux apps | `flatpak` (+ Flathub remote) |
| Windows apps | `wine`, `wine64` (Proton can be layered later) |
| Windows VM fallback | `qemu-system-x86`, `qemu-utils` |
| AI / tooling | `python3`, `pip`, `git`, the `omni` CLI |

> Android (Waydroid) requires kernel modules (`binder`, `ashmem`) that are configured at first boot rather than baked into the live image.

## Try the ISO

```bash
qemu-system-x86_64 -m 4096 -enable-kvm -cdrom dist/omnios-ai-bookworm-amd64.iso
```
