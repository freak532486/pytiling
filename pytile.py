import Xlib.display
import Xlib.X
import os
from definitions import *
import layouts

display = Xlib.display.Display()
root = display.screen().root

def get_window_geometry(win: Window):
    win = win.window
    geom = win.get_geometry()
    (x, y) = (geom.x, geom.y)
    while True:
        parent = win.query_tree().parent
        pgeom = parent.get_geometry()
        x += pgeom.x
        y += pgeom.y
        if parent.id == root.id:
            break
        win = parent
    return Rect(x, y, geom.width, geom.height)

def get_root_window_size():
    root_workspace = root.get_full_property(display.intern_atom("_NET_CURRENT_DESKTOP"), Xlib.X.AnyPropertyType).value[0]
    geometry_array = root.get_full_property(display.intern_atom("_NET_WORKAREA"), Xlib.X.AnyPropertyType).value
    width = geometry_array[4 * root_workspace + 2]
    height = geometry_array[4 * root_workspace + 3]
    return (width, height)

def get_all_normal_windows_on_current_workspace():
    window_list = list(root.get_full_property(
        display.intern_atom("_NET_CLIENT_LIST"), Xlib.X.AnyPropertyType
    ).value)
    root_workspace = root.get_full_property(display.intern_atom("_NET_CURRENT_DESKTOP"), Xlib.X.AnyPropertyType).value[0]
    ret = []
    for window_id in window_list:
        window = display.create_resource_object("window", window_id)
        window_workspace = window.get_full_property(display.intern_atom("_NET_WM_DESKTOP"), Xlib.X.AnyPropertyType)
        window_type = window.get_full_property(display.intern_atom("_NET_WM_WINDOW_TYPE"), Xlib.X.AnyPropertyType)
        if window_workspace == None or window_type == None:
            continue
        window_workspace = window_workspace.value[0]
        window_type = window_type.value[0]
        if window_workspace == root_workspace and window_type == display.intern_atom("_NET_WM_WINDOW_TYPE_NORMAL"):
            ret.append(Window(window, window_id))
    return ret

def move_window(window: Window, rect: Rect):
    """ rect is a 4-tuple (x, y, width, height), where x and y describe the top left corner of the new position """
    # window_name = window.get_full_property(display.intern_atom("WM_NAME"), Xlib.X.AnyPropertyType).value.decode("UTF-8")
    window_frame = window.window.get_full_property(display.intern_atom("_NET_FRAME_EXTENTS"), Xlib.X.AnyPropertyType).value
    f_l, f_r, f_t, f_b = (window_frame[0], window_frame[1], window_frame[2], window_frame[3])
    arg1 = f'-ir "{hex(window.id)}"'
    arg2 = f'-e 0,{rect.x},{rect.y},{rect.width - f_l - f_r},{rect.height - f_t - f_b}'
    os.system(f"wmctrl {arg1} {arg2}")

def dist(a, b):
    ax, ay = a
    bx, by = b
    return (ax - bx) * (ax - bx) + (ay - by) * (ay - by)

def getClosestWindow(rect: Rect, windows):
    center = rect.center()
    min_window = windows[0]
    min_dist = float("inf")
    for window in windows:
        window_rect = get_window_geometry(window)
        window_center = window_rect.center()
        if dist(center, window_center) < min_dist:
            min_window = window
            min_dist = dist(center, window_center)
    return min_window





windows = get_all_normal_windows_on_current_workspace()
root_size = get_root_window_size()
root_geom = Rect(0, 0, root_size[0], root_size[1])

divider = layouts.MasterSlaveDivider()

divide = divider.divide(root_geom, len(windows), gaps = 20)
for region in divide:
    win = getClosestWindow(region, windows)
    move_window(win, region)
    windows.remove(win)