from definitions import *

class Layout:

    regions = []

    def __dist__(self, a, b):
        ax, ay = a
        bx, by = b
        return (ax - bx) * (ax - bx) + (ay - by) * (ay - by)

    def __get_closest_window(self, rect: Rect, windows):
        center = rect.center()
        min_window = windows[0]
        min_dist = float("inf")
        for window in windows:
            window_rect = window.get_geometry()
            window_center = window_rect.center()
            if self.__dist__(center, window_center) < min_dist:
                min_window = window
                min_dist = self.__dist__(center, window_center)
        return min_window

    def assign_and_move(self, windows):
        for region in self.regions:
            win = self.__get_closest_window(region, windows)
            win.move_resize(region)
            windows.remove(win)

class MasterSlaveDivider(Layout):

    def __init__(self, screen: Rect, n, gaps = 0, master_ratio = 0.5):
        super()
        if n == 1:
            return [Rect(gaps, gaps, screen.width - 2 * gaps, screen.height - 2 * gaps)]
        # Now that the divide by 0 is out of the way...
        master_width = screen.width * master_ratio - 1.5 * gaps
        slave_width = screen.width * (1 - master_ratio) - 1.5 * gaps
        master_height = screen.height - 2 * gaps
        slave_height = (screen.height - n * gaps) / (n - 1)
        self.regions.append(Rect(gaps, gaps, master_width, master_height))
        for i in range(n - 1):
            self.regions.append(Rect(2 * gaps + master_width, gaps + (slave_height + gaps) * i, slave_width, slave_height))

class ColumnDivider(Layout):

    def __init__(self, screen: Rect, n, gaps = 0):
        ret = []
        height = screen.height - 2 * gaps
        width = (screen.width - (n + 1) * gaps) / n
        for i in range(n):
            self.regions.append(Rect(int(gaps + (width + gaps) * i), gaps, int(width), height))
