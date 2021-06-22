from Xlib.X import WhenMapped
import Xlib.display
import subprocess
import time

class Rect:
    def __init__(self, x, y, width, height):
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)

    def center(self):
        return (self.x + self.width / 2, self.y + self.height / 2)

    def topleft(self):
        return (self.x, self.y)

    def __repr__(self):
        return f"(x: {self.x}, y: {self.y}, width: {self.width}, height: {self.height})"

    def __eq__(self, rect):
        if type(rect) != type(self):
            return False
        return rect.x == self.x and rect.y == self.y and rect.width == self.width and rect.height == self.height

class Window:

    display = Xlib.display.Display()

    def __init__(self, window, id):
        self.window = window
        self.grabbed = False
        self.id = id

    @staticmethod
    def from_id(id):
        return Window(Window.display.create_resource_object("window", id), id)

    @staticmethod
    def get_root():
        return Window.display.screen().root

    @staticmethod
    def get_root_geom(workspace):
        geometry_array = Window.get_root().get_full_property(Window.display.intern_atom("_NET_WORKAREA"), Xlib.X.AnyPropertyType).value
        width = geometry_array[4 * workspace + 2]
        height = geometry_array[4 * workspace + 3]
        return Rect(0, 0, width, height)

    @staticmethod
    def get_current_workspace():
        display = Xlib.display.Display()
        return Window.get_root().get_full_property(display.intern_atom("_NET_CURRENT_DESKTOP"), Xlib.X.AnyPropertyType).value[0]

    @staticmethod
    def get_all(workspace=None):
        t = time.time()

        root = Window.get_root()
        window_list = list(root.get_full_property(
            Window.display.intern_atom("_NET_CLIENT_LIST"), 
            Xlib.X.AnyPropertyType).value
        )
        ret = []
        for window_id in window_list:
            window = Window.display.create_resource_object("window", window_id)
            window_workspace = window.get_full_property(Window.display.intern_atom("_NET_WM_DESKTOP"), Xlib.X.AnyPropertyType)
            window_type = window.get_full_property(Window.display.intern_atom("_NET_WM_WINDOW_TYPE"), Xlib.X.AnyPropertyType)
            if window_workspace == None or window_type == None:
                continue
            window_workspace = window_workspace.value[0]
            window_type = window_type.value[0]
            if (window_workspace == workspace or workspace == None) and window_type == Window.display.intern_atom("_NET_WM_WINDOW_TYPE_NORMAL"):
                ret.append(Window(window, window_id))
        return ret

    @staticmethod
    def get_display():
        return Window.display

    def get_frame(self):
        """ Returns 4-tuple (frame_left_thickness, frame_right_thickness, frame_top_thickness, frame_bottom_thickness) """
        window_frame = self.window.get_full_property(Window.display.intern_atom("_NET_FRAME_EXTENTS"), Xlib.X.AnyPropertyType).value
        return window_frame[0], window_frame[1], window_frame[2], window_frame[3]

    def move_resize(self, rect: Rect):
        """ rect is a 4-tuple (x, y, width, height), where x and y describe the top left corner of the new position """
        f_l, f_r, f_t, f_b = self.get_frame()
        arg1 = f'-ir "{hex(self.id)}"'
        arg2 = f'-e 0,{rect.x},{rect.y},{rect.width - f_l - f_r},{rect.height - f_t - f_b}'
        subprocess.run(f"wmctrl {arg1} {arg2}", shell = True)

    def get_geometry(self):
        win = self.window
        coords = Window.get_root().translate_coords(win, 0, 0)
        geom = win.get_geometry()
        ret = Rect(coords.x, coords.y, geom.width, geom.height)
        return ret

    def get_property(self, property):
        try:
            result = self.window.get_full_property(self.display.intern_atom(property), Xlib.X.AnyPropertyType)
            if result == None:
                return None
            return result.value[0]
        except Xlib.error.BadWindow:
            return False

    def get_workspace(self):
        return self.get_property("_NET_WM_DESKTOP")

    def is_normal(self):
        return self.get_property("_NET_WM_WINDOW_TYPE") == self.display.intern_atom("_NET_WM_WINDOW_TYPE_NORMAL")