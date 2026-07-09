#!/usr/bin/env python3
"""BluePaper - Animated Wallpaper Manager for GNOME Wayland"""

import os, sys, json, subprocess, threading, signal, base64, shutil, time, socket
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

# AppIndicator — try both variants
INDICATOR_AVAILABLE = False
try:
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import AppIndicator3 as AppIndicator
    INDICATOR_AVAILABLE = True
except:
    try:
        gi.require_version('AyatanaAppIndicator3', '0.1')
        from gi.repository import AyatanaAppIndicator3 as AppIndicator
        INDICATOR_AVAILABLE = True
    except:
        pass

from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, Gio

WORKSHOP_PATH  = os.path.expanduser("~/.local/share/Steam/steamapps/workshop/content/431960")
CONFIG_DIR     = os.path.expanduser("~/.config/bluepaper")
CONFIG_FILE    = os.path.join(CONFIG_DIR, "config.json")
RENDERER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'renderer.py')
RENDERER_SOCKET = '/tmp/bluepaper_renderer.sock'
APP_VERSION    = "1.0.0"

LOGO_B64 = "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"


def get_logo_pixbuf(size=64):
    try:
        loader = GdkPixbuf.PixbufLoader()
        loader.write(base64.b64decode(LOGO_B64))
        loader.close()
        pb = loader.get_pixbuf()
        return pb.scale_simple(size, size, GdkPixbuf.InterpType.BILINEAR) if pb else None
    except: return None

def save_logo_file():
    path = os.path.join(CONFIG_DIR, 'icon.png')
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(path):
        with open(path, 'wb') as f:
            f.write(base64.b64decode(LOGO_B64))
    return path

def load_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    d = {"current_wallpaper": None, "muted": True, "volume": 50, "workshop_path": WORKSHOP_PATH}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f: d.update(json.load(f))
        except: pass
    return d

