
class Wall:
    def __init__(self, x1, x2, y1, y2, c):
        self.x1, self.x2 = x1, x2
        self.y1, self.y2= y1, y2
        self.c = c

class Sector:
    def __init__(self, ws, we, z1, z2):
        self.ws, self.we = ws, we
        self.z1, self.z2 = z1, z2
        self.d = 0