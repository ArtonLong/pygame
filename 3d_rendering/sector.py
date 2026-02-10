
from settings import *

class Wall:
    def __init__(self, x1, x2, y1, y2, c, wt_index, u, v):
        self.x1, self.x2 = x1, x2
        self.y1, self.y2= y1, y2
        self.u, self.v = u, v
        self.wt_index = wt_index
        self.c = c

class Sector:
    def __init__(self, z1, z2, ss, st, walls: list[Wall], d=0, surf=[0]*WIDTH, surface=0):
        self.z1, self.z2 = z1, z2
        self.d = d
        self.surf = surf
        self.surface = surface
        self.ss = ss
        self.st = st

        self.walls = walls