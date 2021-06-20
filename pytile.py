from definitions import *
import layouts

current_workspace = Window.get_current_workspace()
windows = Window.get_all(workspace = current_workspace)
root_size = Window.get_root_size(current_workspace)
root_geom = Rect(0, 0, root_size[0], root_size[1])

divider = layouts.MasterSlaveDivider(windows, root_geom, gaps = 20)
divider.assign_and_move()