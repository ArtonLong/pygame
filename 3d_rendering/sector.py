
from settings import *

class Wall:
    def __init__(self, x1, x2, y1, y2, c):
        self.x1, self.x2 = x1, x2
        self.y1, self.y2= y1, y2
        self.c = c

class Sector:
    def __init__(self, z1, z2, ct, cb, walls: list[Wall]):
        self.z1, self.z2 = z1, z2
        self.ct, self.cb = ct, cb
        self.d = 0
        self.surf = [0] * WIDTH
        self.surface = 0

        self.walls = walls