def save_config(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f: json.dump(cfg, f, indent=2)

def has_cmd(cmd): return shutil.which(cmd) is not None

def get_wallpapers(path):
    results = []
    if not os.path.exists(path): return results
    for entry in sorted(os.scandir(path), key=lambda e: e.name):
        if not entry.is_dir(): continue
        media = next((os.path.join(entry.path, f) for f in os.listdir(entry.path)
                      if f.lower().endswith(('.mp4','.gif','.webm','.avi','.mkv'))), None)
        if not media: continue
        proj = {}
        pf = os.path.join(entry.path, 'project.json')
        if os.path.exists(pf):
            try:
                with open(pf) as f: proj = json.load(f)
            except: pass
        preview = proj.get('preview','')
        if preview:
            fp = os.path.join(entry.path, preview)
            preview = fp if os.path.exists(fp) else ''
        results.append({
            'id': entry.name, 'path': entry.path, 'media': media,
            'title': proj.get('title', f'Wallpaper {entry.name}'),
            'description': proj.get('description',''),
            'preview': preview,
            'type': os.path.splitext(media)[1].lower().lstrip('.')
        })
    return results

# ── IPC to renderer ───────────────────────────────────────────────────────────
def send_ipc(cmd):
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(RENDERER_SOCKET)
        s.sendall(cmd.encode())
        s.close()
        return True
    except: return False

def renderer_running():
    return send_ipc('ping') or os.path.exists(RENDERER_SOCKET)

def set_gnome_bg(uri):
    subprocess.run(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri', uri], capture_output=True)
    subprocess.run(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri-dark', uri], capture_output=True)
    subprocess.run(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-options', 'zoom'], capture_output=True)

def extract_frame(media):
    """Extrae un frame del video y lo pone como fondo de GNOME (para blur de WhiteSur)"""
    if not has_cmd('ffmpeg'):
        return
    frame_path = os.path.join(CONFIG_DIR, 'current_frame.jpg')
    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', media,
            '-ss', '00:00:03', '-vframes', '1',
            '-vf', 'scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080',
            '-q:v', '2', frame_path
        ], capture_output=True, timeout=10)
        if os.path.exists(frame_path):
            uri = f'file://{frame_path}'
            # Forzar reload: cambiar a negro primero, luego al frame
            # Esto obliga a WhiteSur a descartar el cache del blur
            set_gnome_bg('file:///dev/null')
            time.sleep(0.15)
            set_gnome_bg(uri)
            # Segunda pasada por si WhiteSur tarda en reaccionar
            threading.Timer(1.0, lambda: set_gnome_bg(uri)).start()
            threading.Timer(2.5, lambda: set_gnome_bg(uri)).start()
    except Exception as e:
        print(f'[bluepaper] extract_frame: {e}')

# ── Wallpaper Player ──────────────────────────────────────────────────────────
class WallpaperPlayer:
    def __init__(self):
        self.proc  = None
        self._lock = threading.Lock()
        self._current = None

    def play(self, media, muted=True, volume=50):
        with self._lock:
            # If renderer already running, just update video via IPC
            if self.proc and self.proc.poll() is None:
                if send_ipc(f'play|{media}'):
                    self._current = media
                    extract_frame(media)
                    return True, 'IPC update'

            # Start new renderer process
            self._kill()
            # Extraer frame del video y ponerlo como fondo de GNOME
            # Así el blur de WhiteSur/GNOME Shell queda sincronizado
            extract_frame(media)
            env = os.environ.copy()
            env['GDK_BACKEND'] = 'x11'
            cmd = [sys.executable, RENDERER_SCRIPT, media]
            if muted: cmd.append('--muted')
            else: cmd += [f'--volume={volume/100.0}']
            try:
                self.proc = subprocess.Popen(
                    cmd, env=env,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(1.2)
                if self.proc.poll() is not None:
                    return False, 'El renderer falló al iniciar'
                self._current = media
                return True, 'XWayland+GTK renderer'
            except Exception as e:
                return False, str(e)

    def stop(self):
        with self._lock:
            send_ipc('stop')
            time.sleep(0.3)
            self._kill()
            self._current = None

    def _kill(self):
        if self.proc:
            try: self.proc.terminate(); self.proc.wait(timeout=3)
            except:
                try: self.proc.kill()
                except: pass
            self.proc = None

    def running(self):
        return self.proc is not None and self.proc.poll() is None

    def current(self): return self._current

# ── CSS ───────────────────────────────────────────────────────────────────────
CSS = b"""
* { font-family: Cantarell, Ubuntu, sans-serif; }
window { background-color: #0d0d1a; color: #e0e0ff; }
.header { background-color: #12122a; padding: 14px 18px; border-bottom: 1px solid #2a2a5a; }
.app-title { font-size: 20px; font-weight: 800; color: #a78bfa; }
.app-subtitle { font-size: 11px; color: #555580; }
.sidebar { background-color: #0f0f22; border-right: 1px solid #1e1e42; }
row { padding: 0; }
row:selected { background-color: #2d1f6e; }
row:hover    { background-color: #1a1a3e; }
.wp-row { padding: 9px 12px; border-bottom: 1px solid #161630; }
.wp-title { font-size: 13px; font-weight: 600; color: #c4b5fd; }
.wp-badge { font-size: 10px; font-weight: 700; color: #9d6fff; background-color: #1e1045; border-radius: 4px; padding: 2px 6px; }
.wp-id { font-size: 11px; color: #3a3a6a; }
.content { background-color: #0d0d1a; padding: 20px; }
.preview-frame { background-color: #0a0a1e; border: 1px solid #252550; border-radius: 10px; padding: 12px; }
.detail-title { font-size: 18px; font-weight: 700; color: #e0d0ff; }
.detail-desc  { font-size: 13px; color: #6a6a9a; }
.detail-meta  { font-size: 11px; color: #3a3a6a; }
.btn-play { background-color: #7c3aed; color: white; border: none; border-radius: 8px; padding: 10px 22px; font-size: 14px; font-weight: 700; }
.btn-play:hover { background-color: #8b5cf6; }
.btn-stop { background-color: #1a1a3a; color: #c4b5fd; border: 1px solid #3a3a6a; border-radius: 8px; padding: 10px 18px; font-size: 13px; }
.btn-stop:hover { background-color: #252550; }
.btn-minor { background-color: transparent; color: #555580; border: 1px solid #252545; border-radius: 6px; padding: 5px 12px; font-size: 12px; }
.btn-minor:hover { color: #a78bfa; border-color: #7c3aed; background-color: #1a1a35; }
.statusbar { background-color: #08081a; border-top: 1px solid #1a1a3a; padding: 5px 12px; }
.status-text { font-size: 11px; color: #3a3a6a; }
.count-label { font-size: 11px; color: #3a3a6a; }
.empty-hint  { font-size: 13px; color: #2a2a5a; }
scrollbar { background-color: #0a0a18; min-width: 5px; }
scrollbar slider { background-color: #252550; border-radius: 3px; min-width: 5px; min-height: 20px; }
scrollbar slider:hover { background-color: #4040a0; }
"""

# ── System Tray Indicator ─────────────────────────────────────────────────────
class TrayIndicator:
    def __init__(self, app):
        self.app = app
        if not INDICATOR_AVAILABLE: return
        icon_path = save_logo_file()
        self.ind = AppIndicator.Indicator.new(
            'bluepaper',
            icon_path,
            AppIndicator.IndicatorCategory.APPLICATION_STATUS)
        self.ind.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.ind.set_menu(self._build_menu())

    def _build_menu(self):
        menu = Gtk.Menu()

        item_title = Gtk.MenuItem(label='BluePaper')
        item_title.set_sensitive(False)
        menu.append(item_title)
        menu.append(Gtk.SeparatorMenuItem())

        item_show = Gtk.MenuItem(label='Abrir BluePaper')
        item_show.connect('activate', lambda _: self.app.show_window())
        menu.append(item_show)

        item_stop = Gtk.MenuItem(label='⏹  Detener wallpaper')
        item_stop.connect('activate', lambda _: self.app.stop_wallpaper())
        menu.append(item_stop)

        menu.append(Gtk.SeparatorMenuItem())

        item_quit = Gtk.MenuItem(label='Salir')
        item_quit.connect('activate', lambda _: self.app.quit())
        menu.append(item_quit)

        menu.show_all()
        return menu

    def update_menu(self):
        if INDICATOR_AVAILABLE:
            self.ind.set_menu(self._build_menu())

# ── Main Window ───────────────────────────────────────────────────────────────
class BluePaperWindow(Gtk.Window):
    def __init__(self, state):
        super().__init__(title="BluePaper")
        self.state = state
        self.selected_idx = -1
        self.set_default_size(940, 600)
        # Hide instead of destroy so tray keeps working
        self.connect('delete-event', self._on_close)
        try:
            Gtk.Window.set_default_icon_from_file(save_logo_file())
        except: pass
        prov = Gtk.CssProvider()
        prov.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), prov, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self._build()
        self.show_all()

    def _on_close(self, *_):
        self.hide()
        return True  # prevent destroy

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        root.pack_start(self._mk_header(), False, False, 0)
        body = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        body.set_vexpand(True)
        body.pack_start(self._mk_sidebar(), False, False, 0)
        body.pack_start(self._mk_detail(), True, True, 0)
        root.pack_start(body, True, True, 0)
        root.pack_start(self._mk_statusbar(), False, False, 0)
        self.add(root)

    def _mk_header(self):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.get_style_context().add_class('header')
        pb = get_logo_pixbuf(38)
        if pb: box.pack_start(Gtk.Image.new_from_pixbuf(pb), False, False, 0)
        tb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        t = Gtk.Label(label="BLUEPAPER"); t.get_style_context().add_class('app-title'); t.set_halign(Gtk.Align.START)
        s = Gtk.Label(label="Animated Wallpaper · Steam Workshop 431960"); s.get_style_context().add_class('app-subtitle'); s.set_halign(Gtk.Align.START)
        tb.pack_start(t, False, False, 0); tb.pack_start(s, False, False, 0)
        box.pack_start(tb, False, False, 0)
        spacer = Gtk.Box(); spacer.set_hexpand(True)
        box.pack_start(spacer, True, True, 0)
        for label, cb in [("↻", lambda b: self._refresh()), ("⚙", lambda b: self._open_settings())]:
            btn = Gtk.Button(label=label); btn.get_style_context().add_class('btn-minor'); btn.connect('clicked', cb)
            box.pack_start(btn, False, False, 2)
        return box

    def _mk_sidebar(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.get_style_context().add_class('sidebar'); box.set_size_request(270, -1)
        self.count_lbl = Gtk.Label(label="0 wallpapers")
        self.count_lbl.get_style_context().add_class('count-label')
        self.count_lbl.set_halign(Gtk.Align.START)
        self.count_lbl.set_margin_start(12); self.count_lbl.set_margin_top(8); self.count_lbl.set_margin_bottom(6)
        box.pack_start(self.count_lbl, False, False, 0)
        box.pack_start(Gtk.Separator(), False, False, 0)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC); scroll.set_vexpand(True)
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.connect('row-selected', self._row_selected)
        scroll.add(self.listbox)
        box.pack_start(scroll, True, True, 0)
        return box

    def _mk_detail(self):
        self.stack = Gtk.Stack(); self.stack.set_hexpand(True)
        # Placeholder
        ph = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        ph.set_valign(Gtk.Align.CENTER); ph.set_halign(Gtk.Align.CENTER)
        pb = get_logo_pixbuf(80)
        if pb: ph.pack_start(Gtk.Image.new_from_pixbuf(pb), False, False, 0)
        lbl = Gtk.Label(label="Selecciona un wallpaper")
        lbl.get_style_context().add_class('empty-hint')
        ph.pack_start(lbl, False, False, 0)
        self.stack.add_named(ph, 'placeholder')
        # Detail
        dv = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        dv.get_style_context().add_class('content'); dv.set_vexpand(True)
        pf = Gtk.Box(); pf.get_style_context().add_class('preview-frame'); pf.set_size_request(-1, 190)
        self.preview_img = Gtk.Image(); self.preview_img.set_hexpand(True)
        pf.pack_start(self.preview_img, True, True, 0)
        dv.pack_start(pf, False, False, 0)
        self.lbl_title = Gtk.Label(label=""); self.lbl_title.get_style_context().add_class('detail-title')
        self.lbl_title.set_halign(Gtk.Align.START); self.lbl_title.set_line_wrap(True)
        dv.pack_start(self.lbl_title, False, False, 0)
        self.lbl_desc = Gtk.Label(label=""); self.lbl_desc.get_style_context().add_class('detail-desc')
        self.lbl_desc.set_halign(Gtk.Align.START); self.lbl_desc.set_line_wrap(True); self.lbl_desc.set_max_width_chars(65)
        dv.pack_start(self.lbl_desc, False, False, 0)
        self.lbl_meta = Gtk.Label(label=""); self.lbl_meta.get_style_context().add_class('detail-meta')
        self.lbl_meta.set_halign(Gtk.Align.START)
        dv.pack_start(self.lbl_meta, False, False, 0)
        dv.pack_start(Gtk.Separator(), False, False, 4)
        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.btn_apply = Gtk.Button(label="▶  Poner como fondo de pantalla")
        self.btn_apply.get_style_context().add_class('btn-play')
        self.btn_apply.connect('clicked', lambda b: self._apply())
        btn_stop = Gtk.Button(label="⏹  Detener")
        btn_stop.get_style_context().add_class('btn-stop')
        btn_stop.connect('clicked', lambda b: self.state['player'].stop() or self.status("⏹  Detenido"))
        btn_row.pack_start(self.btn_apply, False, False, 0)
        btn_row.pack_start(btn_stop, False, False, 0)
        dv.pack_start(btn_row, False, False, 0)
        mute_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        ml = Gtk.Label(label="Silenciar audio:"); ml.get_style_context().add_class('detail-desc')
        self.mute_sw = Gtk.Switch(); self.mute_sw.set_active(self.state['config'].get('muted', True))
        self.mute_sw.connect('state-set', self._mute_toggled)
        mute_row.pack_start(ml, False, False, 0); mute_row.pack_start(self.mute_sw, False, False, 0)
        dv.pack_start(mute_row, False, False, 0)
        self.stack.add_named(dv, 'detail')
        self.stack.set_visible_child_name('placeholder')
        return self.stack

    def _mk_statusbar(self):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.get_style_context().add_class('statusbar')
        self.status_lbl = Gtk.Label(label="Listo"); self.status_lbl.get_style_context().add_class('status-text')
        self.status_lbl.set_halign(Gtk.Align.START); self.status_lbl.set_hexpand(True)
        ver = Gtk.Label(label=f"BluePaper v{APP_VERSION}"); ver.get_style_context().add_class('status-text')
        box.pack_start(self.status_lbl, True, True, 4); box.pack_end(ver, False, False, 4)
        return box

    def populate(self, wallpapers):
        for ch in self.listbox.get_children(): self.listbox.remove(ch)
        n = len(wallpapers)
        self.count_lbl.set_text(f"{n} wallpaper{'s' if n != 1 else ''}")
        if not wallpapers:
            row = Gtk.ListBoxRow()
            lbl = Gtk.Label(label="No se encontraron wallpapers.\nRevisa ⚙ Settings.")
            lbl.get_style_context().add_class('empty-hint')
            lbl.set_margin_top(24); lbl.set_margin_bottom(24)
            row.add(lbl); self.listbox.add(row); self.listbox.show_all(); return
        for i, wp in enumerate(wallpapers):
            row = Gtk.ListBoxRow(); row.wp_idx = i
            vb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            vb.get_style_context().add_class('wp-row')
            top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            tl = Gtk.Label(label=wp['title'][:36] + ('…' if len(wp['title'])>36 else ''))
            tl.get_style_context().add_class('wp-title'); tl.set_halign(Gtk.Align.START); tl.set_hexpand(True)
            badge = Gtk.Label(label=wp['type'].upper()); badge.get_style_context().add_class('wp-badge')
            top.pack_start(tl, True, True, 0); top.pack_end(badge, False, False, 0)
            il = Gtk.Label(label=f"ID: {wp['id']}"); il.get_style_context().add_class('wp-id'); il.set_halign(Gtk.Align.START)
            vb.pack_start(top, False, False, 0); vb.pack_start(il, False, False, 0)
            row.add(vb); self.listbox.add(row)
        self.listbox.show_all()

    def _row_selected(self, lb, row):
        if row is None: return
        idx = getattr(row, 'wp_idx', -1)
        if idx < 0: return
        self.selected_idx = idx; self._show_detail(idx)

    def _show_detail(self, idx):
        wps = self.state['wallpapers']
        if idx < 0 or idx >= len(wps): return
        wp = wps[idx]
        self.lbl_title.set_text(wp['title'])
        desc = wp.get('description','') or 'Sin descripción.'
        self.lbl_desc.set_text(desc[:220] + ('…' if len(desc)>220 else ''))
        try: sz_str = f"  •  {os.path.getsize(wp['media'])/1024/1024:.1f} MB"
        except: sz_str = ''
        self.lbl_meta.set_text(f"ID: {wp['id']}  •  {wp['type'].upper()}  •  {os.path.basename(wp['media'])}{sz_str}")
        if wp.get('preview') and os.path.exists(wp['preview']):
            try:
                pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(wp['preview'], 500, 170, True)
                self.preview_img.set_from_pixbuf(pb)
            except: self.preview_img.set_from_icon_name('video-x-generic', Gtk.IconSize.DIALOG)
        else: self.preview_img.set_from_icon_name('video-x-generic', Gtk.IconSize.DIALOG)
        self.stack.set_visible_child_name('detail')

    def _apply(self):
        if self.selected_idx < 0: return
        wp  = self.state['wallpapers'][self.selected_idx]
        cfg = self.state['config']
        cfg['current_wallpaper'] = wp['id']; save_config(cfg)
        ok, backend = self.state['player'].play(
            wp['media'], muted=cfg.get('muted', True), volume=cfg.get('volume', 50))
        self.status(f"▶  {wp['title']}  [{backend}]" if ok else f"⚠  {backend}")

    def _mute_toggled(self, sw, state):
        self.state['config']['muted'] = state; save_config(self.state['config']); return False

    def _refresh(self):
        wps = get_wallpapers(self.state['config'].get('workshop_path', WORKSHOP_PATH))
        self.state['wallpapers'] = wps; self.populate(wps)
        self.status(f"Actualizado — {len(wps)} wallpapers")

    def _open_settings(self):
        d = SettingsDialog(self, self.state['config'])
        if d.run() == Gtk.ResponseType.OK:
            self.state['config']['workshop_path'] = d.get_path()
            save_config(self.state['config']); self._refresh()
        d.destroy()

    def status(self, msg): self.status_lbl.set_text(msg)

    def select_by_id(self, wp_id):
        for i, wp in enumerate(self.state['wallpapers']):
            if wp['id'] == wp_id:
                row = self.listbox.get_row_at_index(i)
                if row: self.listbox.select_row(row); break

class SettingsDialog(Gtk.Dialog):
    def __init__(self, parent, cfg):
        super().__init__(title="Configuración", transient_for=parent, modal=True)
        self.set_default_size(540, 150)
        self.add_button("Cancelar", Gtk.ResponseType.CANCEL)
        self.add_button("Guardar",  Gtk.ResponseType.OK)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_start(18); box.set_margin_end(18); box.set_margin_top(14); box.set_margin_bottom(14)
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        lbl = Gtk.Label(label="Ruta Workshop:"); lbl.set_size_request(130,-1); lbl.set_halign(Gtk.Align.START)
        self.entry = Gtk.Entry(); self.entry.set_text(cfg.get('workshop_path', WORKSHOP_PATH)); self.entry.set_hexpand(True)
        row.pack_start(lbl, False, False, 0); row.pack_start(self.entry, True, True, 0)
        box.pack_start(row, False, False, 0)
        self.get_content_area().pack_start(box, True, True, 0); self.show_all()
    def get_path(self): return self.entry.get_text().strip()

# ── Application ───────────────────────────────────────────────────────────────
class BluePaperApp:
    def __init__(self):
        self.config     = load_config()
        self.player     = WallpaperPlayer()
        self.wallpapers = get_wallpapers(self.config.get('workshop_path', WORKSHOP_PATH))
        self.state      = {'config': self.config, 'player': self.player, 'wallpapers': self.wallpapers}
        self.win        = BluePaperWindow(self.state)
        self.win.populate(self.wallpapers)
        if self.config.get('current_wallpaper'):
            self.win.select_by_id(self.config['current_wallpaper'])
        self.tray = TrayIndicator(self) if INDICATOR_AVAILABLE else None
        if not INDICATOR_AVAILABLE:
            print('[BluePaper] AppIndicator no disponible. Instala: sudo apt install gir1.2-appindicator3-0.1', file=sys.stderr)

    def show_window(self):
        self.win.show_all()
        self.win.present()

    def stop_wallpaper(self):
        self.player.stop()
        self.win.status("⏹  Detenido")

    def quit(self):
        self.player.stop()
        Gtk.main_quit()

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = BluePaperApp()
    Gtk.main()

if __name__ == '__main__':
    main()
