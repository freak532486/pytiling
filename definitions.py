class Window:
    def __init__(self, window, id):
        self.window = window
        self.id = id

class Rect:
    def __init__(self, x, y, width, height):
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)

    def center(self):
        return (self.x + self.width / 2, self.y + self.height / 2)

    def __repr__(self):
        return f"(x: {self.x}, y: {self.y}, width: {self.width}, height: {self.height})"