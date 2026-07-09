# BluePaper

**Animated Wallpaper Manager for Linux** — compatible with Wallpaper Engine wallpapers on Wayland, GNOME, KDE Plasma, Sway, Hyprland, and more.

> Designed for users migrating from Windows to Linux who want to keep using their Wallpaper Engine Workshop wallpapers (Steam App ID: **431960**).

---

# Features

- 🖥️ **Native Wayland support** via `mpvpaper`
- 📂 **Automatic detection** of your Steam Workshop wallpapers
- 🎨 **Wallpaper preview** with title and description
- 🔇 **Audio control** (mute/unmute)
- 💾 **Remembers** your last selected wallpaper
- ⚙️ **Customizable Workshop directory**
- 🎬 Supports `.mp4`, `.gif`, `.webm`, and `.avi`

---

# Quick Installation

```bash
sudo bash install.sh
```

## System Requirements

| Component | Package | Notes |
|-----------|---------|-------|
| Python 3 | `python3` | Included by default on Ubuntu |
| GTK Bindings | `python3-gi gir1.2-gtk-3.0` | Installed automatically |
| Media Player | `mpv` | `sudo apt install mpv` |
| **Native Wayland backend** | `mpvpaper` | Recommended (see below) |

## Installing mpvpaper (Recommended for Wayland)

```bash
# Ubuntu 24.04 / 26.04 — Build from source
sudo apt install -y cmake libmpv-dev libwayland-dev wayland-protocols
git clone https://github.com/GhostNaN/mpvpaper
cd mpvpaper
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
sudo cmake --install build
```

---

# Usage

```bash
# Launch the graphical interface
bluepaper

# Or search for "BluePaper" in your application menu
```

## First Launch

1. Open **BluePaper**
2. Your Wallpaper Engine Workshop wallpapers should be detected automatically.
3. Select a wallpaper and click **"▶ Set as Wallpaper"**.
4. If your Workshop folder is located elsewhere, open **Settings** and update the path.

---

# Steam Workshop Directory

Default location:

```text
~/.local/share/Steam/steamapps/workshop/content/431960/
```

Expected folder structure:

```text
431960/
├── 123456789/          ← Wallpaper ID
│   ├── video.mp4
│   ├── project.json
│   └── scene.pkg
├── 987654321/
│   ├── animation.gif
│   ├── project.json
│   └── scene.pkg
```

---

# Playback Backends

BluePaper automatically tries the following backends in order:

1. **mpvpaper** — Native Wayland layer-shell support (recommended)
2. **swww** — Ideal for GIF wallpapers on Sway and Hyprland
3. **mpv** — Embedded/window playback fallback

---

# Uninstall

```bash
sudo bash uninstall.sh
```

---

# Compatibility

| Desktop Environment | Status | Notes |
|---------------------|--------|-------|
| GNOME + Wayland | ✅ | Using mpvpaper |
| KDE Plasma + Wayland | ✅ | Using mpvpaper |
| Sway | ✅ | Using mpvpaper or swww |
| Hyprland | ✅ | Using mpvpaper or swww |
| GNOME + X11 | ✅ | Using mpv or xwinwrap |
| Ubuntu 24.04 LTS | ✅ | Tested |
| Ubuntu 26.04 LTS | ✅ | Supported |

---

# License

This project is licensed under the **MIT License**.

You are free to use, modify, distribute, and even use this software commercially, provided that the original copyright notice and license are included.
