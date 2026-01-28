import pygame
from pygame.locals import *
import sys
import math

from settings import *
from player import Player
from sector import Sector, Wall

class App:
    def __init__(self):
        pygame.init()

        self._running = True
        self.DISPLAY_SURF = pygame.display.set_mode(SIZE)

        self.player = Player(70, -110, 20, 0, 0)

        self.sectors = [Sector(0, 4, 0, 40, 3, 4), Sector(4, 8, 0, 40, 1, 2)]
        self.walls = [
            Wall(0,0,32,0,1), Wall(32,0,32,32,2), Wall(32,32,0,32,1), Wall(0,32,0,0,2),
            Wall(64,96,0,0,3), Wall(96,96,0,32,4), Wall(96,64,32,32,3), Wall(64,64,32,0,4)
            ]

        self.cos = [0]*360
        self.sin = [0]*360

        for i in range(360):
            self.cos[i] = math.cos(i/180*math.pi)
            self.sin[i] = math.sin(i/180*math.pi)

    def dist(self, x1, x2, y1, y2):
        return math.sqrt((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1))

    def clip_behind_player(self, x1, y1, z1, x2, y2, z2):
        d = y1 - y2
        if d == 0: d = 1
        s = y1 / d
        x1 = x1 + s * (x2 - x1)
        y1 = y1 + s * (y2 - y1)
        if y1 == 0: y1 = 1
        z1 = z1 + s * (z2 - z1)
        return x1, y1, z1

    def draw_wall(self, x1, x2, b1, b2, t1, t2, c, s: Sector):
        dyb = b2 - b1
        dyt = t2 - t1
        dx = x2 - x1
        if dx == 0:
            dx = 1
        xs = x1

        if x1 < 1: x1 = 1
        if x2 < 1: x2 = 1
        if x1 > WIDTH-1: x1 = WIDTH-1
        if x2 > WIDTH-1: x2 = WIDTH-1

        x = math.floor(x1)-1

        while x<x2:
            x+=1
            y1 = dyb*(x-xs+0.5)/dx+b1
            y2 = dyt*(x-xs+0.5)/dx+t1
            
            if s.surface == 1: 
                
                s.surf[x] = y1
                continue
            if s.surface == 2: 
                s.surf[x] = y2
                continue
            if s.surface == -1:
                y=s.surf[x]
                while y<y1:
                    self.draw_pixel(x,y,s.cb)
                    y+=1
            if s.surface == -2:
                y=y2
                while y<s.surf[x]:
                    self.draw_pixel(x,y,s.ct)
                    y+=1
            y=y1
            while y<y2:
                if y1 < 1: y1 = 1
                if y2 < 1: y2 = 1
                if y1 > HEIGHT-1: y1 = HEIGHT-1
                if y2 > HEIGHT-1: y2 = HEIGHT-1

                self.draw_pixel(x,y,c)
                y+=1

    def draw_3d(self):
        wx = [0,0,0,0]
        wy = [0,0,0,0]
        wz = [0,0,0,0]
        cos, sin = self.cos[self.player.a], self.sin[self.player.a]

        for s in range(len(self.sectors)-1):
            for w in range(len(self.sectors)-s-1):
                if self.sectors[w].d < self.sectors[w+1].d:
                    st = self.sectors[w]
                    self.sectors[w] = self.sectors[w+1]
                    self.sectors[w+1] = st

        #offsetting the position of the wall point 1 at 40, 10. by the player
        for s in self.sectors:
            s.d = 0

            if self.player.z < s.z1: s.surface = 1
            elif self.player.z > s.z2: s.surface = 2
            else: s.surface = 0

            for loop in range(2):

                for i in range(s.ws, s.we):
                    w = self.walls[i]
                
                    x1 = w.x1 - self.player.x
                    y1 = w.y1 - self.player.y
                    x2 = w.x2 - self.player.x
                    y2 = w.y2 - self.player.y

                    if loop == 0:
                        swp = x1
                        x1 = x2
                        x2 = swp
                        swp = y1
                        y1 = y2
                        y2 = swp
                    
                    wx[0] = x1*cos-y1*sin
                    wx[1] = x2*cos-y2*sin
                    wx[2] = wx[0]
                    wx[3] = wx[1]

                    wy[0] = y1*cos+x1*sin
                    wy[1] = y2*cos+x2*sin
                    wy[2] = wy[0]
                    wy[3] = wy[1]

                    s.d += self.dist(0, 0, (wx[0]+wx[1])/2, (wy[0]+wy[1])/2)

                    wz[0] = s.z1-self.player.z + ((self.player.l*wy[0])/32)
                    wz[1] = s.z1-self.player.z + ((self.player.l*wy[1])/32)
                    wz[2] = wz[0] + s.z2
                    wz[3] = wz[1] + s.z2
                    if wy[0] < 1 and wy[1] < 1: continue

                    if wy[0] < 1:
                        wx[0], wy[0], wz[0] = self.clip_behind_player(wx[0], wy[0], wz[0], wx[1], wy[1], wz[1],)
                        wx[2], wy[2], wz[2] = self.clip_behind_player(wx[2], wy[2], wz[2], wx[3], wy[3], wz[3],)
                    
                    if wy[1] < 1:
                        wx[1], wy[1], wz[1] = self.clip_behind_player(wx[1], wy[1], wz[1], wx[0], wy[0], wz[0],)
                        wx[3], wy[3], wz[3] = self.clip_behind_player(wx[3], wy[3], wz[3], wx[2], wy[2], wz[2],)

                    #screen pos
                    wx[0] = wx[0]*200/wy[0]+W2
                    wy[0] = wz[0]*200/wy[0]+H2
                    wx[1] = wx[1]*200/wy[1]+W2
                    wy[1] = wz[1]*200/wy[1]+H2
                    wx[2] = wx[2]*200/wy[2]+W2
                    wy[2] = wz[2]*200/wy[2]+H2
                    wx[3] = wx[3]*200/wy[3]+W2
                    wy[3] = wz[3]*200/wy[3]+H2

                    # self.draw_pixel(wx[0], wy[0], w.c)
                    # self.draw_pixel(wx[1], wy[1], w.c)
                    # self.draw_pixel(wx[2], wy[2], w.c)
                    # self.draw_pixel(wx[3], wy[3], w.c)

                    self.draw_wall(wx[0], wx[1], wy[0], wy[1], wy[2], wy[3], w.c, s)
                s.d /= (s.we-s.ws)
                s.surface *= -1

    def draw_pixel(self, x, y, c):
        if c == 0: color = (255,255,255)
        elif c == 1: color = (255,0,0)
        elif c == 2: color = (0,255,0)
        elif c == 3: color = (0,0,255)
        elif c == 4: color = (100,0,155)
        else: color = (50,50,50)

        pygame.draw.rect(self.DISPLAY_SURF, color, ((x*PIXEL_SCALE, HEIGHT*PIXEL_SCALE - y*PIXEL_SCALE), (PIXEL_SCALE, PIXEL_SCALE)))

    def on_quit(self):
        pygame.quit()
        sys.exit()

    def font(self, text):
        font = pygame.font.SysFont("Arial" , 18 , bold = True)
        return font.render(text , 1, pygame.Color("RED"))

    def fps_counter(self, clock):
        fps = str(int(clock.get_fps()))
        fps_t = self.font(fps)
        self.DISPLAY_SURF.blit(fps_t,(0,0))
 
    def on_execute(self):
        clock = pygame.time.Clock()

        while( self._running ):
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.on_quit()
            self.DISPLAY_SURF.fill((0,0,0))

            self.player.move_player(self.cos, self.sin)
            self.draw_3d()
            #self.draw_pixel(W2, H2, 1)

            self.fps_counter(clock)
            pygame.display.update()
            clock.tick(FPS)
 
if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()