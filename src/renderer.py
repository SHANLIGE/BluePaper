#!/usr/bin/env python3
"""
BluePaper Renderer
GDK_BACKEND=x11 + Gtk.Window tipo DESKTOP + gtksink
"""

import os, sys, argparse, signal, subprocess
os.environ['GDK_BACKEND'] = 'x11'

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Gdk, GLib, Gst

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('media')
    parser.add_argument('--muted', action='store_true')
    parser.add_argument('--volume', type=int, default=50)
    args = parser.parse_args()

    Gst.init(None)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, lambda *_: Gtk.main_quit())

    # Resolución del monitor principal
    display = Gdk.Display.get_default()
    monitor = display.get_primary_monitor() or display.get_monitor(0)
    geo = monitor.get_geometry()
    W, H = geo.width, geo.height

    # ── Ventana tipo DESKTOP (igual que Hidamari) ─────────────────────────────
    win = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
    win.set_title('bluepaper-renderer')
    win.set_default_size(W, H)
    win.move(geo.x, geo.y)
    win.set_decorated(False)
    win.set_app_paintable(True)
    win.set_skip_taskbar_hint(True)
    win.set_skip_pager_hint(True)
    win.set_keep_below(True)
    win.set_type_hint(Gdk.WindowTypeHint.DESKTOP)
    win.stick()
    win.set_resizable(False)

    # Revisar fondo negro para cambiar en GTK y no haga state en el cambio 
    # Fondo negro
    win.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 1))

    pipeline = [None]
    gtk_sink  = [None]

    def on_realize(widget):
        # Forzar tipo DESKTOP via xprop en el XID real
        gdk_win = win.get_window()
        if gdk_win:
            xid = gdk_win.get_xid()
            # Forzar _NET_WM_WINDOW_TYPE_DESKTOP
            subprocess.Popen([
                'xprop', '-id', str(xid),
                '-f', '_NET_WM_WINDOW_TYPE', '32a',
                '-set', '_NET_WM_WINDOW_TYPE',
                '_NET_WM_WINDOW_TYPE_DESKTOP'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Bajar al fondo
            gdk_win.lower()

    def setup_pipeline():
        uri = f'file://{os.path.abspath(args.media)}'

        sink = Gst.ElementFactory.make('gtksink', 'sink')
        if not sink:
            print('[renderer] ERROR: gtksink no disponible', file=sys.stderr)
            Gtk.main_quit()
            return False

        gtk_sink[0] = sink
        video_widget = sink.get_property('widget')

        # Expandir video a toda la pantalla
        video_widget.set_size_request(W, H)
        video_widget.set_hexpand(True)
        video_widget.set_vexpand(True)
        win.add(video_widget)
        win.show_all()

        # Forzar hints después del show
        def apply_hints(_=None):
            win.set_keep_below(True)
            gdk_win = win.get_window()
            if gdk_win:
                gdk_win.lower()
                xid = gdk_win.get_xid()
                subprocess.Popen([
                    'xprop', '-id', str(xid),
                    '-f', '_NET_WM_WINDOW_TYPE', '32a',
                    '-set', '_NET_WM_WINDOW_TYPE',
                    '_NET_WM_WINDOW_TYPE_DESKTOP'
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return False

        for ms in (100, 400, 900, 2000, 5000):
            GLib.timeout_add(ms, apply_hints)

        # Pipeline GStreamer con playbin
        pipe = Gst.ElementFactory.make('playbin', 'player')
        pipe.set_property('uri', uri)
        pipe.set_property('video-sink', sink)
        pipe.set_property('mute', args.muted)
        if not args.muted:
            pipe.set_property('volume', args.volume / 100.0)

        bus = pipe.get_bus()
        bus.add_signal_watch()

        def on_msg(bus, msg):
            t = msg.type
            if t == Gst.MessageType.EOS:
                pipe.seek_simple(
                    Gst.Format.TIME,
                    Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
                    0)
            elif t == Gst.MessageType.ERROR:
                err, dbg = msg.parse_error()
                print(f'[renderer] GST error: {err}', file=sys.stderr)
                if dbg:
                    print(f'[renderer] debug: {dbg}', file=sys.stderr)
                Gtk.main_quit()

        bus.connect('message', on_msg)
        pipe.set_state(Gst.State.PLAYING)
        pipeline[0] = pipe
        return False

    win.connect('realize', on_realize)
    win.connect('destroy', lambda *_: (
        pipeline[0] and pipeline[0].set_state(Gst.State.NULL),
        Gtk.main_quit()
    ))

    win.show()
    GLib.idle_add(setup_pipeline)
    Gtk.main()

    if pipeline[0]:
        pipeline[0].set_state(Gst.State.NULL)

if __name__ == '__main__':
    main()
