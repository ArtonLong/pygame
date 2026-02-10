import pygame
from pygame.locals import *
import sys
import math
import time

from settings import *
from player import Player
from sector import Sector, Wall
from editor import Editor
from textures import *

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
        #self.floors()
        #self.test_texture(M_GRASS)
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

        wt = TEXTURES[w.wt_index]
        ht = 0
        ht_step = wt.width*w.u/dx

        if x1 < 0:
            ht -= ht_step*x1 
            x1 = 0
        if x2 < 0: x2 = 0
        if x1 > WIDTH: x1 = WIDTH
        if x2 > WIDTH: x2 = WIDTH

        for x in range(math.floor(x1), math.floor(x2)):
            y1 = dyb*(x-xs+0.5)/dx+b1
            y2 = dyt*(x-xs+0.5)/dx+t1

            vt = 0
            vt_step = wt.height*w.v/(y2-y1)
            
            if y1 < 0: 
                vt -= vt_step*y1
                y1 = 0
            if y2 < 0: y2 = 0
            if y1 > HEIGHT: y1 = HEIGHT
            if y2 > HEIGHT: y2 = HEIGHT    

            if front_back == 0:
                if s.surface == 1: s.surf[x] = y1
                if s.surface == 2: s.surf[x] = y2
                for y in range(math.floor(y1), math.floor(y2)):
                    pixel = (math.floor(wt.height-(vt%wt.height))*3*wt.width + math.floor(ht%wt.width)*3)
                    if pixel >= len(wt.texture):
                        vt += vt_step
                        continue
                    r = wt.texture[pixel]
                    g = wt.texture[pixel+1]
                    b = wt.texture[pixel+2]
                    self.draw_pixel(x,y,(r,g,b))
                    vt += vt_step
                ht += ht_step

            if front_back == 1:
                #for y in range(math.floor(y1), math.floor(y2)):
                wo = 0
                x2 = x-W2
                tile = s.ss*7

                if s.surface == 1: 
                    y2 = s.surf[x]
                    wo = s.z1
                if s.surface == 2: 
                    y1 = s.surf[x]
                    wo = s.z2

                look_up_down = -self.player.l*6.1
                if look_up_down>HEIGHT: look_up_down=HEIGHT
                move_up_down = (self.player.z-wo)/H2
                if move_up_down == 0: move_up_down = 0.001
                
                ys = y1-H2
                ye = y2-H2

                for y in range(math.floor(ys), math.floor(ye)):
                    z = y+look_up_down
                    if z == 0: z = 0.0001
                    fx = x2/z*move_up_down*tile
                    fy = FOV/z*move_up_down*tile
                    rx = fx*self.sin[self.player.a]-fy*self.cos[self.player.a]+(self.player.y/60*tile)
                    ry = fx*self.cos[self.player.a]+fy*self.sin[self.player.a]-(self.player.x/60*tile)

                    if rx < 0: rx = -rx+1
                    if ry < 0: ry = -ry+1
                    
                    st:Texture = SURFACE_TEXTURES[s.st]

                    pixel = abs(math.floor(st.height-(ry%st.height)-1)*3*st.width + math.floor(rx%st.width)*3)
                    r = st.texture[pixel]
                    g = st.texture[pixel+1]
                    b = st.texture[pixel+2]
                    self.draw_pixel(x2+W2,y+H2,(r,g,b))

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
                    wx[0] = wx[0]*FOV/wy[0]+W2
                    wy[0] = wz[0]*FOV/wy[0]+H2
                    wx[1] = wx[1]*FOV/wy[1]+W2
                    wy[1] = wz[1]*FOV/wy[1]+H2
                    wx[2] = wx[2]*FOV/wy[2]+W2
                    wy[2] = wz[2]*FOV/wy[2]+H2
                    wx[3] = wx[3]*FOV/wy[3]+W2
                    wy[3] = wz[3]*FOV/wy[3]+H2

                    self.draw_wall(wx[0], wx[1], wy[0], wy[1], wy[2], wy[3], s, w, front_back)
                    
                    # self.draw_pixel(wx[0], wy[0], (255,255,255))
                    # self.draw_pixel(wx[1], wy[1], (255,255,255))
                    # self.draw_pixel(wx[2], wy[2], (255,255,255))
                    # self.draw_pixel(wx[3], wy[3], (255,255,255))
                s.d /= len(s.walls)

    def floors(self):

        look_up_down = -self.player.l*4
        if look_up_down>HEIGHT: look_up_down=HEIGHT
        move_up_down = self.player.z/16
        if move_up_down == 0: move_up_down = 0.001

        ys = -H2
        ye = -look_up_down

        if move_up_down < 0: 
            ys = -look_up_down
            ye = H2+look_up_down

        for y in range(ys, ye):
            for x in range(-W2, W2):
                z = y+look_up_down
                if z == 0: z = 0.0001
                fx = x/z*move_up_down
                fy = FOV/z*move_up_down
                rx = fx*self.sin[self.player.a]-fy*self.cos[self.player.a]+(self.player.y/30)
                ry = fx*self.cos[self.player.a]+fy*self.sin[self.player.a]-(self.player.x/30)

                if rx < 0: rx = -rx+1
                if ry < 0: ry = -ry+1
                if rx<=0 or ry<=0 or rx >= 5 or ry >= 5: continue
                if int(rx%2) == int(ry%2): self.draw_pixel(x+W2, y+H2, (255,0,0))
                else: self.draw_pixel(x+W2, y+H2, (0,255,0))

    def draw_pixel(self, x, y, color:tuple):
        pygame.draw.rect(self.DISPLAY_SURF, color, ((x*PIXEL_SCALE, HEIGHT*PIXEL_SCALE - y*PIXEL_SCALE), (PIXEL_SCALE, PIXEL_SCALE)))

    def test_texture(self, texture: Texture):
        for y in range(texture.height):
            for x in range(texture.width):
                pixel = (texture.height-y-1)*3*texture.width + x*3
                r = texture.texture[pixel]
                g = texture.texture[pixel+1]
                b = texture.texture[pixel+2]
                self.draw_pixel(x,y,(r,g,b))

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
                s = self.editor.sectors[self.editor.selected_sector]
                self.editor.texture_v(s)
                s.z2 = int(self.editor.height)
                self.editor.is_setting_height = False

        if self.editor.is_setting_z and self.editor.press_delay():
            num = self.editor.numpad()
            if type(num) == int:
                self.editor.z += str(num)
            elif num == "b":
                self.editor.z = self.editor.z[:-1]
            elif num == "e":
                s = self.editor.sectors[self.editor.selected_sector]
                self.editor.texture_v(s)
                s.z1 = int(self.editor.z)
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