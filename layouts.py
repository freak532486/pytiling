from os import close
from definitions import *
import time

class Layout:

    def __init__(self, windows, screen: Rect):
        self.windows = windows.copy()
        self.regions = []
        self.__grab_region = None
        self.calculate_regions(screen)
        self.assign_and_move()

    def __dist(self, a, b):
        ax, ay = a
        bx, by = b
        return (ax - bx) * (ax - bx) + (ay - by) * (ay - by)

    def __get_closest_window(self, rect: Rect):
        center = rect.topleft()
        min_window = self.windows[0]
        min_dist = float("inf")
        for window in self.windows:
            t = time.time()
            window_rect = window.get_geometry()
            print(f"get_geometry: {1000 * (time.time() - t)} ms")
            window_center = window_rect.topleft()
            if self.__dist(center, window_center) < min_dist:
                min_window = window
                min_dist = self.__dist(center, window_center)
        return min_window

    def __get_closest_region(self, window: Window):
        min_dist = float("inf")
        min_region = self.regions[0]
        for region in self.regions:
            dist = self.__dist(region.topleft(), window.get_geometry().topleft())
            if dist < min_dist:
                min_dist = dist
                min_region = region
        return min_region

    # Override this for new layouts
    def calculate_regions(self, screen):
        return [screen] * len(self.windows)

    def assign_and_move(self):
        new_windows = []
        for i in range(len(self.regions)):
            region = self.regions[i]
            t = time.time()
            win = self.__get_closest_window(region)
            print(f"get_closest: {1000 * (time.time() - t)} ms")
            t = time.time()
            win.move_resize(region)
            print(f"move_resize: {1000 * (time.time() - t)} ms")
            new_windows.append(win)
            self.windows.remove(win)
        self.windows = new_windows

    def on_grab(self, window: Window):
        self.__grab_region = self.regions[self.windows.index(window)]

    def on_move(self, window: Window):
        if not window.grabbed:
            return
        closest_region = self.__get_closest_region(window)
        if closest_region != self.__grab_region:
            corresponding_window_index = self.regions.index(closest_region)
            grabbed_window_index = self.windows.index(window)
            corresponding_window = self.windows[corresponding_window_index]
            corresponding_window.move_resize(self.__grab_region)
            self.__grab_region = closest_region
            self.windows[corresponding_window_index] = window
            self.windows[grabbed_window_index] = corresponding_window

    def on_drop(self, window: Window):
        if self.__grab_region == None:
            return
        window.move_resize(self.__grab_region)
        self.__grab_region = None


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
        # Edge cases 
        if n == 0:
            self.regions = []
            return
        if n == 1:
            self.regions = [Rect(gaps, gaps, screen.width - 2 * gaps, screen.height - 2 * gaps)]
            return
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
