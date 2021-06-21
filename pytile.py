from definitions import *
import layouts
import Xlib.X
import subprocess
import re
from pynput.keyboard import Listener, Key

class Main:

    def __init__(self, gaps = 0, manage_all = False):
        self.managed_workspace = Window.get_current_workspace()
        self.gaps = gaps
        self.combo_pressed = False
        root_size = Window.get_root_size(self.managed_workspace)
        self.root_geom = Rect(0, 0, root_size[0], root_size[1])
        self.windows = []
        if manage_all:
            self.add_all_windows_from_current_workspace()
        self.layout = layouts.MasterSlaveDivider(self.windows, self.root_geom, gaps = self.gaps)

    def __get_event_window(self, event):
        event_window_candidates = [window for window in self.windows if window.window == event.window]
        if len(event_window_candidates) == 0:
            return None
        return event_window_candidates[0]

    def add_all_windows_from_current_workspace(self):
        self.windows = Window.get_all(workspace = self.managed_workspace)

        Window.get_root().change_attributes(event_mask = Xlib.X.SubstructureNotifyMask)
        for window in self.windows:
            window.window.change_attributes(event_mask = Xlib.X.StructureNotifyMask | Xlib.X.FocusChangeMask)

    def relayout(self):
        self.layout = layouts.MasterSlaveDivider(self.windows, self.root_geom, gaps = self.gaps)

    def add_managed_window(self, window_id):
        window = Window(Window.display.create_resource_object("window", window_id), window_id)
        if window.is_normal() and window.get_workspace() == self.managed_workspace:
            window.window.change_attributes(event_mask = Xlib.X.StructureNotifyMask | Xlib.X.FocusChangeMask)
            self.windows.append(window)
            self.relayout()

    def run(self):
        while True:
            event = Window.display.next_event()
            if event != None:
                if event.type == Xlib.X.ConfigureNotify:
                    event_window = self.__get_event_window(event)
                    if event_window == None:
                        continue
                    self.layout.on_move(event_window)

                if event.type == Xlib.X.FocusOut:
                    if event.mode == Xlib.X.NotifyGrab:
                        event_window = self.__get_event_window(event)
                        if event_window == None:
                            continue
                        event_window.grabbed = True
                        self.layout.on_grab(event_window)

                if event.type == Xlib.X.FocusIn:
                    if event.mode == Xlib.X.NotifyUngrab:
                        event_window = self.__get_event_window(event)
                        if event_window == None:
                            continue
                        event_window.grabbed = False
                        self.layout.on_drop(event_window)

                if event.type == Xlib.X.DestroyNotify:
                    destroyed_window_id = event.window.id
                    for window in self.windows:
                        if window.id == destroyed_window_id:
                            self.windows.remove(window)
                            self.layout = layouts.MasterSlaveDivider(self.windows, self.root_geom, gaps = self.gaps)

main_thread = Main(gaps = 20, manage_all = True)

key_combo = { Key.cmd, Key.space }
current = set()

def on_press(key):
    if key in key_combo:
        current.add(key)
        if current == key_combo:
            get_window_id_interactive()

def on_release(key):
    if key in current:
        current.remove(key)

def get_window_id_interactive():
    output = subprocess.check_output("xwininfo -int", shell = True, encoding="UTF-8")
    id = int(re.search("id: (\d*)", output).group(1))
    main_thread.add_managed_window(id)


Listener(on_press = on_press, on_release = on_release).start()
main_thread.run()
        