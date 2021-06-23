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

    def _dist(self, a, b):
        ax, ay = a
        bx, by = b
        return (ax - bx) * (ax - bx) + (ay - by) * (ay - by)

    def _get_closest_window(self, rect: Rect):
        center = rect.topleft()
        min_window = self.windows[0]
        min_dist = float("inf")
        for window in self.windows:
            window_rect = window.get_geometry()
            window_center = window_rect.topleft()
            if self._dist(center, window_center) < min_dist:
                min_window = window
                min_dist = self._dist(center, window_center)
        return min_window

    def _get_closest_region(self, window: Window):
        min_dist = float("inf")
        min_region = self.regions[0]
        for region in self.regions:
            dist = self._dist(region.topleft(), window.get_geometry().topleft())
            if dist < min_dist:
                min_dist = dist
                min_region = region
        return min_region

    def _get_corresponding_region(self, window):
        for i in range(len(self.windows)):
            if self.windows[i].id == window.id:
                return self.regions[i]
        return None

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
            win = self._get_closest_window(region)
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
        old_geom = self._get_corresponding_region(window)
        new_geom = window.get_geometry()
        dx, dy = (new_geom.x - old_geom.x, new_geom.y - old_geom.y)
        dw, dh = (new_geom.width - old_geom.width, new_geom.height - old_geom.height)
        if (dx == 0 and dy == 0) or (dx == -dw and dy == 0) or (dx == 0 and dy == -dh) or (dx == -dw and dy == -dh):
            self.on_resize(window, dx, dy, dw, dh)
            return
        closest_region = self._get_closest_region(window)
        if closest_region != self.__grab_region:
            corresponding_window_index = self.regions.index(closest_region)
            grabbed_window_index = self.windows.index(window)
            corresponding_window = self.windows[corresponding_window_index]
            corresponding_window.move_resize(self.__grab_region)
            self.__grab_region = closest_region
            self.windows[corresponding_window_index] = window
            self.windows[grabbed_window_index] = corresponding_window

    def has_window(self, window: Window):
        return window.id in list(map(lambda w : w.id, self.windows))

    # Override in own layout
    def on_resize(self, window: Window):
        return

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

    def on_resize(self, window: Window, dx: int, dy: int, dw: int, dh: int):
        is_master = self.regions.index(self._get_corresponding_region(window)) == 0
        if is_master:
            if dx != 0:
                return
            self.regions[0].width += dw
            for i in range(1, len(self.windows)):
                self.regions[i].width -= dw
                self.regions[i].x += dw
                self.windows[i].move_resize(self.regions[i])
        else:
            index = self.regions.index(self._get_corresponding_region(window))
            if dx != 0: # Width resize on left handle
                self.regions[0].width -= dw
                self.windows[0].move_resize(self.regions[0])
                for i in range(1, len(self.windows)):
                    window_to_adjust = self.windows[i]
                    region_to_adjust = self.regions[i]
                    region_to_adjust.x += dx
                    region_to_adjust.width += dw
                    if i != index:
                        window_to_adjust.move_resize(self.regions[i])
            if dh != 0:
                top_bar_grabbed = dy != 0
                if top_bar_grabbed:
                    index_to_adjust = index - 1 # Region above resized window
                    if index_to_adjust < 1:
                        return
                    self.regions[index].y += dy
                    self.regions[index].height += dh
                    self.regions[index_to_adjust].height -= dh
                    self.windows[index_to_adjust].move_resize(self.regions[index_to_adjust])
                else:
                    index_to_adjust = index + 1 # Region below resized window
                    if index_to_adjust >= len(self.regions):
                        return
                    self.regions[index].height += dh
                    self.regions[index_to_adjust].height -= dh
                    self.regions[index_to_adjust].y += dh
                    self.windows[index_to_adjust].move_resize(self.regions[index_to_adjust])