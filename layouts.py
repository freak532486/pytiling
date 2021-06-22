from os import close
from definitions import *
import time

class Layout:

    def __init__(self, windows, screen: Rect):
        self.windows = windows.copy()
        self.regions = self.calculate_regions(len(windows))
        self.regions = []
        self.screen = screen
        self.__grab_region = None
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
            window_rect = window.get_geometry()
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

    def add_windows(self, windows):
        new_windows = self.windows.copy()
        for window in windows:
            if window.id not in list(map(lambda window : window.id, self.windows)):
                new_windows.append(window)
        new_regions = self.calculate_regions(len(new_windows)) 
        self.regions = new_regions
        self.windows = new_windows
        self.assign_and_move()

    def remove_windows(self, windows):
        new_windows = self.windows.copy()
        for window in windows:
            for _window in self.windows:
                if _window.id ==  window.id:
                    new_windows.remove(_window)
        new_regions = self.calculate_regions(len(new_windows)) 
        self.regions = new_regions
        self.windows = new_windows
        self.assign_and_move() 

    # Override this for new layouts
    def calculate_regions(self):
        return [self.screen] * len(self.windows)

    def assign_and_move(self):
        new_windows = []
        for i in range(len(self.regions)):
            region = self.regions[i]
            t = time.time()
            win = self.__get_closest_window(region)
            t = time.time()
            win.move_resize(region)
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
        

    def calculate_regions(self, n):
        regions = [] 
        gaps = self.gaps
        master_ratio = self.master_ratio
        # Edge cases 
        if n == 0:
            regions = []
            return regions
        if n == 1:
            regions = [Rect(gaps, gaps, self.screen.width - 2 * gaps, self.screen.height - 2 * gaps)]
            return regions
        # Now that the divide by 0 is out of the way...
        master_width = self.screen.width * master_ratio - 1.5 * gaps
        slave_width = self.screen.width * (1 - master_ratio) - 1.5 * gaps
        master_height = self.screen.height - 2 * gaps
        slave_height = (self.screen.height - n * gaps) / (n - 1)
        regions.append(Rect(gaps, gaps, master_width, master_height))
        for i in range(n - 1):
            regions.append(Rect(2 * gaps + master_width, gaps + (slave_height + gaps) * i, slave_width, slave_height))
        return regions

class ColumnDivider(Layout):

    gaps = None

    def __init__(self, windows, screen: Rect, gaps = 0):
        self.gaps = gaps
        super().__init__(windows, screen)
        

    def calculate_regions(self, screen):
        n = len(self.windows)
        gaps = self.gaps
        height = self.screen.height - 2 * gaps
        width = (self.screen.width - (n + 1) * gaps) / n
        for i in range(n):
            self.regions.append(Rect(int(gaps + (width + gaps) * i), gaps, int(width), height))
