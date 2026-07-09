#!/bin/bash
# BluePaper Uninstaller

set -e

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root: sudo bash uninstall.sh"
    exit 1
fi

INSTALL_PREFIX="/usr/local"

echo "Removing BluePaper..."

rm -rf "${INSTALL_PREFIX}/lib/bluepaper"
rm -f "${INSTALL_PREFIX}/bin/bluepaper"
rm -f "${INSTALL_PREFIX}/share/applications/bluepaper.desktop"
rm -f "${INSTALL_PREFIX}/share/icons/hicolor/256x256/apps/bluepaper.png"
rm -f "${INSTALL_PREFIX}/share/icons/hicolor/128x128/apps/bluepaper.png"
rm -f "${INSTALL_PREFIX}/share/icons/hicolor/64x64/apps/bluepaper.png"
rm -rf "${INSTALL_PREFIX}/share/bluepaper"
rm -f "/etc/xdg/autostart/bluepaper-startup.desktop"

gtk-update-icon-cache /usr/local/share/icons/hicolor 2>/dev/null || true
update-desktop-database 2>/dev/null || true

echo "BluePaper has been uninstalled."
echo "User config at ~/.config/bluepaper was preserved (remove manually if desired)."
