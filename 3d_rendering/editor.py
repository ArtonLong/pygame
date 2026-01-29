import pygame
from pygame.locals import *
import math
import time
import json

from settings import *
from sector import Sector, Wall

class Editor:
    def __init__(self, surface, player):
        self.DISPLAY_SURF = surface
        self.player = player
        self.tslc = 0

        self.sectors:list[Sector] = []  

        self.menu_width = 64
        self.selected_sector = 0
        self.selected_wall = 0
        self.grid_scale = 32

        self.start_sector_point = None
        self.start_wall_point = None
        self.is_placing_sector = False

        self.new_sector_btn = Button(self.menu_width, 25, SIZE[0]-self.menu_width, 0, "new sector")
        self.load_btn = Button(self.menu_width, 25, SIZE[0]-self.menu_width, SIZE[1]-50, "Load")
        self.save_btn = Button(self.menu_width, 25, SIZE[0]-self.menu_width, SIZE[1]-25, "Save")

    def handle_click(self):
        current_time = time.time()
        
        if pygame.mouse.get_pressed()[0] and current_time - self.tslc > 0.5:
            self.tslc = current_time
            return True
        return False

    def place_player(self):
        pygame.draw.circle(self.DISPLAY_SURF, (255, 0, 0), (self.player.x, self.player.y), PIXEL_SCALE*3)

    def draw(self):
        color = (0,0,0)

        vert_lines = int(SIZE[0]//4)
        for v in range(vert_lines):
            pygame.draw.line(self.DISPLAY_SURF, color, (v*self.grid_scale, SIZE[1]), (v*self.grid_scale, 0), PIXEL_SCALE)
        hor_lines = int(SIZE[1]//4)
        for h in range(hor_lines):
            pygame.draw.line(self.DISPLAY_SURF, color, (SIZE[0], h*self.grid_scale), (0, h*self.grid_scale), PIXEL_SCALE)

        pygame.draw.rect(self.DISPLAY_SURF, (100, 100, 100), ((SIZE[0]-self.menu_width, 0),(self.menu_width, SIZE[1])))

        self.new_sector_btn.draw(self.DISPLAY_SURF)
        self.save_btn.draw(self.DISPLAY_SURF)

        for s in self.sectors:
            for w in s.walls:
                self.draw_line(w.x1, w.y1, w.x2, w.y2, 0,0,0)

    def button_handler(self):
        if self.new_sector_btn.button_click() and not self.is_placing_sector:
            self.tslc = time.time() + 0.5
            self.place_sector()
            self.is_placing_sector = True

        if self.save_btn.button_click():
            temp = []
            for s in self.sectors:
                temp.append(self.sector_to_dict(s))
            data = {"sectors": temp}
            with open(MAP_LOAD, "w") as json_file:
                json.dump(data, json_file, indent=4)

        if self.load_btn.button_click():
            with open(MAP_LOAD, "r") as json_file:
                data = json.load(json_file)
            for s in data["sectors"]:
                self.sectors.append(self.dict_to_sectors(s))

    def dict_to_sectors(self, d:dict):
        s = Sector(**d)
        for i, w in enumerate(s.walls):
            s.walls[i] = Wall(**w)
        return s
            
    def sector_to_dict(self, s:Sector):
        s_dict = s.__dict__
        for i, w in enumerate(s_dict["walls"]):
            s_dict["walls"][i] = w.__dict__
        return s_dict

    def place_sector(self):
        new_sector = Sector(0,40,1,2, [])
        self.sectors.append(new_sector)
    
    def placing_walls(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_x = round(mouse_pos[0]/self.grid_scale)*self.grid_scale
        mouse_y = round(mouse_pos[1]/self.grid_scale)*self.grid_scale

        self.draw_pixel(mouse_x, mouse_y, 0)
        if self.start_wall_point != None:
            self.draw_line(self.start_wall_point[0], self.start_wall_point[1], mouse_x, mouse_y, 0,0,0)

        if self.handle_click():
            if self.start_sector_point == None:
                self.start_wall_point = (mouse_x, mouse_y)
                self.start_sector_point = (mouse_x, mouse_y)
                return
            
            new_wall = Wall(self.start_wall_point[0], mouse_x, self.start_wall_point[1], mouse_y, 1)

            if self.start_sector_point == (mouse_x, mouse_y) and len(self.sectors[-1].walls) >= 2:
                self.start_sector_point = None
                self.start_wall_point = None
                self.is_placing_sector = False
            elif self.start_sector_point == (mouse_x, mouse_y):
                return
            else:
                self.start_wall_point = (mouse_x, mouse_y)

            self.sectors[-1].walls.append(new_wall)


    def draw_pixel(self, x, y, c):
        if c == 0: color = (255,255,255)
        elif c == 1: color = (255,0,0)
        elif c == 2: color = (0,255,0)
        elif c == 3: color = (0,0,255)
        elif c == 4: color = (100,0,155)
        else: color = (50,50,50)

        pygame.draw.rect(self.DISPLAY_SURF, color, ((x, y), (PIXEL_SCALE, PIXEL_SCALE)))

    def draw_line(self, x1,y1,x2,y2, r,g,b):
        x = x2-x1
        y = y2-y1
        max = math.fabs(x)
        if math.fabs(y)>max: max=math.fabs(y)
        if x == 0 and y == 0: return
        x /= max
        y /= max
        for i in range(int(max)):
            self.draw_pixel(x1,y1,0)
            x1+=x
            y1+=y

class Button:
    def __init__(self, width, height, x, y, text):
        self.width, self.height = width, height
        self.x, self.y = x, y
        self.text = self.font(text)

        self.tslc = 0
        self.rect = pygame.Rect(x, y, width, height)

    def handle_click(self):
        current_time = time.time()
        
        if pygame.mouse.get_pressed()[0] and current_time - self.tslc > 1:
            self.tslc = current_time
            return True
        return False

    def button_click(self):
        if self.handle_click():
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                return True
        return False

    def font(self, text):
        font = pygame.font.SysFont("Arial" , 10, bold = True)
        return font.render(text , 1, (0,0,0))

    def draw(self, surface):
        pygame.draw.rect(surface, (200,200,200), self.rect)
        surface.blit(self.text, (self.x, self.y))