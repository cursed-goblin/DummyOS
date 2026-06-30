#!/usr/bin/env bash
#
# Build a bootable OmniOS AI live ISO using Debian live-build.
#
# The resulting image boots into a Wayland (sway) desktop with the OmniOS app
# runtimes (Flatpak, Wine, QEMU/KVM) and the `omni` CLI preinstalled.
#
# Usage:  sudo iso/build-iso.sh
# Output: dist/omnios-ai-<dist>-amd64.iso
#
set -euo pipefail

DIST="${OMNI_DIST:-bookworm}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKDIR="${REPO_ROOT}/iso/work"

echo "==> Installing live-build"
sudo apt-get update
sudo apt-get install -y live-build

echo "==> Configuring live-build (distribution: ${DIST})"
rm -rf "${WORKDIR}"
mkdir -p "${WORKDIR}"
cd "${WORKDIR}"

lb config \
  --distribution "${DIST}" \
  --architectures amd64 \
  --debian-installer none \
  --archive-areas "main contrib non-free non-free-firmware" \
  --iso-application "OmniOS AI" \
  --iso-volume "OmniOS-AI" \
  --bootappend-live "boot=live components quiet splash"

echo "==> Adding package lists"
mkdir -p config/package-lists
cat > config/package-lists/omnios.list.chroot <<'PKGS'
# Base Wayland desktop
xwayland
sway
seatd
foot
pipewire
wireplumber
network-manager
brightnessctl
# App runtimes
flatpak
wine
wine64
qemu-system-x86
qemu-utils
# AI / tooling
python3
python3-pip
python3-venv
git
ca-certificates
PKGS

echo "==> Bundling the OmniOS scaffold into the image"
mkdir -p config/includes.chroot/opt/omnios
cp -r "${REPO_ROOT}/omni" config/includes.chroot/opt/omnios/
cp "${REPO_ROOT}/pyproject.toml" config/includes.chroot/opt/omnios/
cp "${REPO_ROOT}/README.md" config/includes.chroot/opt/omnios/

echo "==> Adding install hook"
mkdir -p config/hooks/live
cat > config/hooks/live/0100-install-omnios.hook.chroot <<'HOOK'
#!/bin/sh
set -e
# Install the omni CLI system-wide inside the image.
pip3 install --break-system-packages /opt/omnios 2>/dev/null || pip3 install /opt/omnios
# Enable Flatpak's Flathub remote for Linux apps.
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo || true
HOOK
chmod +x config/hooks/live/0100-install-omnios.hook.chroot

echo "==> Building ISO (this can take a while)"
sudo lb build

mkdir -p "${REPO_ROOT}/dist"
ISO_OUT="${REPO_ROOT}/dist/omnios-ai-${DIST}-amd64.iso"
if ls live-image-amd64.hybrid.iso >/dev/null 2>&1; then
  mv live-image-amd64.hybrid.iso "${ISO_OUT}"
else
  mv ./*.iso "${ISO_OUT}"
fi

echo "==> ISO built: ${ISO_OUT}"
ls -lh "${ISO_OUT}"
