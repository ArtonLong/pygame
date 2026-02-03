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
        self.selected_color = 0
        self.sector_height = "0"
        self.sector_z = "0"
        self.color = (255,0,0)
        self.grid_scale = 32

        self.start_sector_point = None
        self.start_wall_point = None
        self.is_placing_sector = False

        self.new_sector_btn = Button(self.menu_width, 25, SIZE[0]-self.menu_width, 0, "new sector")
        self.delete_btn = Button(self.menu_width, 25, SIZE[0]-self.menu_width, 25, "Delete")
        self.load_btn = Button(self.menu_width, 25, SIZE[0]-self.menu_width, SIZE[1]-50, "Load")
        self.save_btn = Button(self.menu_width, 25, SIZE[0]-self.menu_width, SIZE[1]-25, "Save")
        self.sector_btn = Button(self.menu_width, 25, SIZE[0]-self.menu_width, 50, "sector:")
        self.wall_btn = Button(self.menu_width, 25, SIZE[0]-self.menu_width, 75, "wall: 0")
        self.color_btn = Button(self.menu_width, 25, SIZE[0]-self.menu_width, 100, "color")
        self.height_btn = Button(self.menu_width, 25, SIZE[0]-self.menu_width, 150, "height: ")
        self.z_location_btn = Button(self.menu_width, 25, SIZE[0]-self.menu_width, 175, "z: ")

        self.is_setting_height = False
        self.height = ""
        self.is_setting_z = False
        self.z = ""

    def handle_click(self):
        current_time = time.time()
        
        if pygame.mouse.get_pressed()[0] and current_time - self.tslc > 0.25:
            self.tslc = current_time
            return True
        return False
    
    def press_delay(self):
        current_time = time.time()
        
        if current_time - self.tslc > 0.15:
            self.tslc = current_time
            return True
        return False

    def place_player(self):
        pygame.draw.circle(self.DISPLAY_SURF, (255, 0, 0), (self.player.x, self.player.y), PIXEL_SCALE*2)

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
        self.delete_btn.draw(self.DISPLAY_SURF)
        self.load_btn.draw(self.DISPLAY_SURF)
        self.save_btn.draw(self.DISPLAY_SURF)
        self.sector_btn.draw(self.DISPLAY_SURF)
        self.wall_btn.draw(self.DISPLAY_SURF)
        self.color_btn.draw(self.DISPLAY_SURF)
        self.height_btn.draw(self.DISPLAY_SURF)
        self.z_location_btn.draw(self.DISPLAY_SURF)

        self.sector_btn.text = f"sector: {self.selected_sector}"
        self.wall_btn.text = f"wall: {self.selected_wall}"
        self.height_btn.text = f"height: {self.height}"
        self.z_location_btn.text = f"z: {self.z}"
        pygame.draw.rect(self.DISPLAY_SURF, self.color, ((self.color_btn.x+(self.color_btn.width-25), self.color_btn.y),(25,25)))

        for i, s in enumerate(self.sectors):
            for j, w in enumerate(s.walls):
                if i == self.selected_sector:
                    if j == self.selected_wall:
                        pygame.draw.circle(self.DISPLAY_SURF, (255,255,255), (w.x1, w.y1), PIXEL_SCALE)
                        pygame.draw.circle(self.DISPLAY_SURF, (255,255,255), (w.x2, w.y2), PIXEL_SCALE)
                self.draw_line(w.x1, w.y1, w.x2, w.y2, w.c)

    def button_handler(self):
        if self.new_sector_btn.button_click() and not self.is_placing_sector:
            self.tslc = time.time() + 0.5
            self.place_sector()
            self.is_placing_sector = True

        if self.delete_btn.button_click() and not self.is_placing_sector:
            self.sectors.pop(self.selected_sector)
            self.selected_sector = 0

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
        
        if self.sector_btn.button_click() and not self.is_placing_sector:
            self.selected_sector += 1
            if self.selected_sector > len(self.sectors)-1:
                self.selected_sector = 0
            self.height = str(self.sectors[self.selected_sector].z2)
            self.z = str(self.sectors[self.selected_sector].z1)

        if self.wall_btn.button_click() and not self.is_placing_sector:
            self.selected_wall += 1
            if self.selected_wall > len(self.sectors[self.selected_sector].walls)-1:
                self.selected_wall = 0

        if self.color_btn.button_click() and not self.is_placing_sector:
            self.selected_color += 1
            if self.selected_color > 3:
                self.selected_color = 0
    
            if self.selected_color == 0:
                self.color = (255,0,0)
            if self.selected_color == 1:
                self.color = (0,255,0)
            if self.selected_color == 2:
                self.color = (0,0,255)
            if self.selected_color == 3:
                self.color = (155,0,100)

            self.sectors[self.selected_sector].walls[self.selected_wall].c = self.color
        
        if self.height_btn.button_click() and not self.is_placing_sector:
            self.is_setting_height = True

        if self.z_location_btn.button_click() and not self.is_placing_sector:
            self.is_setting_z = True
    
    def numpad(self):
        keys = pygame.key.get_pressed()

        for i, k in enumerate(keys):
            if k:
                if i == 42:
                    return "b"
                elif i == 40:
                    return "e"
                num = (i + 1) % 10
                return num
        return None
        
    def dict_to_sectors(self, d:dict):
        s = Sector(**d)
        for i, w in enumerate(s.walls):
            s.walls[i] = Wall(**w)
        return s
            
    def sector_to_dict(self, s:Sector):
        s_dict = {}
        temp = []
        for key, value in s.__dict__.items():
            s_dict[key] = value
        for w in s_dict["walls"]:
            temp.append(w.__dict__)
        s_dict["walls"] = temp
        return s_dict

    def place_sector(self):
        new_sector = Sector(0,40,1,2, [])
        self.sectors.append(new_sector)
        index = len(self.sectors) - 1
        self.selected_sector = index
        self.sector_btn.text = f"sector: {index}"
    
    def placing_walls(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_x = round(mouse_pos[0]/self.grid_scale)*self.grid_scale
        mouse_y = round(mouse_pos[1]/self.grid_scale)*self.grid_scale

        self.draw_pixel(mouse_x, mouse_y, (255,255,255))
        if self.start_wall_point != None:
            self.draw_line(self.start_wall_point[0], self.start_wall_point[1], mouse_x, mouse_y, (255,255,255))

        if self.handle_click():
            if self.start_sector_point == None:
                self.start_wall_point = (mouse_x, mouse_y)
                self.start_sector_point = (mouse_x, mouse_y)
                return
            
            new_wall = Wall(self.start_wall_point[0], mouse_x, self.start_wall_point[1], mouse_y, self.color)

            if self.start_sector_point == (mouse_x, mouse_y) and len(self.sectors[-1].walls) >= 2:
                self.start_sector_point = None
                self.start_wall_point = None
                self.is_placing_sector = False
            elif self.start_sector_point == (mouse_x, mouse_y):
                return
            else:
                self.start_wall_point = (mouse_x, mouse_y)

            self.sectors[-1].walls.append(new_wall)


    def draw_pixel(self, x, y, color:tuple):
        pygame.draw.rect(self.DISPLAY_SURF, color, ((x, y), (PIXEL_SCALE, PIXEL_SCALE)))

    def draw_line(self, x1,y1,x2,y2, color:tuple):
        x = x2-x1
        y = y2-y1
        max = math.fabs(x)
        if math.fabs(y)>max: max=math.fabs(y)
        if x == 0 and y == 0: return
        x /= max
        y /= max
        for i in range(int(max)):
            self.draw_pixel(x1,y1,color)
            x1+=x
            y1+=y

class Button:
    def __init__(self, width, height, x, y, text):
        self.width, self.height = width, height
        self.x, self.y = x, y
        self.text = text

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
        f_text = self.font(self.text)
        pygame.draw.rect(surface, (200,200,200), self.rect)
        surface.blit(f_text, (self.x, self.y))