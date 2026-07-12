#!/bin/bash
# BluePaper Installer for Ubuntu 24.04/26.04 LTS
set -e

INSTALL_PREFIX="/usr/local"
VERSION="1.0.0"
RED='\033[0;31m'; GREEN='\033[0;32m'; BLUE='\033[0;34m'
PURPLE='\033[0;35m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'
BOLD='\033[1m'; NC='\033[0m'

echo -e "${PURPLE}"
cat << 'BANNER'
  ██████╗ ██╗     ██╗   ██╗███████╗██████╗  █████╗ ██████╗ ███████╗██████╗ 
  ██╔══██╗██║     ██║   ██║██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
  ██████╔╝██║     ██║   ██║█████╗  ██████╔╝███████║██████╔╝█████╗  ██████╔╝
  ██╔══██╗██║     ██║   ██║██╔══╝  ██╔═══╝ ██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗
  ██████╔╝███████╗╚██████╔╝███████╗██║     ██║  ██║██║     ███████╗██║  ██║
  ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝
BANNER
echo -e "${NC}"
echo -e "${CYAN}  Animated Wallpaper Manager  •  Steam Workshop 431960  •  v${VERSION}${NC}"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}✗ Ejecuta como root: sudo bash install.sh${NC}"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BOLD}${BLUE}[1/5]${NC} Instalando dependencias..."
apt-get install -y -q \
    python3 python3-gi python3-gi-cairo \
    gir1.2-gtk-3.0 gir1.2-gdkpixbuf-2.0 \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-libav \
    gir1.2-gstreamer-1.0 \
    gir1.2-gst-plugins-base-1.0 \
    ffmpeg \
    x11-utils \
    2>/dev/null || true
echo -e "     ${GREEN}✓${NC} Dependencias instaladas"

echo ""
echo -e "${BOLD}${BLUE}[2/5]${NC} Instalando archivos de BluePaper..."

mkdir -p "${INSTALL_PREFIX}/lib/bluepaper"
mkdir -p "${INSTALL_PREFIX}/share/applications"
mkdir -p "${INSTALL_PREFIX}/share/icons/hicolor/256x256/apps"
mkdir -p "${INSTALL_PREFIX}/share/icons/hicolor/128x128/apps"
mkdir -p "${INSTALL_PREFIX}/share/icons/hicolor/64x64/apps"
mkdir -p "${INSTALL_PREFIX}/bin"

# Copiar bluepaper.py Y renderer.py
cp "${SCRIPT_DIR}/src/bluepaper.py" "${INSTALL_PREFIX}/lib/bluepaper/bluepaper.py"
cp "${SCRIPT_DIR}/src/renderer.py"  "${INSTALL_PREFIX}/lib/bluepaper/renderer.py"
chmod 644 "${INSTALL_PREFIX}/lib/bluepaper/bluepaper.py"
chmod 644 "${INSTALL_PREFIX}/lib/bluepaper/renderer.py"
echo -e "     ${GREEN}✓${NC} bluepaper.py + renderer.py instalados en ${INSTALL_PREFIX}/lib/bluepaper/"

# Icono
if [ -f "${SCRIPT_DIR}/logo.png" ]; then
    cp "${SCRIPT_DIR}/logo.png" "${INSTALL_PREFIX}/share/icons/hicolor/256x256/apps/bluepaper.png"
    cp "${SCRIPT_DIR}/logo.png" "${INSTALL_PREFIX}/share/icons/hicolor/128x128/apps/bluepaper.png"
    cp "${SCRIPT_DIR}/logo.png" "${INSTALL_PREFIX}/share/icons/hicolor/64x64/apps/bluepaper.png"
    echo -e "     ${GREEN}✓${NC} Iconos instalados"
fi

echo ""
echo -e "${BOLD}${BLUE}[3/5]${NC} Creando launcher..."

# IMPORTANTE: NO exportar GDK_BACKEND aquí — bluepaper.py lo maneja internamente
# El renderer necesita GDK_BACKEND=x11 pero bluepaper.py necesita wayland
cat > "${INSTALL_PREFIX}/bin/bluepaper" << 'LAUNCHER'
#!/bin/bash
exec python3 /usr/local/lib/bluepaper/bluepaper.py "$@"
LAUNCHER
chmod +x "${INSTALL_PREFIX}/bin/bluepaper"
echo -e "     ${GREEN}✓${NC} Launcher creado: ${INSTALL_PREFIX}/bin/bluepaper"

echo ""
echo -e "${BOLD}${BLUE}[4/5]${NC} Creando entrada de escritorio..."
cat > "${INSTALL_PREFIX}/share/applications/bluepaper.desktop" << DESKTOP
[Desktop Entry]
Version=1.0
Type=Application
Name=BluePaper
GenericName=Animated Wallpaper Manager
Comment=Steam Workshop animated wallpaper player for GNOME Wayland
Exec=/usr/local/bin/bluepaper
Icon=bluepaper
Categories=Utility;Settings;DesktopSettings;
Keywords=wallpaper;animated;steam;workshop;wayland;background;
StartupNotify=true
DESKTOP
chmod 744 "${INSTALL_PREFIX}/share/applications/bluepaper.desktop"
gtk-update-icon-cache "${INSTALL_PREFIX}/share/icons/hicolor" 2>/dev/null || true
update-desktop-database 2>/dev/null || true
echo -e "     ${GREEN}✓${NC} Entrada de escritorio creada"

echo ""
echo -e "${BOLD}${BLUE}[5/5]${NC} Verificando instalación..."

# Verificar que renderer.py existe
if [ -f "${INSTALL_PREFIX}/lib/bluepaper/renderer.py" ]; then
    echo -e "     ${GREEN}✓${NC} renderer.py presente"
else
    echo -e "     ${RED}✗ renderer.py NO encontrado — la instalación falló${NC}"
    exit 1
fi

if command -v bluepaper &>/dev/null; then
    echo -e "     ${GREEN}✓${NC} comando 'bluepaper' disponible"
fi

# Verificar gstreamer gtksink
if gst-inspect-1.0 gtksink &>/dev/null 2>&1; then
    echo -e "     ${GREEN}✓${NC} GStreamer gtksink disponible"
else
    echo -e "     ${YELLOW}⚠${NC} gtksink no encontrado, instala: sudo apt install gstreamer1.0-plugins-good"
fi

echo ""
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}${BOLD}  ✓ BluePaper ${VERSION} instalado!${NC}"
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${BOLD}Ejecutar:${NC}  ${CYAN}bluepaper${NC}  o busca 'BluePaper' en el menú"
echo -e "  ${BOLD}Desinstalar:${NC}  ${CYAN}sudo bash uninstall.sh${NC}"
echo ""
