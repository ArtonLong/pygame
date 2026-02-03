import pygame
from pygame.locals import *
import sys
import math
import time

from settings import *
from player import Player
from sector import Sector, Wall
from editor import Editor

class App:
    def __init__(self):
        pygame.init()

        self._running = True
        self.DISPLAY_SURF = pygame.display.set_mode(SIZE)
        self.is_edit = False
        self.tslp = 0

        self.player = Player(W2*PIXEL_SCALE, H2*PIXEL_SCALE, 20, 0, 0)
        self.editor = Editor(self.DISPLAY_SURF, self.player)

        self.sectors = []

        self.cos = []
        self.sin = []
        for i in range(360):
            self.cos.append(math.cos(i/180*math.pi))
            self.sin.append(math.sin(i/180*math.pi))

    def dist(self, x1, y1, x2, y2):
        return math.sqrt((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1))
    
    def game_scene(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_i] and self.menu_press_interval():
            self.is_edit = True   
        self.player.move_player(self.cos, self.sin)
        self.draw_3d()

    def clip_behind_player(self, x1, y1, z1, x2, y2, z2):
        d = y1 - y2
        if d == 0: d = 1
        s = y1 / d
        x1 = x1 + s * (x2 - x1)
        #y1 = y1 + s * (y2 - y1)
        #if y1 == 0: y1 = 1
        y1 = 1
        z1 = z1 + s * (z2 - z1)
        return x1, y1, z1

    def draw_wall(self, x1, x2, b1, b2, t1, t2, s: Sector, w: Wall, front_back):
        dyb = b2 - b1
        dyt = t2 - t1
        dx = x2 - x1
        if dx == 0:
            dx = 1
        xs = x1

        if x1 < 0: x1 = 0
        if x2 < 0: x2 = 0
        if x1 > WIDTH: x1 = WIDTH
        if x2 > WIDTH: x2 = WIDTH

        x1 = math.floor(x1)
        x2 = math.floor(x2)

        for x in range(x1, x2):
            y1 = math.floor(dyb*(x-xs+0.5)/dx+b1)
            y2 = math.floor(dyt*(x-xs+0.5)/dx+t1)
            
            if y1 < 0: y1 = 0
            if y2 < 0: y2 = 0
            if y1 > HEIGHT: y1 = HEIGHT
            if y2 > HEIGHT: y2 = HEIGHT

            if front_back == 0:
                if s.surface == 1: s.surf[x] = y1
                if s.surface == 2: s.surf[x] = y2
                for y in range(y1, y2):
                    self.draw_pixel(x,y,w.c)
            if front_back == 1:
                if s.surface == 1: y2 = s.surf[x]
                if s.surface == 2: y1 = s.surf[x]
                for y in range(y1, y2):
                    self.draw_pixel(x,y,(0,255,0))

    def draw_3d(self):
        wx = [0,0,0,0]
        wy = [0,0,0,0]
        wz = [0,0,0,0]
        cos, sin = self.cos[self.player.a], self.sin[self.player.a]
        #bubble sort sectors in order of draw distance
        n = len(self.sectors)
        for i in range(n):
            swapped = False
            for j in range(0, n-i-1):
                if self.sectors[j].d < self.sectors[j+1].d:
                    self.sectors[j], self.sectors[j+1] = self.sectors[j+1], self.sectors[j]
                    swapped = True
            if not swapped:
                break

        for s in self.sectors:
            s.d = 0
            if self.player.z < s.z1: 
                s.surface = 1
                cycles = 2
                for x in range(WIDTH):
                    s.surf[x] = HEIGHT
            elif self.player.z > s.z2: 
                s.surface = 2
                cycles = 2
                for x in range(WIDTH):
                    s.surf[x] = 0
            else: 
                s.surface = 0
                cycles = 1
            #draw both sides of the wall so the top and bottom of the sector can be drawn
            for front_back in range(cycles):
                for w in s.walls:
                
                    x1 = w.x1 - self.player.x
                    y1 = w.y1 - self.player.y
                    x2 = w.x2 - self.player.x
                    y2 = w.y2 - self.player.y

                    if front_back == 1:
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
                    wz[2] = s.z2-self.player.z + ((self.player.l*wy[0])/32)
                    wz[3] = s.z2-self.player.z + ((self.player.l*wy[1])/32)
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

                    self.draw_wall(wx[0], wx[1], wy[0], wy[1], wy[2], wy[3], s, w, front_back)
                    
                    # self.draw_pixel(wx[0], wy[0], (255,255,255))
                    # self.draw_pixel(wx[1], wy[1], (255,255,255))
                    # self.draw_pixel(wx[2], wy[2], (255,255,255))
                    # self.draw_pixel(wx[3], wy[3], (255,255,255))
                s.d /= len(s.walls)

    def draw_pixel(self, x, y, color:tuple):
        pygame.draw.rect(self.DISPLAY_SURF, color, ((x*PIXEL_SCALE, HEIGHT*PIXEL_SCALE - y*PIXEL_SCALE), (PIXEL_SCALE, PIXEL_SCALE)))

    def edit_scene(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_i] and self.menu_press_interval():
            self.is_edit = False 
        self.editor.button_handler()
        self.editor.draw()
        if self.editor.is_placing_sector:
            self.editor.placing_walls()
        self.editor.place_player()

        if self.editor.is_setting_height and self.editor.press_delay():
            num = self.editor.numpad()
            if type(num) == int:
                self.editor.height += str(num)
            elif num == "b":
                self.editor.height = self.editor.height[:-1]
            elif num == "e":
                self.editor.sectors[self.editor.selected_sector].z2 = int(self.editor.height)
                self.editor.is_setting_height = False

        if self.editor.is_setting_z and self.editor.press_delay():
            num = self.editor.numpad()
            if type(num) == int:
                self.editor.z += str(num)
            elif num == "b":
                self.editor.z = self.editor.z[:-1]
            elif num == "e":
                self.editor.sectors[self.editor.selected_sector].z1 = int(self.editor.z)
                self.editor.is_setting_z = False
    
    def menu_press_interval(self):
        current_time = time.time()
        if current_time - self.tslp > 0.5: 
            self.tslp = current_time
            return True
        return False

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

            self.sectors = self.editor.sectors
                
            if self.is_edit:
               self.DISPLAY_SURF.fill((0,50,0))
               self.edit_scene()
            else:
                self.DISPLAY_SURF.fill((0,0,0))
                self.game_scene() 

            self.fps_counter(clock)
            pygame.display.update()
            clock.tick(FPS)
 
if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()