from definitions import *

class MasterSlaveDivider:

    def divide(self, rect: Rect, n, gaps = 0, master_ratio = 0.5):
        if n == 1:
            return [Rect(gaps, gaps, rect.width - 2 * gaps, rect.height - 2 * gaps)]
        # Now that the divide by 0 is out of the way...
        ret = []
        master_width = rect.width * master_ratio - 1.5 * gaps
        slave_width = rect.width * (1 - master_ratio) - 1.5 * gaps
        master_height = rect.height - 2 * gaps
        slave_height = (rect.height - n * gaps) / (n - 1)

        ret.append(Rect(gaps, gaps, master_width, master_height))
        for i in range(n - 1):
            ret.append(Rect(2 * gaps + master_width, gaps + (slave_height + gaps) * i, slave_width, slave_height))
        return ret

class ColumnDivider:

    def divide(self, rect: Rect, n, gaps = 0):
        ret = []
        height = rect.height - 2 * gaps
        width = (rect.width - (n + 1) * gaps) / n
        current_x = gaps
        for i in range(n):
            ret.append(Rect(int(current_x), gaps, int(width), height))
            current_x += width + gaps
        return ret
