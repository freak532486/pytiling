from definitions import *
import layouts

def dist(a, b):
    ax, ay = a
    bx, by = b
    return (ax - bx) * (ax - bx) + (ay - by) * (ay - by)

def getClosestWindow(rect: Rect, windows):
    center = rect.center()
    min_window = windows[0]
    min_dist = float("inf")
    for window in windows:
        window_rect = window.get_geometry()
        window_center = window_rect.center()
        if dist(center, window_center) < min_dist:
            min_window = window
            min_dist = dist(center, window_center)
    return min_window

current_workspace = Window.get_current_workspace()
windows = Window.get_all(workspace = current_workspace)
root_size = Window.get_root_size(current_workspace)
root_geom = Rect(0, 0, root_size[0], root_size[1])

divider = layouts.MasterSlaveDivider()

divide = divider.divide(root_geom, len(windows), gaps = 20)
for region in divide:
    win = getClosestWindow(region, windows)
    win.move_resize(region)
    windows.remove(win)