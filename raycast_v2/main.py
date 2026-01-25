import pygame
from pygame.locals import *
import sys
import math

from settings import *

class Player:
    def __init__(self, x, y, z, a, l):
        self.x, self.y, self.z = x,y,z
        self.a = a
        self.l = l

    def move_player(self, cos, sin):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.a -= 2
        if keys[pygame.K_RIGHT]:
            self.a += 2
        self.a = self.rotation_clamp(self.a)

        dx = sin[self.a]*10
        dy = cos[self.a]*10

        if keys[pygame.K_d]:
            self.x += dy
            self.y -= dx
        if keys[pygame.K_a]:
            self.x -= dy
            self.y += dx
        if keys[pygame.K_w]:
            self.x += dx
            self.y += dy
        if keys[pygame.K_s]:
            self.x -= dx
            self.y -= dy
        if keys[pygame.K_UP]:
            self.l -= 1
        if keys[pygame.K_DOWN]:
            self.l += 1
        if keys[pygame.K_SPACE]:
            self.z += 4
        if keys[pygame.K_LCTRL]:
            self.z -= 4

    def rotation_clamp(self, a):
        if a < 0:
            a += 360
        elif a > 359:
            a -= 360
        return a

class App:
    def __init__(self):
        pygame.init()

        self._running = True
        self.DISPLAY_SURF = pygame.display.set_mode(SIZE)

        self.player = Player(70, -110, 20, 0, 0)

        self.cos = [0]*360
        self.sin = [0]*360

        for i in range(360):
            self.cos[i] = math.cos(i/180*math.pi)
            self.sin[i] = math.sin(i/180*math.pi)

    def draw_wall(self, x1, x2, b1, b2, t1, t2):
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

        x = x1
        while x<x2:
            y1 = dyb*(x-xs*0.5)/dx+b1
            y2 = dyt*(x-xs*0.5)/dx+t1
            y=y1
            while y<y2:

                if y1 < 1: y1 = 1
                if y2 < 1: y2 = 1
                if y1 > HEIGHT-1: y1 = HEIGHT-1
                if y2 > HEIGHT-1: y2 = HEIGHT-1

                self.draw_pixel(x,y,0)
                y+=1
            x+=1

    def draw_3d(self):
        wx = [0,0,0,0]
        wy = [0,0,0,0]
        wz = [0,0,0,0]
        cos, sin = self.cos[self.player.a], self.sin[self.player.a]

        #offsetting the position of the wall point 1 at 40, 10. by the player
        x1 = 40 - self.player.x
        y1 = 10 - self.player.y
        x2 = 40 - self.player.x
        y2 = 290 - self.player.y
        
        wx[0] = x1*cos-y1*sin
        wx[1] = x2*cos-y2*sin
        wx[2] = wx[0]
        wx[3] = wx[1]

        wy[0] = y1*cos+x1*sin
        wy[1] = y2*cos+x2*sin
        wy[2] = wy[0]
        wy[3] = wy[1]

        wz[0] = 0-self.player.z + ((self.player.l*wy[0])/32)
        wz[1] = 0-self.player.z + ((self.player.l*wy[1])/32)
        wz[2] = wz[0] + 40
        wz[3] = wz[1] + 40


        #screen pos
        wx[0] = wx[0]*200/wy[0]+W2
        wy[0] = wz[0]*200/wy[0]+H2
        wx[1] = wx[1]*200/wy[1]+W2
        wy[1] = wz[1]*200/wy[1]+H2
        wx[2] = wx[2]*200/wy[2]+W2
        wy[2] = wz[2]*200/wy[2]+H2
        wx[3] = wx[3]*200/wy[3]+W2
        wy[3] = wz[3]*200/wy[3]+H2

        # self.draw_pixel(wx[0], wy[0], 0)
        # self.draw_pixel(wx[1], wy[1], 0)

        self.draw_wall(wx[0], wx[1], wy[0], wy[1], wy[2], wy[3])

    def draw_pixel(self, x, y, c):
        if c == 0: color = (255,255,255)
        elif c == 1: color = (255,0,0)
        elif c == 2: color = (0,255,0)
        elif c == 3: color = (0,0,255)
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
            self.draw_pixel(0, 0, 1)

            self.fps_counter(clock)
            pygame.display.update()
            clock.tick(FPS)
 
if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()