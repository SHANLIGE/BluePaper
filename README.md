# BluePaper 🎞️

**Animated Wallpaper Manager for Linux** — compatible with Wayland, GNOME, KDE, Sway, Hyprland y más.

> Compatible con wallpapers de Steam Workshop (App ID: 431960 — Wallpaper Engine)

---

## Características

- 🖥️ **Soporte Wayland nativo** vía `mpvpaper`
- 📂 **Carga automática** de tus wallpapers de Steam Workshop
- 🎨 **Vista previa** de cada wallpaper con su título y descripción
- 🔇 **Control de audio** (silenciar/activar)
- 💾 **Recuerda** el último wallpaper activo
- ⚙️ **Ruta personalizable** del workshop
- 🎬 Soporta `.mp4`, `.gif`, `.webm`, `.avi`

---

## Instalación rápida

```bash
sudo bash install.sh
```

### Requisitos del sistema

| Componente | Paquete | Notas |
|-----------|---------|-------|
| Python 3 | `python3` | Ya incluido en Ubuntu |
| GTK Bindings | `python3-gi gir1.2-gtk-3.0` | Auto-instalado |
| Reproductor | `mpv` | `sudo apt install mpv` |
| **Wayland nativo** | `mpvpaper` | Recomendado (ver abajo) |

### Instalar mpvpaper (recomendado para Wayland)

```bash
# Ubuntu 24.04/26.04 — compilar desde fuente:
sudo apt install -y cmake libmpv-dev libwayland-dev wayland-protocols
git clone https://github.com/GhostNaN/mpvpaper
cd mpvpaper
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
sudo cmake --install build
```

---

## Uso

```bash
# Abrir la interfaz gráfica
bluepaper

# O busca "BluePaper" en el menú de aplicaciones
```

### Primera vez

1. Abre **BluePaper**
2. Tus wallpapers del Workshop deberían aparecer automáticamente
3. Selecciona uno y haz clic en **"▶ Set as Wallpaper"**
4. Si la ruta es diferente, ve a **Settings** y ajústala

---

## Ruta del Workshop

Por defecto:
```
~/.local/share/Steam/steamapps/workshop/content/431960/
```

Estructura esperada:
```
431960/
├── 123456789/          ← ID del wallpaper
│   ├── video.mp4       ← archivo de medios
│   ├── project.json    ← metadatos (título, descripción)
│   └── scene.pkg
├── 987654321/
│   ├── animation.gif
│   ├── project.json
│   └── scene.pkg
```

---

## Backends de reproducción

BluePaper intenta los siguientes backends en orden:

1. **mpvpaper** — Wayland layer-shell nativo (mejor opción)
2. **swww** — para GIFs en Sway/Hyprland
3. **mpv** — modo ventana/embed

---

## Desinstalar

```bash
sudo bash uninstall.sh
```

---

## Compatibilidad

| Entorno | Estado | Notas |
|---------|--------|-------|
| GNOME + Wayland | ✅ | Con mpvpaper |
| KDE Plasma + Wayland | ✅ | Con mpvpaper |
| Sway | ✅ | Con mpvpaper o swww |
| Hyprland | ✅ | Con mpvpaper o swww |
| GNOME + X11 | ✅ | Con mpv o xwinwrap |
| Ubuntu 24.04 LTS | ✅ | Probado |
| Ubuntu 26.04 LTS | ✅ | Soportado |

---

## Licencia

MIT — libre para usar, modificar y distribuir.
