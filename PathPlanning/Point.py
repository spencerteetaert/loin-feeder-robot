import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Point (" + str(self.x) + ", " + str(self.y) + ")"

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)
    def __mul__(self, factor):
        return Point(self.x * factor, self.y * factor)
    def __truediv__(self, factor):
        return Point(self.x / factor, self.y / factor)
    def __floordiv__(self, factor):
        return Point(self.x // factor, self.y // factor)

    def mag(self):
        return (self.x**2 + self.y**2)**0.5
    def norm(self):
        return Point(self.x / self.mag(), self.y / self.mag())
    def angle(self):
        if self.x < 0:
            return (math.degrees(math.atan((-1*self.y)/self.x)) + 180 + 360) % 360
        elif self.x == 0:
            if self.y < 0:
                return 90
            else:
                return 270
        else:
            return (math.degrees(math.atan((-1*self.y)/self.x)) + 360) % 360

    def toTuple(self):
        return (round(self.x), round(self.y))