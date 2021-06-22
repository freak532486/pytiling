from definitions import *
import layouts
import Xlib.X
import subprocess
import re
from pynput.keyboard import Listener, Key

class Main:

    def __init__(self, gaps = 0, manage_all = False):
        self.layout_dict = {} # Maps workspace number to layout
        self.gaps = gaps
        self.combo_pressed = False
        if manage_all:
            self.add_all_windows_from_current_workspace()
        Window.get_root().change_attributes(event_mask = Xlib.X.SubstructureNotifyMask)

    def __get_event_window(self, event):
        event_window_candidates = [window for window in self.get_current_layout().windows if window.window == event.window]
        if len(event_window_candidates) == 0:
            return None
        return event_window_candidates[0]
  
    def get_current_layout(self):
        ws = Window.get_current_workspace()
        if ws not in self.layout_dict:
            self.layout_dict[ws] = layouts.MasterSlaveDivider([], Window.get_root_geom(ws), gaps = self.gaps)
        return self.layout_dict[ws]

    def add_all_windows_from_current_workspace(self):
        windows = Window.get_all(workspace = Window.get_current_workspace())

        for window in windows:
            window.window.change_attributes(event_mask = Xlib.X.StructureNotifyMask | Xlib.X.FocusChangeMask)
            self.add_managed_window(window)

    def add_managed_window(self, window):
        if window.is_normal():
            workspace = window.get_workspace()
            window.window.change_attributes(event_mask = Xlib.X.StructureNotifyMask | Xlib.X.FocusChangeMask)
            if workspace not in self.layout_dict:
                self.layout_dict[workspace] = layouts.MasterSlaveDivider([], Window.get_root_geom(workspace), gaps = self.gaps)
            self.layout_dict[workspace].add_windows([window])

    def run(self):
        while True:
            event = Window.display.next_event()
            if event != None:
                if event.type == Xlib.X.ConfigureNotify:
                    event_window = self.__get_event_window(event)
                    if event_window == None:
                        continue
                    self.get_current_layout().on_move(event_window)

                if event.type == Xlib.X.FocusOut:
                    if event.mode == Xlib.X.NotifyGrab:
                        event_window = self.__get_event_window(event)
                        if event_window == None:
                            continue
                        event_window.grabbed = True
                        self.get_current_layout().on_grab(event_window)

                if event.type == Xlib.X.FocusIn:
                    if event.mode == Xlib.X.NotifyUngrab:
                        event_window = self.__get_event_window(event)
                        if event_window == None:
                            continue
                        event_window.grabbed = False
                        self.get_current_layout().on_drop(event_window)

                if event.type == Xlib.X.DestroyNotify:
                    destroyed_window_id = event.window.id
                    for window in self.get_current_layout().windows:
                        if window.id == destroyed_window_id:
                            self.get_current_layout().remove_windows([window])

main_thread = Main(gaps = 20, manage_all = False)

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
    main_thread.add_managed_window(Window.from_id(id))


Listener(on_press = on_press, on_release = on_release).start()
main_thread.run()
        