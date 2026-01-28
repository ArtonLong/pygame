import pygame
from pygame.locals import *
import math

from settings import *
from sector import Sector, Wall

class Editor:
    def __init__(self, surface, player):
        self.DISPLAY_SURF = surface
        self.player = player
        #self.mouse_pos = 0
        self.sectors = []
        self.walls = []
        self.menu_width = 64
        self.grid_scale = 32

        self.start_sector_point = None
        self.start_wall_point = [0,0]
        self.end_wall_point = [0,0]
        self.is_placing_sector = False

        self.new_sector_btn = Button(self.menu_width, 25, SIZE[0]-self.menu_width, 0, "new sector")

    def place_player(self):
        pygame.draw.circle(self.DISPLAY_SURF, (255, 0, 0), (self.player.x+PIXEL_SCALE*W2, self.player.y+PIXEL_SCALE*H2), PIXEL_SCALE*3)

    def draw(self):
        color = (0,0,0)
        #self.mouse_pos = pygame.mouse.get_pos()

        vert_lines = int(SIZE[0]//4)
        for v in range(vert_lines):
            pygame.draw.line(self.DISPLAY_SURF, color, (v*self.grid_scale, SIZE[1]), (v*self.grid_scale, 0), PIXEL_SCALE)
        hor_lines = int(SIZE[1]//4)
        for h in range(hor_lines):
            pygame.draw.line(self.DISPLAY_SURF, color, (SIZE[0], h*self.grid_scale), (0, h*self.grid_scale), PIXEL_SCALE)

        pygame.draw.rect(self.DISPLAY_SURF, (100, 100, 100), ((SIZE[0]-self.menu_width, 0),(self.menu_width, SIZE[1])))

        self.new_sector_btn.draw(self.DISPLAY_SURF)
        if self.new_sector_btn.button_click() and not self.is_placing_sector:
            self.place_sector()
            self.is_placing_sector = True

        if self.is_placing_sector:
            self.placing_walls()

    def place_sector(self):
        new_sector = Sector(0,0,0,0,1,2)
    
    def placing_walls(self):
        mouse_pos = pygame.mouse.get_pos()
        self.draw_pixel(mouse_pos[0], mouse_pos[1], 0)

    def draw_pixel(self, x, y, c):
        if c == 0: color = (255,255,255)
        elif c == 1: color = (255,0,0)
        elif c == 2: color = (0,255,0)
        elif c == 3: color = (0,0,255)
        elif c == 4: color = (100,0,155)
        else: color = (50,50,50)

        pygame.draw.rect(self.DISPLAY_SURF, color, ((x*PIXEL_SCALE, y*PIXEL_SCALE), (PIXEL_SCALE, PIXEL_SCALE)))

    def drawLine(self, x1,y1,x2,y2, r,g,b):
        x = x2-x1
        y = y2-y1
        max = math.fabs(x)
        if math.fabs(y)>max: max=math.fabs(y)
        x /= max
        y /= max
        for i in range(max):
            self.draw_pixel(x1,y1,r,g,b)
            x1+=x
            y1+=y

class Button:
    def __init__(self, width, height, x, y, text):
        self.width, self.height = width, height
        self.x, self.y = x, y
        self.text = self.font(text)

        self.rect = pygame.Rect(x, y, width, height)

    def button_click(self):
        pressed = pygame.mouse.get_pressed()
        if pressed[0]:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                return True
        return False

    def font(self, text):
        font = pygame.font.SysFont("Arial" , 10, bold = True)
        return font.render(text , 1, (0,0,0))

    def draw(self, surface):
        pygame.draw.rect(surface, (200,200,200), self.rect)
        surface.blit(self.text, (self.x, self.y))