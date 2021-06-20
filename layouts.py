from definitions import *

class Layout:

    regions = []
    windows = []

    def __init__(self, windows, screen: Rect):
        self.windows = windows
        self.calculate_regions(screen)
        self.assign_and_move()

    def __dist__(self, a, b):
        ax, ay = a
        bx, by = b
        return (ax - bx) * (ax - bx) + (ay - by) * (ay - by)

    def __get_closest_window(self, rect: Rect):
        center = rect.center()
        min_window = self.windows[0]
        min_dist = float("inf")
        for window in self.windows:
            window_rect = window.get_geometry()
            window_center = window_rect.center()
            if self.__dist__(center, window_center) < min_dist:
                min_window = window
                min_dist = self.__dist__(center, window_center)
        return min_window

    # Override this for new layouts
    def calculate_regions(self, screen):
        return [screen] * len(self.windows)

    def assign_and_move(self):
        new_windows = []
        for i in range(len(self.regions)):
            region = self.regions[i]
            win = self.__get_closest_window(region)
            win.move_resize(region)
            new_windows.append(win)
            self.windows.remove(win)
        self.windows = new_windows

class MasterSlaveDivider(Layout):

    gaps = None
    master_ratio = None

    def __init__(self, windows, screen: Rect, gaps = 0, master_ratio = 0.5):
        self.gaps = gaps
        self.master_ratio = master_ratio
        super().__init__(windows, screen)
        

    def calculate_regions(self, screen):
        n = len(self.windows)
        gaps = self.gaps
        master_ratio = self.master_ratio
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

    gaps = None

    def __init__(self, windows, screen: Rect, gaps = 0):
        self.gaps = gaps
        super().__init__(windows, screen)
        

    def calculate_regions(self, screen):
        n = len(self.windows)
        gaps = self.gaps
        height = screen.height - 2 * gaps
        width = (screen.width - (n + 1) * gaps) / n
        for i in range(n):
            self.regions.append(Rect(int(gaps + (width + gaps) * i), gaps, int(width), height))
